from app.database.connection import SessionLocal
from app.drift.version_loader import VersionLoader


def main():
    session = SessionLocal()

    try:
        loader = VersionLoader(session)

        # Use the document ID printed by
        # test_database_models.py / your database.
        document_id = input(
            "Enter document ID: "
        ).strip()

        result = loader.get_version(
            document_id=document_id,
            version_number=1,
        )

        if result is None:
            print("Version not found.")
            return

        document = result["document"]
        version = result["version"]
        chunks = result["chunks"]

        print("\nDocument:")
        print(document.name)

        print("\nVersion:")
        print(version.version_number)

        print("\nChunks:")
        print(len(chunks))

        for chunk in chunks:
            print(
                f"\n[{chunk.chunk_index}] "
                f"{chunk.text}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()