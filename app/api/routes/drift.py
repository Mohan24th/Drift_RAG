from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.document_service import DocumentService
from app.database.repositories.documents import DocumentRepository
from app.drift.analyzer import DriftAnalyzer
from app.drift.retrieval import DriftRetriever
from app.drift.semantic import SemanticDrift
from app.drift.service import DriftService
from app.drift.summary import create_summary
from app.drift.version_loader import VersionLoader
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


router = APIRouter()


class DriftRequest(BaseModel):
    from_version: int = Field(
        gt=0
    )

    to_version: int = Field(
        gt=0
    )

    queries: list[str] = Field(
        min_length=1,
        max_length=50,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class DriftReportResponse(BaseModel):
    query: str
    retrieval_overlap: float
    rank_change: float
    semantic_change: float


class DriftResponse(BaseModel):
    document_id: str
    from_version: int
    to_version: int
    queries_evaluated: int
    affected_queries: int
    overall_level: str
    overall_score: float
    reports: list[DriftReportResponse]


def build_drift_service(
    session: Session,
) -> DriftService:

    repository = DocumentRepository(
        session=session,
    )

    document_service = DocumentService(
        repository=repository,
        ingestion_service=None,
        embedding_model=None,
        session=session,
    )

    embedding_model = EmbeddingModel()

    retriever = PgRetriever(
        session=session,
        embedding_model=embedding_model,
    )

    drift_retriever = DriftRetriever(
        retriever=retriever,
    )

    version_loader = VersionLoader(
        session=session,
    )

    analyzer = DriftAnalyzer(
        semantic_detector=SemanticDrift(
            embedding_model=embedding_model,
        ),
    )

    return DriftService(
        version_loader=version_loader,
        drift_retriever=drift_retriever,
        analyzer=analyzer,
    )


@router.post(
    "/{document_id}/drift",
    response_model=DriftResponse,
)
def analyze_drift(
    document_id: str,
    request: DriftRequest,
    session: Session = Depends(get_db),
):

    if request.from_version == request.to_version:
        raise HTTPException(
            status_code=400,
            detail="from_version and to_version must be different.",
        )

    if request.from_version > request.to_version:
        raise HTTPException(
            status_code=400,
            detail="from_version must be less than to_version.",
        )

    queries = [
        query.strip()
        for query in request.queries
        if query.strip()
    ]

    if not queries:
        raise HTTPException(
            status_code=422,
            detail="At least one non-empty query is required.",
        )

    try:
        service = build_drift_service(
            session
        )

        reports = []

        for query in queries:
            report = service.analyze(
                document_id=document_id,
                v1_number=request.from_version,
                v2_number=request.to_version,
                query=query,
                top_k=request.top_k,
            )

            reports.append(
                report
            )

        summary = create_summary(
            reports
        )

        return DriftResponse(
            document_id=document_id,
            from_version=request.from_version,
            to_version=request.to_version,
            queries_evaluated=summary.total_queries,
            affected_queries=summary.affected_queries,
            overall_level=summary.overall_level,
            overall_score=summary.overall_score,
            reports=[
                DriftReportResponse(
                    query=report.query,
                    retrieval_overlap=report.retrieval_overlap,
                    rank_change=report.rank_change,
                    semantic_change=report.semantic_change,
                )
                for report in reports
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc