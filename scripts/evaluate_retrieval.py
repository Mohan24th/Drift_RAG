import json

from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.retriever import Retriever
from app.evaluation.evaluator import evaluate_retrieval


def main():
    source = "company_policy.txt"
    version = "v1"

    text = load_text_file(
        f"data/{version}/{source}"
    )

    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=100,
    )

    embedding_model = EmbeddingModel()

    retriever = Retriever(embedding_model)
    retriever.build_index(chunks)

    with open(
        "data/queries.json",
        "r",
        encoding="utf-8",
    ) as file:
        queries = json.load(file)

    results = evaluate_retrieval(
        retriever,
        queries,
        top_k=3,
    )

    hit_at_1 = sum(
        result.hit_at_1
        for result in results
    )

    hit_at_k = sum(
        result.hit_at_k
        for result in results
    )

    total = len(results)

    print("\n=== Retrieval Evaluation ===")

    for result in results:
        print(f"\nQuery: {result.query}")
        print(f"Expected: {result.expected_chunk}")
        print(f"Retrieved: {result.retrieved_chunks}")
        print(f"Hit@1: {result.hit_at_1}")
        print(f"Hit@3: {result.hit_at_k}")

    print("\n=== Summary ===")
    print(f"Queries: {total}")
    print(f"Hit@1: {hit_at_1}/{total}")
    print(f"Hit@3: {hit_at_k}/{total}")


if __name__ == "__main__":
    main()