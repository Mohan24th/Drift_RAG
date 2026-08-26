import json

#from rich.prompt import result

from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text

from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.retriever import Retriever

from app.drift.semantic import SemanticDrift
from app.drift.analyzer import DriftAnalyzer


def build_retriever(
    version: str,
    embedding_model: EmbeddingModel,
) -> Retriever:

    source = "company_policy.txt"

    text = load_text_file(
        f"data/{version}/{source}"
    )

    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=100,
    )

    retriever = Retriever(
        embedding_model
    )

    retriever.build_index(chunks)

    return retriever


def main():

    embedding_model = EmbeddingModel()

    v1_retriever = build_retriever(
        "v1",
        embedding_model,
    )

    v2_retriever = build_retriever(
        "v2",
        embedding_model,
    )

    semantic_detector = SemanticDrift(
        embedding_model
    )

    analyzer = DriftAnalyzer(
        semantic_detector
    )

    with open(
        "data/queries.json",
        "r",
        encoding="utf-8",
    ) as file:

        queries = json.load(file)

    print("\n=== DRIFT ANALYSIS ===")

    for item in queries:

        query = item["query"]

        v1_results = v1_retriever.retrieve(
            query,
            top_k=3,
        )

        v2_results = v2_retriever.retrieve(
            query,
            top_k=3,
        )

        result = analyzer.analyze(
            query=query,
            v1_results=v1_results,
            v2_results=v2_results,
        )

        print("\n-----------------------------")

        print(f"Query: {result.query}")

        print(
        f"Retrieval overlap: "
        f"{result.retrieval_overlap:.4f}"
        )

        print(
            f"Rank change: "
            f"{result.rank_change:.4f}"
        )

        print(
            f"Semantic change: "
            f"{max(0.0, result.semantic_change):.4f}"
        )

        print(
            f"Retrieval drift: "
            f"{result.retrieval_drift:.4f}"
        )

        print(
            f"Content drift: "
            f"{result.content_drift:.4f}"
        )

        print(
            f"Overall drift: "
            f"{result.overall_drift:.4f}"
        )


if __name__ == "__main__":
    main()
