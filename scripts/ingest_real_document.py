from app.database.connection import SessionLocal
from app.database.document_service import DocumentService
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel


def main():

    session = SessionLocal()

    try:
        repository = DocumentRepository(
            session
        )

        ingestion_service = IngestionService()

        embedding_model = EmbeddingModel()

        service = DocumentService(
            repository=repository,
            ingestion_service=ingestion_service,
            embedding_model=embedding_model,
            session=session,
        )

        result = service.ingest_document(
            file_path=(
                "data/test_documents/"
                "company_policy_2.pdf"
            ),
            document_name="Leave Policy",
            version_number=2,
            chunk_size=100,
        )

        print("\n=== Document Ingested ===")

        print(
            f"Document ID: "
            f"{result['document'].id}"
        )

        print(
            f"Version: "
            f"v{result['version'].version_number}"
        )

        print(
            f"Chunks: "
            f"{len(result['chunks'])}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()