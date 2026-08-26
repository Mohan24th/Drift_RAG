from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import ChunkModel


def main():

    session = SessionLocal()

    try:
        statement = select(ChunkModel)

        chunks = session.execute(
            statement
        ).scalars().all()

        print(
            f"Database chunks: {len(chunks)}"
        )

        for chunk in chunks:

            print("\n--------------------")

            print(
                f"ID: {chunk.id}"
            )

            print(
                f"Version ID: {chunk.version_id}"
            )

            print(
                f"Index: {chunk.chunk_index}"
            )

            print(
                f"Text: {chunk.text}"
            )

            print(
                f"Embedding dimensions: "
                f"{len(chunk.embedding)}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()