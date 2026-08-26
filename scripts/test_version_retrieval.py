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

        document_id = input(
            "Enter document ID: "
        ).strip()

        from app.drift.version_loader import VersionLoader

        loader = VersionLoader(session)

        version = loader.get_version(
            document_id=document_id,
            version_number=1,
        )

        if version is None:
            print("Version 1 not found.")
            return

        version_id = version["version"].id

        results = retriever.retrieve(
            query="How many vacation days do employees get?",
            top_k=3,
            version_id=version_id,
        )

        print("\nV1 retrieval:")

        for rank, (
            chunk,
            retrieved_version,
            document,
            score,
        ) in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"chunk={chunk.chunk_index} "
                f"score={score:.4f}"
            )

            print(chunk.text)

    finally:
        session.close()


if __name__ == "__main__":
    main()