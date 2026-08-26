import json

from app.drift.analyzer import DriftAnalyzer
from app.drift.semantic import SemanticDrift
from app.drift.summary import DriftSummary
from app.ingestion.chunker import chunk_text
from app.ingestion.loader import load_text_file
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.retriever import Retriever


def build_retriever(version: str, embedding_model: EmbeddingModel) -> Retriever:
    """Loads a policy document version, chunks it, and builds a retriever index."""
    source = "company_policy.txt"
    text = load_text_file(f"data/{version}/{source}")
    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=100,
    )
    retriever = Retriever(embedding_model)
    retriever.build_index(chunks)
    return retriever


def main():
    embedding_model = EmbeddingModel()
    v1_retriever = build_retriever("v1", embedding_model)

    semantic_detector = SemanticDrift(embedding_model)
    analyzer = DriftAnalyzer(semantic_detector)

    with open("data/queries.json", "r", encoding="utf-8") as file:
        queries = json.load(file)

    versions = ["v2", "v3", "v4"]

    for version in versions:
        print("\n")
        print("=" * 50)
        print(f"COMPARISON: V1 → {version.upper()}")
        print("=" * 50)

        version_retriever = build_retriever(version, embedding_model)
        reports = []

        for item in queries:
            query = item["query"]
            v1_results = v1_retriever.retrieve(query, top_k=3)
            version_results = version_retriever.retrieve(query, top_k=3)

            report = analyzer.analyze(
                query=query,
                v1_results=v1_results,
                v2_results=version_results,
            )
            reports.append(report)

        summary = DriftSummary(reports)

        print("\n=== SUMMARY ===")
        print(f"Queries evaluated: {summary.query_count}")
        print(f"Average retrieval drift: {summary.average_retrieval_drift:.4f}")
        print(f"Average content drift: {summary.average_content_drift:.4f}")
        print(f"Composite drift score: {summary.composite_drift_score:.4f}")

        print("\n=== MOST AFFECTED QUERIES ===")
        for rank, report in enumerate(summary.most_affected_queries, start=1):
            print(f"\n{rank}. {report.query}")
            print(f"  Drift: {report.composite_drift_score:.4f}")
            print(f"  Retrieval: {report.retrieval_drift:.4f}")
            print(f"  Content: {report.content_drift:.4f}")


if __name__ == "__main__":
    main()
