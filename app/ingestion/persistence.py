from uuid import uuid4

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.ingestion.chunker import Chunk


class IngestionPersistence:
    def __init__(
        self,
        repository: DocumentRepository,
    ):
        self.repository = repository

    def save_chunks(
        self,
        version: DocumentVersionModel,
        chunks: list[Chunk],
        embeddings,
    ) -> list[ChunkModel]:

        models = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            model = ChunkModel(
                id=str(uuid4()),
                version_id=version.id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                embedding=embedding.tolist(),
            )

            models.append(model)

        return self.repository.create_chunks(
            models
        )