from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

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
from app.auth.dependencies import require_roles
from app.auth.models import User
from app.database.document_service import DocumentService
from app.database.models import DocumentModel
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.storage.base import DocumentStorage
from app.storage.dependencies import (
    get_document_storage,
)


router = APIRouter()


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


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
    repository = DocumentRepository(
        session=session,
    )

    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Document name cannot be empty.",
        )

    existing = repository.get_document_by_name(
        name
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="A document with this name already exists.",
        )

    document = DocumentModel(
        id=str(uuid4()),
        name=name,
    )

    repository.create_document(
        document
    )

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
    document_service: DocumentService = Depends(
        get_document_service
    ),
    current_user: User = Depends(
        require_roles("HR", "ADMIN")
    ),
    document_storage: DocumentStorage = Depends(
        get_document_storage
    ),
):
    repository = DocumentRepository(
        session=session,
    )

    document = repository.get_document_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    expected_version = (
        repository.get_next_version_number(
            document_id
        )
    )

    if version_number != expected_version:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Invalid version number. "
                f"The next version must be "
                f"v{expected_version}."
            ),
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    suffix = Path(
        file.filename
    ).suffix.lower()

    if suffix not in {
        ".pdf",
        ".txt",
    }:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    temp_path = None
    total_size = 0

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            while True:
                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "File size exceeds "
                            "the 10 MB limit."
                        ),
                    )

                temp_file.write(chunk)

            temp_path = temp_file.name

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        stored_path = document_storage.save(
            source_path=temp_path,
            document_id=document.id,
            version_number=version_number,
            filename=file.filename,
        )

        # The storage layer moved the temporary file.
        temp_path = None

        result = document_service.ingest_document(
            file_path=stored_path,
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

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if temp_path:
            Path(
                temp_path
            ).unlink(
                missing_ok=True
            )

        await file.close()


@router.post(
    "/{document_id}/versions/{version_number}/approve",
    response_model=VersionResponse,
)
def approve_document_version(
    document_id: str,
    version_number: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("HR", "ADMIN")
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

    version = repository.get_version(
        document_id=document_id,
        version_number=version_number,
    )

    if version is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Version v{version_number} "
                "not found."
            ),
        )

    if version.status == "APPROVED":
        return VersionResponse(
            document_id=document_id,
            version_id=version.id,
            version_number=version.version_number,
            chunks_created=len(
                version.chunks
            ),
        )

    version.status = "APPROVED"
    version.approved_at = datetime.utcnow()

    session.commit()

    return VersionResponse(
        document_id=document_id,
        version_id=version.id,
        version_number=version.version_number,
        chunks_created=len(
            version.chunks
        ),
    )