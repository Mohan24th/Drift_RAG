from app.database.connection import SessionLocal
from app.drift.analyzer import DriftAnalyzer
from app.drift.retrieval import DriftRetriever
from app.drift.semantic import SemanticDrift
from app.drift.service import DriftService
from app.drift.summary import create_summary
from app.drift.version_loader import VersionLoader
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


QUERIES = [
    "How many vacation days do employees get?",
    "When should employees request leave?",
    "Can unused leave be carried forward?",
    "Who approves leave requests?",
]


def main():
    session = SessionLocal()

    try:
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

        service = DriftService(
            version_loader=version_loader,
            drift_retriever=drift_retriever,
            analyzer=analyzer,
        )

        document_id = (
            "647e4ef2-d359-4a93-8a27-f4bece148ee1"
        )

        reports = []

        for query in QUERIES:
            report = service.analyze(
                document_id=document_id,
                v1_number=1,
                v2_number=2,
                query=query,
                top_k=3,
            )

            reports.append(report)

        summary = create_summary(
            reports
        )

        print()
        print("=" * 60)
        print("DRIFT REPORT")
        print("Leave Policy: V1 → V2")
        print("=" * 60)

        print()
        print(
            f"Overall Drift: "
            f"{summary.overall_level}"
        )

        print(
            f"Overall Score: "
            f"{summary.overall_score:.4f}"
        )

        print(
            f"Queries evaluated: "
            f"{summary.total_queries}"
        )

        print(
            f"Affected queries: "
            f"{summary.affected_queries}"
        )

        print()
        print("-" * 60)

        for index, report in enumerate(
            reports,
            start=1,
        ):
            retrieval_drift = (
                1.0
                - report.retrieval_overlap
            )

            content_drift = (
                report.semantic_change
            )

            print()
            print(
                f"{index}. {report.query}"
            )

            print(
                f"   Retrieval drift: "
                f"{retrieval_drift:.4f}"
            )

            print(
                f"   Content drift:   "
                f"{content_drift:.4f}"
            )

            print(
                f"   Overall drift:   "
                f"{(retrieval_drift + content_drift) / 2:.4f}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()