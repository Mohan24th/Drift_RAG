import time
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)
from app.retrieval.embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

class PgRetriever:
    def __init__(
        self,
        session: Session,
        embedding_model: EmbeddingModel,
    ):
        self.session = session
        self.embedding_model = embedding_model

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        version_id: str | None = None,
        min_score: float | None = None,
        document_id: str | None = None,
        allow_unapproved_version: bool = False,
    ):
        start_total = time.perf_counter()
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        if min_score is not None and not -1 <= min_score <= 1:
            raise ValueError("min_score must be between -1 and 1.")

        # 1. Embedding Generation Timing
        start_emb = time.perf_counter()
        query_embedding = self.embedding_model.encode(
            [query]
        )[0].tolist()
        emb_time = time.perf_counter() - start_emb

        distance = ChunkModel.embedding.cosine_distance(
            query_embedding
        )
        similarity = 1 - distance

        # OPTIMIZATION: Select only required columns instead of full models
        # Downstream consumers (RAGAnswerer/DriftService) need:
        # Chunk: text, chunk_index, id
        # Version: version_number, id
        # Document: name, id
        # Score: similarity
        statement = (
            select(
                ChunkModel.id,
                ChunkModel.text,
                ChunkModel.chunk_index,
                DocumentVersionModel.id,
                DocumentVersionModel.version_number,
                DocumentModel.id,
                DocumentModel.name,
                similarity.label("score"),
            )
            .join(
                DocumentVersionModel,
                ChunkModel.version_id == DocumentVersionModel.id,
            )
            .join(
                DocumentModel,
                DocumentVersionModel.document_id == DocumentModel.id,
            )
        )

        if version_id is not None:
            statement = statement.where(
                DocumentVersionModel.id == version_id
            )
            if not allow_unapproved_version:
                statement = statement.where(
                    DocumentVersionModel.status == "APPROVED"
                )
        else:
            statement = statement.where(
                DocumentVersionModel.status == "APPROVED"
            )

        if document_id is not None:
            statement = statement.where(DocumentModel.id == document_id)

        if min_score is not None:
            statement = statement.where(similarity >= min_score)

        statement = statement.order_by(distance).limit(top_k)

        # 2. DB Execution Timing
        start_db = time.perf_counter()
        results = self.session.execute(statement).all()
        db_time = time.perf_counter() - start_db

        # 3. Processing Timing
        start_proc = time.perf_counter()
        
        # Reconstruct a structure compatible with the existing consumers:
        # (chunk, version, document, score)
        # Since we selected specific columns, we create simple namespaces or objects 
        # to avoid breaking downstream attributes access.
        
        final_results = []
        for row in results:
            # Mocking the model objects to maintain backward compatibility with .text, .name etc.
            class ChunkProxy:
                def __init__(self, id, text, idx):
                    self.id = id; self.text = text; self.chunk_index = idx
            
            class VersionProxy:
                def __init__(self, id, num):
                    self.id = id; self.version_number = num
            
            class DocumentProxy:
                def __init__(self, id, name):
                    self.id = id; self.name = name

            final_results.append((
                ChunkProxy(row[0], row[1], row[2]),
                VersionProxy(row[3], row[4]),
                DocumentProxy(row[5], row[6]),
                float(row[7])
            ))
        
        proc_time = time.perf_counter() - start_proc
        total_time = time.perf_counter() - start_total

        logger.info(
            "Retrieval Performance: total=%.4fs, emb=%.4fs, db=%.4fs, proc=%.4fs",
            total_time, emb_time, db_time, proc_time
        )

        return final_results
