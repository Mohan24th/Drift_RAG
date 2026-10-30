
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)
from app.retrieval.embeddings import EmbeddingModel


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
    ):
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        if min_score is not None and not -1 <= min_score <= 1:
            raise ValueError("min_score must be between -1 and 1.")

        query_embedding = self.embedding_model.encode(
            [query]
        )[0].tolist()

        distance = ChunkModel.embedding.cosine_distance(
            query_embedding
        )
        similarity = 1 - distance

        statement = (
            select(
                ChunkModel,
                DocumentVersionModel,
                DocumentModel,
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
            # Explicit version selection supports version comparisons
            # and drift analysis, including archived versions.
            statement = statement.where(
                DocumentVersionModel.id == version_id
            )
        else:
            # Normal employee queries use approved versions only.
            statement = statement.where(
                DocumentVersionModel.status == "APPROVED"
            )

        if min_score is not None:
            statement = statement.where(similarity >= min_score)

        statement = statement.order_by(distance).limit(top_k)

        results = self.session.execute(statement).all()

        return [
            (chunk, version, document, float(score))
            for chunk, version, document, score in results
        ]
