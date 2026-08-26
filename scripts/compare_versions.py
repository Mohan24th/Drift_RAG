import json

from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.retriever import Retriever
from app.evaluation.comparison import RetrievalComparison


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

    retriever = Retriever(embedding_model)
    retriever.build_index(chunks)

    return retriever


def main():
    embedding_model = EmbeddingModel()

    print("Building V1 index...")
    v1_retriever = build_retriever(
        "v1",
        embedding_model,
    )

    print("Building V2 index...")
    v2_retriever = build_retriever(
        "v2",
        embedding_model,
    )

    with open(
        "data/queries.json",
        "r",
        encoding="utf-8",
    ) as file:
        queries = json.load(file)

    comparisons = []

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

        comparison = RetrievalComparison(
            query=query,
            v1_chunks=[
                chunk.chunk_id
                for chunk, _ in v1_results
            ],
            v2_chunks=[
                chunk.chunk_id
                for chunk, _ in v2_results
            ],
            v1_scores=[
                score
                for _, score in v1_results
            ],
            v2_scores=[
                score
                for _, score in v2_results
            ],
        )

        comparisons.append(comparison)

    print("\n=== V1 vs V2 Retrieval ===")

    for comparison in comparisons:
        print(f"\nQuery: {comparison.query}")

        print(
            f"V1: {comparison.v1_chunks}"
        )

        print(
            f"V2: {comparison.v2_chunks}"
        )

        print(
            f"Common: {comparison.common_chunks}"
        )

        print(
            f"V1 only: {comparison.v1_only_chunks}"
        )

        print(
            f"V2 only: {comparison.v2_only_chunks}"
        )


if __name__ == "__main__":
    main()