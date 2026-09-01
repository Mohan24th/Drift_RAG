from pathlib import Path

from app.storage.base import DocumentStorage


class LocalDocumentStorage(
    DocumentStorage
):
    def __init__(
        self,
        base_dir: str,
    ):
        self.base_dir = Path(
            base_dir
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

        document_dir = (
            self.base_dir
            / document_id
            / f"v{version_number}"
        )

        document_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_filename = Path(
            filename
        ).name

        destination = (
            document_dir
            / safe_filename
        )

        source.replace(
            destination
        )

        return str(destination)