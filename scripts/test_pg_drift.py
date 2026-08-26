from app.database.connection import SessionLocal
from app.drift.analyzer import DriftAnalyzer
from app.drift.retrieval import DriftRetriever
from app.drift.semantic import SemanticDrift
from app.drift.service import DriftService
from app.drift.version_loader import VersionLoader
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():
    session = SessionLocal()

    try:
        embedding_model = EmbeddingModel()

        pg_retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        drift_retriever = DriftRetriever(
            retriever=pg_retriever,
        )

        version_loader = VersionLoader(
            session=session,
        )

        semantic_detector = SemanticDrift(
            embedding_model=embedding_model,
        )

        analyzer = DriftAnalyzer(
            semantic_detector=semantic_detector,
        )

        drift_service = DriftService(
            version_loader=version_loader,
            drift_retriever=drift_retriever,
            analyzer=analyzer,
        )

        document_id = (
            "647e4ef2-d359-4a93-8a27-f4bece148ee1"
        )

        query = (
            "How many vacation days do employees get?"
        )

        report = drift_service.analyze(
            document_id=document_id,
            v1_number=1,
            v2_number=2,
            query=query,
            top_k=3,
        )

        print("\n=== PostgreSQL Drift Analysis ===\n")

        print(
            f"Query: {report.query}"
        )

        print(
            f"Retrieval overlap: "
            f"{report.retrieval_overlap:.4f}"
        )

        print(
            f"Rank change: "
            f"{report.rank_change:.4f}"
        )

        print(
            f"Semantic change: "
            f"{report.semantic_change:.4f}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()