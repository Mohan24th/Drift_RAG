from uuid import uuid4

from app.database.connection import SessionLocal
from app.database.models import (
    DocumentModel,
    DocumentVersionModel,
)


def main():

    session = SessionLocal()

    try:
        document = DocumentModel(
            id=str(uuid4()),
            name="Leave Policy",
        )

        session.add(document)

        version = DocumentVersionModel(
            id=str(uuid4()),
            document_id=document.id,
            version_number=1,
            file_path="data/test_documents/company_policy.pdf",
        )

        session.add(version)

        session.commit()

        print("Document created:")
        print(document.id)
        print(document.name)

        print("\nVersion created:")
        print(version.id)
        print(version.version_number)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()