from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field

from app.api.dependencies import get_rag_service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.generation.service import RAGService


router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class SourceResponse(BaseModel):
    document_name: str
    version_number: int
    chunk_index: int
    score: float
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


@router.post(
    "/{document_id}/query",
    response_model=QueryResponse,
)
def query_document(
    document_id: str,
    request: QueryRequest,
    service: RAGService = Depends(
        get_rag_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        response = service.answer(
            document_id=document_id,
            question=question,
            top_k=request.top_k,
        )

        return QueryResponse(
            answer=response.answer,
            sources=[
                SourceResponse(
                    document_name=source.document_name,
                    version_number=source.version_number,
                    chunk_index=source.chunk_index,
                    score=source.score,
                    text=source.text,
                )
                for source in response.sources
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc