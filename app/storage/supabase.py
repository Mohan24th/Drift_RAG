from pathlib import Path
from tempfile import NamedTemporaryFile

from supabase import create_client

from app.storage.base import DocumentStorage


class SupabaseDocumentStorage(
    DocumentStorage
):
    def __init__(
        self,
        supabase_url: str,
        service_key: str,
        bucket: str,
    ):
        self.bucket = bucket

        self.client = create_client(
            supabase_url,
            service_key,
        )

    def save(
        self,
        source_path: str,
        document_id: str,
        version_number: int,
        filename: str,
    ) -> str:

        source = Path(source_path)

        if not source.is_file():
            raise FileNotFoundError(
                f"Source file not found: {source}"
            )

        safe_filename = Path(
            filename
        ).name

        storage_path = (
            f"{document_id}/"
            f"v{version_number}/"
            f"{safe_filename}"
        )

        try:
            with source.open("rb") as file:
                self.client.storage \
                    .from_(self.bucket) \
                    .upload(
                        path=storage_path,
                        file=file,
                        file_options={
                            "upsert": False,
                        },
                    )

        except Exception as exc:
            raise RuntimeError(
                "Failed to upload document "
                "to Supabase Storage."
            ) from exc

        return storage_path

    def get_local_path(
        self,
        storage_path: str,
    ) -> str:

        suffix = Path(
            storage_path
        ).suffix

        temp_file = NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        )

        temp_path = temp_file.name

        temp_file.close()

        try:
            response = (
                self.client.storage
                .from_(self.bucket)
                .download(storage_path)
            )

            Path(temp_path).write_bytes(
                response
            )

            return temp_path

        except Exception as exc:
            Path(temp_path).unlink(
                missing_ok=True
            )

            raise RuntimeError(
                "Failed to download document "
                "from Supabase Storage."
            ) from exc