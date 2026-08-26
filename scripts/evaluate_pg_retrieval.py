import json

from app.database.connection import SessionLocal
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():
    with open("data/queries.json", "r") as file:
        queries = json.load(file)

    session = SessionLocal()

    try:
        embedding_model = EmbeddingModel()

        retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        hit_at_1 = 0
        hit_at_3 = 0

        print("\n=== PostgreSQL Retrieval Evaluation ===\n")

        for item in queries:
            query = item["query"]
            expected_chunk = item["expected_chunk"]

            expected_index = int(
                expected_chunk.split("-")[-1]
            )

            results = retriever.retrieve(
                query,
                top_k=3,
            )

            retrieved_indices = [
                chunk.chunk_index
                for chunk, _ in results
            ]

            hit1 = (
                len(retrieved_indices) > 0
                and retrieved_indices[0] == expected_index
            )

            hit3 = (
                expected_index in retrieved_indices
            )

            if hit1:
                hit_at_1 += 1

            if hit3:
                hit_at_3 += 1

            print(f"Query: {query}")
            print(f"Expected: {expected_chunk}")
            print(
                f"Retrieved: "
                f"{retrieved_indices}"
            )
            print(f"Hit@1: {hit1}")
            print(f"Hit@3: {hit3}")
            print()

        total = len(queries)

        print("=== Summary ===")
        print(f"Queries: {total}")
        print(f"Hit@1: {hit_at_1}/{total}")
        print(f"Hit@3: {hit_at_3}/{total}")

    finally:
        session.close()


if __name__ == "__main__":
    main()