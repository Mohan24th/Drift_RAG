from pathlib import Path
from app.ingestion.loader import load_document
from app.ingestion.chunker import Chunk, chunk_text
from app.config import settings

class IngestionService:
    def ingest(
        self,
        file_path: str,
        source: str,
        version: str,
        chunk_size: int | None = None,
    ) -> list[Chunk]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        text = load_document(path)

        # Pass chunk_size if provided, otherwise chunker uses settings.chunk_size
        # We explicitly pass None for overlap to ensure the chunker uses settings.chunk_overlap
        return chunk_text(
            text=text,
            source=source,
            version=version,
            chunk_size=chunk_size,
            overlap=None,
        )
