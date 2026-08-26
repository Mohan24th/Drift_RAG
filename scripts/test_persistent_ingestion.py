from uuid import uuid4

from app.database.connection import SessionLocal
from app.database.models import (
    DocumentModel,
    DocumentVersionModel,
)
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.ingestion.persistence import (
    IngestionPersistence,
)
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel


def main():

    session = SessionLocal()

    try:
        repository = DocumentRepository(
            session
        )

        persistence = IngestionPersistence(
            repository
        )

        ingestion_service = IngestionService()

        embedding_model = EmbeddingModel()

        # 1. Create document
        document = DocumentModel(
            id=str(uuid4()),
            name="Leave Policy",
        )

        repository.create_document(
            document
        )

        # 2. Create version
        version = DocumentVersionModel(
            id=str(uuid4()),
            document_id=document.id,
            version_number=1,
            file_path=(
                "data/test_documents/"
                "company_policy.pdf"
            ),
        )

        repository.create_version(
            version
        )

        # 3. Extract + chunk
        chunks = ingestion_service.ingest(
            file_path=(
                "data/test_documents/"
                "company_policy.pdf"
            ),
            source="company_policy.pdf",
            version="v1",
            chunk_size=100,
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        # 4. Generate embeddings
        embeddings = embedding_model.encode(
            [chunk.text for chunk in chunks]
        )

        print(
            f"Embeddings generated: "
            f"{len(embeddings)}"
        )

        print(
            f"Embedding dimension: "
            f"{embeddings.shape[1]}"
        )

        # 5. Persist chunks + embeddings
        saved_chunks = persistence.save_chunks(
            version=version,
            chunks=chunks,
            embeddings=embeddings,
        )

        session.commit()

        print(
            f"Chunks persisted: "
            f"{len(saved_chunks)}"
        )

        print("\nPersistence successful!")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()