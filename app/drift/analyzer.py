from app.drift.report import DriftReport
from app.drift.metrics import (
    top_k_overlap,
    mean_rank_change,
)
from app.drift.semantic import SemanticDrift


class DriftAnalyzer:
    def __init__(
        self,
        semantic_detector: SemanticDrift,
    ):
        self.semantic_detector = semantic_detector

    def analyze(
        self,
        query: str,
        v1_results,
        v2_results,
    ) -> DriftReport:

        v1_ids = [
            chunk.chunk_id
            for chunk, _ in v1_results
        ]

        v2_ids = [
            chunk.chunk_id
            for chunk, _ in v2_results
        ]

        retrieval_overlap = top_k_overlap(
            v1_ids,
            v2_ids,
        )

        rank_change = mean_rank_change(
            v1_ids,
            v2_ids,
        )

        v2_by_id = {
            chunk.chunk_id: chunk
            for chunk, _ in v2_results
        }

        weighted_changes = []
        total_weight = 0.0

        for rank, (v1_chunk, _) in enumerate(
            v1_results,
            start=1,
        ):
            v2_chunk = v2_by_id.get(
                v1_chunk.chunk_id
            )

            if v2_chunk is None:
                continue

            change = self.semantic_detector.calculate(
                v1_chunk.text,
                v2_chunk.text,
            )

            weight = 1.0 / rank

            weighted_changes.append(
                change * weight
            )

            total_weight += weight

        if total_weight > 0:
            semantic_change = (
                sum(weighted_changes)
                / total_weight
            )
        else:
            semantic_change = 1.0

        return DriftReport(
            query=query,
            retrieval_overlap=retrieval_overlap,
            rank_change=rank_change,
            semantic_change=max(
                0.0,
                semantic_change,
            ),
        )