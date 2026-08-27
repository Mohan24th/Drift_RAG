from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_document_service,
)
from app.database.document_service import DocumentService
from app.database.models import DocumentModel
from app.database.repositories.documents import (
    DocumentRepository,
)


router = APIRouter()


class CreateDocumentRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )


class DocumentResponse(BaseModel):
    id: str
    name: str


class VersionResponse(BaseModel):
    document_id: str
    version_id: str
    version_number: int
    chunks_created: int


@router.post(
    "/",
    response_model=DocumentResponse,
)
def create_document(
    request: CreateDocumentRequest,
    session: Session = Depends(get_db),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Document name cannot be empty.",
        )

    repository = DocumentRepository(
        session=session
    )

    existing = repository.get_document_by_name(
        name
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "A document with this name "
                "already exists."
            ),
        )

    from uuid import uuid4

    document = DocumentModel(
        id=str(uuid4()),
        name=name,
    )

    repository.create_document(document)
    session.commit()

    return DocumentResponse(
        id=document.id,
        name=document.name,
    )


@router.post(
    "/{document_id}/versions",
    response_model=VersionResponse,
)
async def upload_document_version(
    document_id: str,
    file: UploadFile = File(...),
    version_number: int = Form(..., gt=0),
    session: Session = Depends(get_db),
    service: DocumentService = Depends(
        get_document_service
    ),
):
    repository = DocumentRepository(
        session=session
    )

    document = repository.get_document_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    suffix = Path(
        file.filename
    ).suffix.lower()

    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF and TXT files "
                "are supported."
            ),
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(content)
            temp_path = temp_file.name

        result = service.ingest_document(
            file_path=temp_path,
            document_name=document.name,
            version_number=version_number,
        )

        return VersionResponse(
            document_id=document.id,
            version_id=result["version"].id,
            version_number=result["version"].version_number,
            chunks_created=len(
                result["chunks"]
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if temp_path:
            Path(temp_path).unlink(
                missing_ok=True
            )