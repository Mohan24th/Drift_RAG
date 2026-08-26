from pathlib import Path
from uuid import uuid4

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        ingestion_service: IngestionService,
        embedding_model: EmbeddingModel,
        session,
    ):
        self.repository = repository
        self.ingestion_service = ingestion_service
        self.embedding_model = embedding_model
        self.session = session

    def ingest_document(
        self,
        file_path: str,
        document_name: str,
        version_number: int,
        chunk_size: int = 100,
    ):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        try:
            # 1. Find existing document
            #    or create a new one.
            document = (
                self.repository.get_document_by_name(
                    document_name
                )
            )

            if document is None:
                document = DocumentModel(
                    id=str(uuid4()),
                    name=document_name,
                )

                self.repository.create_document(
                    document
                )

            # 2. Create new version
            version = DocumentVersionModel(
                id=str(uuid4()),
                document_id=document.id,
                version_number=version_number,
                file_path=str(path),
            )

            self.repository.create_version(
                version
            )

            # 3. Extract and chunk
            chunks = self.ingestion_service.ingest(
                file_path=str(path),
                source=path.name,
                version=f"v{version_number}",
                chunk_size=chunk_size,
            )

            if not chunks:
                raise ValueError(
                    "No chunks were created from the document"
                )

            # 4. Generate embeddings
            embeddings = self.embedding_model.encode(
                [chunk.text for chunk in chunks]
            )

            # 5. Convert chunks to database models
            chunk_models = []

            for chunk, embedding in zip(
                chunks,
                embeddings,
            ):
                chunk_models.append(
                    ChunkModel(
                        id=str(uuid4()),
                        version_id=version.id,
                        chunk_index=chunk.chunk_index,
                        text=chunk.text,
                        embedding=embedding.tolist(),
                    )
                )

            # 6. Persist chunks
            self.repository.create_chunks(
                chunk_models
            )

            # 7. Commit entire operation
            self.session.commit()

            return {
                "document": document,
                "version": version,
                "chunks": chunk_models,
            }

        except Exception:
            self.session.rollback()
            raise

    def get_latest_version(
        self,
        document_id: str,
    ) -> DocumentVersionModel:

        version = self.repository.get_latest_version(
            document_id
        )

        if version is None:
            raise ValueError(
                f"No versions found for document: {document_id}"
            )

        return version