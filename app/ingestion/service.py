
from pathlib import Path

from app.ingestion.loader import load_document
from app.ingestion.chunker import Chunk, chunk_text


class IngestionService:
    def ingest(
        self,
        file_path: str,
        source: str,
        version: str,
        chunk_size: int = 500,
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

        # Load the file according to its extension.
        text = load_document(path)

        # Preserve the existing chunking interface.
        return chunk_text(
            text=text,
            source=source,
            version=version,
            chunk_size=chunk_size,
        )
