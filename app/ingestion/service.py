from pathlib import Path

from app.ingestion.loader import load_text_file
from app.ingestion.pdf_loader import load_pdf
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

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = load_pdf(path)

        elif suffix == ".txt":
            text = load_text_file(path)

        else:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

        return chunk_text(
            text=text,
            source=source,
            version=version,
            chunk_size=chunk_size,
        )