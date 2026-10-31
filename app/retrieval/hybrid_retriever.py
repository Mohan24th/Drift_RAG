"""BM25 and pgvector retrieval combined with reciprocal rank fusion."""

import logging
import re
import time

from rank_bm25 import BM25Okapi
from sqlalchemy import select

from app.database.models import ChunkModel, DocumentModel, DocumentVersionModel
from app.retrieval.pg_retriever import PgRetriever

logger = logging.getLogger(__name__)
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.casefold())


class HybridRetriever:
    """Retrieve candidates with BM25 and vector search, then fuse by RRF."""

    def __init__(self, retriever: PgRetriever, rrf_k: int = 60):
        if rrf_k < 1:
            raise ValueError("rrf_k must be at least 1.")
        self.retriever = retriever
        self.session = retriever.session
        self.rrf_k = rrf_k

    def _retrieve_bm25(self, query: str, top_k: int, version_id: str | None,
                       document_id: str | None):
        statement = (
            select(
                ChunkModel.id,
                ChunkModel.text,
                ChunkModel.chunk_index,
                DocumentVersionModel.id,
                DocumentVersionModel.version_number,
                DocumentModel.id,
                DocumentModel.name,
            )
            .join(DocumentVersionModel, ChunkModel.version_id == DocumentVersionModel.id)
            .join(DocumentModel, DocumentVersionModel.document_id == DocumentModel.id)
        )
        if version_id is not None:
            statement = statement.where(
                DocumentVersionModel.id == version_id,
                DocumentVersionModel.status == "APPROVED",
            )
        else:
            statement = statement.where(DocumentVersionModel.status == "APPROVED")
        if document_id is not None:
            statement = statement.where(DocumentModel.id == document_id)

        rows = self.session.execute(statement).all()
        query_tokens = tokenize(query)
        if not rows or not query_tokens:
            return []

        corpus = [tokenize(row[1]) for row in rows]
        if not any(corpus):
            return []
        scores = BM25Okapi(corpus).get_scores(query_tokens)
        ranked = sorted(
            enumerate(rows), key=lambda pair: (-float(scores[pair[0]]), str(pair[1][0]))
        )

        results = []
        for index, row in ranked:
            if not corpus[index]:
                continue
            chunk, version, document = _proxies(row)
            results.append((chunk, version, document, float(scores[index])))
            if len(results) == top_k:
                break
        return results

    def retrieve(self, query: str, top_k: int = 3, version_id: str | None = None,
                 min_score: float | None = None, document_id: str | None = None):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        query = query.strip()
        start = time.perf_counter()
        vector = self.retriever.retrieve(
            query=query, top_k=top_k, version_id=version_id,
            min_score=min_score, document_id=document_id,
        )
        keyword = self._retrieve_bm25(query, top_k, version_id, document_id)

        fused = {}
        for rank, result in enumerate(vector, start=1):
            chunk, version, document, score = result
            key = str(chunk.id)
            entry = fused.setdefault(key, [result, 0.0, score])
            entry[1] += 1 / (self.rrf_k + rank)
        for rank, result in enumerate(keyword, start=1):
            chunk, version, document, _score = result
            key = str(chunk.id)
            entry = fused.setdefault(key, [result, 0.0, None])
            entry[1] += 1 / (self.rrf_k + rank)

        ordered = sorted(
            fused.values(),
            key=lambda item: (-item[1], str(item[0][0].id)),
        )[:top_k]
        results = [
            (chunk, version, document, cosine_score)
            for (chunk, version, document, _), rrf_score, cosine_score in ordered
        ]
        for (chunk, _version, _document, _), rrf_score, _cosine in ordered:
            chunk.rrf_score = rrf_score
        logger.info("Hybrid retrieval completed in %.4fs", time.perf_counter() - start)
        return results


def _proxies(row):
    class Proxy:
        def __init__(self, id, **values):
            self.id = id
            self.__dict__.update(values)

    return (
        Proxy(row[0], text=row[1], chunk_index=row[2]),
        Proxy(row[3], version_number=row[4]),
        Proxy(row[5], name=row[6]),
    )
