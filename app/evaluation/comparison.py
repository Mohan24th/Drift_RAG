from dataclasses import dataclass


@dataclass
class RetrievalComparison:
    query: str

    v1_chunks: list[str]
    v2_chunks: list[str]

    v1_scores: list[float]
    v2_scores: list[float]

    @property
    def common_chunks(self) -> set[str]:
        return set(self.v1_chunks) & set(self.v2_chunks)

    @property
    def v1_only_chunks(self) -> set[str]:
        return set(self.v1_chunks) - set(self.v2_chunks)

    @property
    def v2_only_chunks(self) -> set[str]:
        return set(self.v2_chunks) - set(self.v1_chunks)