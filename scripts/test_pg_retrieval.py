from app.database.connection import SessionLocal
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():
    session = SessionLocal()

    try:
        embedding_model = EmbeddingModel()

        retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        # Current active version: V2
        version_id = (
            "32bca701-1a13-4e66-a451-1061f0faa20a"
        )

        queries = [
            "How many vacation days do employees get?",
            "When should employees request leave?",
            "Who approves leave?",
        ]

        for query in queries:

            print(f"\nQUERY: {query}")

            results = retriever.retrieve(
                query,
                top_k=3,
                version_id=version_id,
            )

            for rank, (
                chunk,
                version,
                document,
                score,
            ) in enumerate(
                results,
                start=1,
            ):
                print(
                    f"\n{rank}. "
                    f"{document.name} "
                    f"v{version.version_number} "
                    f"chunk={chunk.chunk_index} "
                    f"score={score:.4f}"
                )

                print(chunk.text)

    finally:
        session.close()


if __name__ == "__main__":
    main()