from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.document_service import DocumentService
from app.database.repositories.documents import DocumentRepository
from app.generation.llm import LLM
from app.generation.qa import RAGAnswerer
from app.generation.service import RAGService
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


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


def build_rag_service(
    session: Session,
) -> RAGService:

    repository = DocumentRepository(
        session=session,
    )

    document_service = DocumentService(
        repository=repository,
        ingestion_service=IngestionService(),
        embedding_model=EmbeddingModel(),
        session=session,
    )

    retriever = PgRetriever(
        session=session,
        embedding_model=document_service.embedding_model,
    )

    answerer = RAGAnswerer(
        retriever=retriever,
        llm=LLM(),
    )

    return RAGService(
        document_service=document_service,
        answerer=answerer,
    )


@router.post(
    "/{document_id}/query",
    response_model=QueryResponse,
)
def query_document(
    document_id: str,
    request: QueryRequest,
    session: Session = Depends(get_db),
):

    try:
        service = build_rag_service(
            session
        )

        response = service.answer(
            document_id=document_id,
            question=request.question.strip(),
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