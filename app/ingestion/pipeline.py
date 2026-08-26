from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.indexer import Indexer
from app.retrieval.retriever import Retriever


class IngestionPipeline:
    def __init__(
        self,
        ingestion_service: IngestionService,
        embedding_model: EmbeddingModel,
    ):
        self.ingestion_service = ingestion_service
        self.embedding_model = embedding_model
        self.indexer = Indexer(
            embedding_model
        )

    def process(
        self,
        file_path: str,
        source: str,
        version: str,
        chunk_size: int = 500,
    ) -> Retriever:

        chunks = self.ingestion_service.ingest(
            file_path=file_path,
            source=source,
            version=version,
            chunk_size=chunk_size,
        )

        vector_store = self.indexer.build_index(
            chunks
        )

        return Retriever(
            embedding_model=self.embedding_model,
            vector_store=vector_store,
        )