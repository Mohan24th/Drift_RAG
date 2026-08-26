from app.ingestion.chunker import Chunk
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.vector_store import VectorStore


class Indexer:
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model

    def build_index(
        self,
        chunks: list[Chunk],
    ) -> VectorStore:

        if not chunks:
            raise ValueError(
                "Cannot build an index from zero chunks"
            )

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = self.embedding_model.encode(
            texts
        )

        store = VectorStore(
            dimension=embeddings.shape[1]
        )

        store.add(
            embeddings=embeddings,
            chunks=chunks,
        )

        return store