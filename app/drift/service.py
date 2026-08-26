from app.drift.analyzer import DriftAnalyzer
from app.drift.retrieval import DriftRetriever
from app.drift.version_loader import VersionLoader


class DriftService:
    def __init__(
        self,
        version_loader: VersionLoader,
        drift_retriever: DriftRetriever,
        analyzer: DriftAnalyzer,
    ):
        self.version_loader = version_loader
        self.drift_retriever = drift_retriever
        self.analyzer = analyzer

    def analyze(
        self,
        document_id: str,
        v1_number: int,
        v2_number: int,
        query: str,
        top_k: int = 3,
    ):
        v1 = self.version_loader.get_version(
            document_id=document_id,
            version_number=v1_number,
        )

        v2 = self.version_loader.get_version(
            document_id=document_id,
            version_number=v2_number,
        )

        if v1 is None:
            raise ValueError(
                f"Version {v1_number} not found"
            )

        if v2 is None:
            raise ValueError(
                f"Version {v2_number} not found"
            )

        v1_id = v1["version"].id
        v2_id = v2["version"].id

        v1_results = self.drift_retriever.retrieve(
            query=query,
            version_id=v1_id,
            top_k=top_k,
        )

        v2_results = self.drift_retriever.retrieve(
            query=query,
            version_id=v2_id,
            top_k=top_k,
        )

        return self.analyzer.analyze(
            query=query,
            v1_results=v1_results,
            v2_results=v2_results,
        )