from dataclasses import dataclass


@dataclass
class DriftReport:
    query: str

    retrieval_overlap: float
    rank_change: float
    semantic_change: float

    @property
    def retrieval_drift(self) -> float:
        """
        Higher value means retrieval behavior
        changed more between corpus versions.
        """

        overlap_drift = 1.0 - self.retrieval_overlap

        return (
            overlap_drift + self.rank_change
        ) / 2

    @property
    def content_drift(self) -> float:
        """
        Higher value means the content of corresponding
        retrieved chunks changed more.
        """

        return max(0.0, self.semantic_change)
    @property
    def overall_drift(self) -> float:
        """
        Combined drift score.

        Retrieval behavior and content change are
        weighted equally for the initial version.
        """

        return max(
            0.0,
            (
                self.retrieval_drift
                + self.content_drift
            ) / 2,
        )