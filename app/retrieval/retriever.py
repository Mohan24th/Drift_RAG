import numpy as np

from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple]:

        query_embedding = self.embedding_model.encode(
            [query]
        )

        return self.vector_store.search(
            query_embedding.astype(np.float32),
            top_k=top_k,
        )