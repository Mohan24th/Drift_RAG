from app.ingestion.chunker import Chunk
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
    ):
        self.embedding_model = embedding_model
        self.vector_store: VectorStore | None = None

    def build_index(self, chunks: list[Chunk]) -> None:
        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_model.encode(texts)

        dimension = embeddings.shape[1]

        self.vector_store = VectorStore(dimension)
        self.vector_store.add(embeddings, chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[Chunk, float]]:
        if self.vector_store is None:
            raise RuntimeError("Index has not been built")

        query_embedding = self.embedding_model.encode([query])

        return self.vector_store.search(
            query_embedding,
            top_k=top_k,
        )