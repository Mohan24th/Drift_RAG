from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import chunk_text


def main():
    source = "company_policy.pdf"
    version = "v1"

    text = load_pdf(
        f"data/test_documents/{source}"
    )

    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=500,
    )

    print(f"Extracted characters: {len(text)}")
    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks:
        print(f"\n--- {chunk.chunk_id} ---")
        print(f"Source: {chunk.source}")
        print(f"Version: {chunk.version}")
        print(chunk.text[:500])


if __name__ == "__main__":
    main()