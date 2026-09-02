from app.drift.metrics import (
    mean_rank_change,
    top_k_overlap,
)
from app.drift.report import (
    DriftChange,
    DriftReport,
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

        # -------------------------------------------------
        # Retrieval identity
        # -------------------------------------------------
        # chunk_index is the logical identity across
        # document versions.
        #
        # Database UUIDs are different for each version,
        # so UUIDs cannot be used for cross-version
        # comparison.

        v1_ids = [
            chunk.chunk_index
            for chunk, _ in v1_results
        ]

        v2_ids = [
            chunk.chunk_index
            for chunk, _ in v2_results
        ]

        # -------------------------------------------------
        # Retrieval drift
        # -------------------------------------------------

        retrieval_overlap = top_k_overlap(
            v1_ids,
            v2_ids,
        )

        rank_change = mean_rank_change(
            v1_ids,
            v2_ids,
        )

        # -------------------------------------------------
        # Content drift
        # -------------------------------------------------

        v2_by_index = {
            chunk.chunk_index: chunk
            for chunk, _ in v2_results
        }

        weighted_changes = []
        total_weight = 0.0

        changes = []

        for rank, (v1_chunk, _) in enumerate(
            v1_results,
            start=1,
        ):
            v2_chunk = v2_by_index.get(
                v1_chunk.chunk_index
            )

            if v2_chunk is None:
                changes.append(
                    DriftChange(
                        chunk_index=v1_chunk.chunk_index,
                        v1_text=v1_chunk.text,
                        v2_text="",
                        change_type="REMOVED",
                    )
                )

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

            if change > 0:
                changes.append(
                    DriftChange(
                        chunk_index=v1_chunk.chunk_index,
                        v1_text=v1_chunk.text,
                        v2_text=v2_chunk.text,
                        change_type="CONTENT",
                    )
                )

        # -------------------------------------------------
        # Detect newly retrieved chunks
        # -------------------------------------------------

        v1_index_set = set(
            v1_ids
        )

        for v2_chunk, _ in v2_results:

            if (
                v2_chunk.chunk_index
                not in v1_index_set
            ):
                changes.append(
                    DriftChange(
                        chunk_index=v2_chunk.chunk_index,
                        v1_text="",
                        v2_text=v2_chunk.text,
                        change_type="ADDED",
                    )
                )

        # -------------------------------------------------
        # Semantic change
        # -------------------------------------------------

        if total_weight > 0:
            semantic_change = (
                sum(weighted_changes)
                / total_weight
            )

        else:
            semantic_change = 1.0

        # -------------------------------------------------
        # Final report
        # -------------------------------------------------

        return DriftReport(
            query=query,
            retrieval_overlap=retrieval_overlap,
            rank_change=rank_change,
            semantic_change=max(
                0.0,
                semantic_change,
            ),
            changes=changes,
        )