from app.ingestion.service import IngestionService


def main():
    service = IngestionService()

    chunks = service.ingest(
        file_path="data/test_documents/company_policy.pdf",
        source="company_policy.pdf",
        version="v1",
        chunk_size=100,
    )

    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks:
        print(f"\n--- {chunk.chunk_id} ---")
        print(f"Source: {chunk.source}")
        print(f"Version: {chunk.version}")
        print(f"Index: {chunk.chunk_index}")
        print(chunk.text)


if __name__ == "__main__":
    main()