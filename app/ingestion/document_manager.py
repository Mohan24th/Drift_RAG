from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.models.document import Document, DocumentVersion


class DocumentManager:
    def __init__(self, storage_dir: str = "data/documents"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_document(
        self,
        name: str,
    ) -> Document:

        return Document(
            document_id=str(uuid4()),
            name=name,
            created_at=datetime.utcnow(),
        )

    def create_version(
        self,
        document: Document,
        source_file: str,
        version_number: int,
    ) -> DocumentVersion:

        version_id = str(uuid4())

        document_dir = (
            self.storage_dir
            / document.document_id
        )

        document_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            document_dir
            / f"v{version_number}"
            / Path(source_file).name
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_bytes(
            Path(source_file).read_bytes()
        )

        return DocumentVersion(
            version_id=version_id,
            document_id=document.document_id,
            version_number=version_number,
            file_path=str(destination),
            created_at=datetime.utcnow(),
        )