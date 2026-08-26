from dataclasses import dataclass


@dataclass
class DriftSummary:
    overall_score: float
    overall_level: str
    affected_queries: int
    total_queries: int


def calculate_overall_score(
    retrieval_drift: float,
    content_drift: float,
) -> float:
    return (
        retrieval_drift + content_drift
    ) / 2


def classify_drift(
    score: float,
) -> str:
    if score < 0.10:
        return "LOW"

    if score < 0.30:
        return "MEDIUM"

    return "HIGH"


def create_summary(
    reports,
) -> DriftSummary:

    if not reports:
        return DriftSummary(
            overall_score=0.0,
            overall_level="LOW",
            affected_queries=0,
            total_queries=0,
        )

    retrieval_drifts = []
    content_drifts = []
    affected = 0

    for report in reports:

        retrieval_drift = (
            1.0 - report.retrieval_overlap
        )

        content_drift = (
            report.semantic_change
        )

        retrieval_drifts.append(
            retrieval_drift
        )

        content_drifts.append(
            content_drift
        )

        if (
            retrieval_drift > 0
            or content_drift > 0
        ):
            affected += 1

    average_retrieval_drift = (
        sum(retrieval_drifts)
        / len(retrieval_drifts)
    )

    average_content_drift = (
        sum(content_drifts)
        / len(content_drifts)
    )

    overall_score = calculate_overall_score(
        retrieval_drift=average_retrieval_drift,
        content_drift=average_content_drift,
    )

    return DriftSummary(
        overall_score=overall_score,
        overall_level=classify_drift(
            overall_score
        ),
        affected_queries=affected,
        total_queries=len(reports),
    )