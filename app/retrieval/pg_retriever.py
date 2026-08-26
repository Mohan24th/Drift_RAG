from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ChunkModel
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
    ) -> list[tuple[ChunkModel, float]]:

        query_embedding = self.embedding_model.encode(
            [query]
        )[0].tolist()

        similarity = (
            1 - ChunkModel.embedding.cosine_distance(
                query_embedding
            )
        )

        statement = (
            select(
                ChunkModel,
                similarity.label("score"),
            )
            .order_by(
                ChunkModel.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(top_k)
        )

        results = self.session.execute(
            statement
        ).all()

        return [
            (chunk, float(score))
            for chunk, score in results
        ]