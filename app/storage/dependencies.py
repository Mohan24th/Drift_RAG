from app.config import settings
from app.storage.base import DocumentStorage
from app.storage.local import LocalDocumentStorage
from app.storage.supabase import (
    SupabaseDocumentStorage,
)


def get_document_storage() -> DocumentStorage:

    if settings.document_storage == "local":
        return LocalDocumentStorage(
            base_dir=settings.document_storage_path
        )

    if settings.document_storage == "supabase":
        return SupabaseDocumentStorage(
            supabase_url=settings.supabase_url,
            service_key=settings.supabase_service_key,
            bucket=settings.supabase_storage_bucket,
        )

    raise RuntimeError(
        "Unsupported document storage: "
        f"{settings.document_storage}"
    )