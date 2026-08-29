from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field

from app.api.dependencies import get_drift_service
from app.drift.service import DriftService
from app.drift.summary import create_summary


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


@router.post(
    "/{document_id}/drift",
    response_model=DriftResponse,
)
def analyze_drift(
    document_id: str,
    request: DriftRequest,
    service: DriftService = Depends(
        get_drift_service
    ),
):

    if request.from_version == request.to_version:
        raise HTTPException(
            status_code=400,
            detail=(
                "from_version and to_version "
                "must be different."
            ),
        )

    if request.from_version > request.to_version:
        raise HTTPException(
            status_code=400,
            detail=(
                "from_version must be less than "
                "to_version."
            ),
        )

    queries = [
        query.strip()
        for query in request.queries
        if query.strip()
    ]

    if not queries:
        raise HTTPException(
            status_code=422,
            detail=(
                "At least one non-empty query "
                "is required."
            ),
        )

    try:
        reports = []

        for query in queries:
            report = service.analyze(
                document_id=document_id,
                v1_number=request.from_version,
                v2_number=request.to_version,
                query=query,
                top_k=request.top_k,
            )

            reports.append(report)

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
                    retrieval_overlap=(
                        report.retrieval_overlap
                    ),
                    rank_change=(
                        report.rank_change
                    ),
                    semantic_change=(
                        report.semantic_change
                    ),
                )
                for report in reports
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc