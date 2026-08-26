from dataclasses import dataclass

from app.drift.report import DriftReport


@dataclass
class DriftSummary:
    reports: list[DriftReport]

    @property
    def query_count(self) -> int:
        return len(self.reports)

    @property
    def average_retrieval_drift(self) -> float:
        if not self.reports:
            return 0.0

        return sum(
            report.retrieval_drift
            for report in self.reports
        ) / len(self.reports)

    @property
    def average_content_drift(self) -> float:
        if not self.reports:
            return 0.0

        return sum(
            report.content_drift
            for report in self.reports
        ) / len(self.reports)

    @property
    def composite_drift_score(self) -> float:
        if not self.reports:
            return 0.0

        return sum(
            report.composite_drift_score
            for report in self.reports
        ) / len(self.reports)

    @property
    def most_affected_queries(
        self,
    ) -> list[DriftReport]:

        return sorted(
            self.reports,
            key=lambda report: report.composite_drift_score,
            reverse=True,
        )