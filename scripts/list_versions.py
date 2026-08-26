from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import (
    DocumentModel,
    DocumentVersionModel,
)


def main():
    session = SessionLocal()

    try:
        statement = (
            select(
                DocumentModel,
                DocumentVersionModel,
            )
            .join(
                DocumentVersionModel,
                DocumentModel.id
                == DocumentVersionModel.document_id,
            )
            .order_by(
                DocumentModel.name,
                DocumentVersionModel.version_number,
            )
        )

        rows = session.execute(
            statement
        ).all()

        print("\n=== Database Versions ===\n")

        for document, version in rows:
            print(
                f"Document: {document.name}"
            )
            print(
                f"Document ID: {document.id}"
            )
            print(
                f"Version: v{version.version_number}"
            )
            print(
                f"Version ID: {version.id}"
            )
            print(
                f"File: {version.file_path}"
            )
            print()

    finally:
        session.close()


if __name__ == "__main__":
    main()