from dataclasses import dataclass


@dataclass
class DriftChange:
    chunk_index: int
    v1_text: str
    v2_text: str
    change_type: str


@dataclass
class DriftReport:
    query: str

    retrieval_overlap: float
    rank_change: float
    semantic_change: float

    changes: list[DriftChange]

    @property
    def retrieval_drift(self) -> float:
        """
        Measures change in retrieval behavior.

        Combines:
        - top-k retrieval-set change
        - ranking change
        """

        overlap_drift = (
            1.0 - self.retrieval_overlap
        )

        return (
            overlap_drift
            + self.rank_change
        ) / 2

    @property
    def content_drift(self) -> float:
        """
        Measures semantic change in corresponding
        retrieved chunks.
        """

        return max(
            0.0,
            self.semantic_change,
        )

    @property
    def composite_drift_score(self) -> float:
        """
        Initial heuristic combining retrieval
        and content drift.

        This score is intended for relative comparison
        between corpus versions, not as an absolute
        probability or universally calibrated measure.
        """

        return (
            self.retrieval_drift
            + self.content_drift
        ) / 2