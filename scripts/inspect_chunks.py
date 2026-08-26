from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text


def main():
    source = "company_policy.txt"
    version = "v1"

    text = load_text_file(f"data/{version}/{source}")

    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=100,
    )

    print(f"Document: {source}")
    print(f"Version: {version}")
    print(f"Chunks: {len(chunks)}")

    for chunk in chunks:
        print(f"\n--- {chunk.chunk_id} ---")
        print(f"Source: {chunk.source}")
        print(f"Version: {chunk.version}")
        print(f"Index: {chunk.chunk_index}")
        print(chunk.text)


if __name__ == "__main__":
    main()