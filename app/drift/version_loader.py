from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    ChunkModel,
    DocumentModel,
    DocumentVersionModel,
)


class VersionLoader:
    def __init__(self, session: Session):
        self.session = session

    def get_version(
        self,
        document_id: str,
        version_number: int,
    ):
        statement = (
            select(
                DocumentModel,
                DocumentVersionModel,
                ChunkModel,
            )
            .join(
                DocumentVersionModel,
                DocumentModel.id
                == DocumentVersionModel.document_id,
            )
            .join(
                ChunkModel,
                DocumentVersionModel.id
                == ChunkModel.version_id,
            )
            .where(
                DocumentModel.id == document_id,
                DocumentVersionModel.version_number
                == version_number,
            )
            .order_by(
                ChunkModel.chunk_index
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        if not rows:
            return None

        document = rows[0][0]
        version = rows[0][1]
        chunks = [row[2] for row in rows]

        return {
            "document": document,
            "version": version,
            "chunks": chunks,
        }