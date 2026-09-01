from app.config import settings
from app.storage.base import DocumentStorage
from app.storage.local import LocalDocumentStorage


def get_document_storage() -> DocumentStorage:

    if settings.document_storage == "local":
        return LocalDocumentStorage(
            base_dir=settings.document_storage_path
        )

    raise RuntimeError(
        f"Unsupported document storage: "
        f"{settings.document_storage}"
    )