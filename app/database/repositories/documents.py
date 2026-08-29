from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_document(
        self,
        document: DocumentModel,
    ) -> DocumentModel:

        self.session.add(document)
        self.session.flush()

        return document

    def create_version(
        self,
        version: DocumentVersionModel,
    ) -> DocumentVersionModel:

        self.session.add(version)
        self.session.flush()

        return version

    def create_chunks(
        self,
        chunks: list[ChunkModel],
    ) -> list[ChunkModel]:

        self.session.add_all(chunks)
        self.session.flush()

        return chunks

    def get_document_by_id(
        self,
        document_id: str,
    ) -> DocumentModel | None:

        statement = (
            select(DocumentModel)
            .where(
                DocumentModel.id == document_id
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_document_by_name(
        self,
        name: str,
    ) -> DocumentModel | None:

        statement = (
            select(DocumentModel)
            .where(
                DocumentModel.name == name
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_latest_version(
        self,
        document_id: str,
    ) -> DocumentVersionModel | None:

        statement = (
            select(DocumentVersionModel)
            .where(
                DocumentVersionModel.document_id
                == document_id
            )
            .order_by(
                DocumentVersionModel.version_number.desc()
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_version(
        self,
        document_id: str,
        version_number: int,
    ) -> DocumentVersionModel | None:

        statement = (
            select(DocumentVersionModel)
            .where(
                DocumentVersionModel.document_id
                == document_id,
                DocumentVersionModel.version_number
                == version_number,
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_next_version_number(
        self,
        document_id: str,
    ) -> int:

        latest = self.get_latest_version(
            document_id
        )

        if latest is None:
            return 1

        return latest.version_number + 1