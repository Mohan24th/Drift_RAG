from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text


def test_load_text_file():
    text = load_text_file("data/v1/company_policy.txt")

    assert text
    assert "20 days" in text


def test_chunk_text():
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = chunk_text(
        text,
        chunk_size=10,
        chunk_overlap=2,
    )

    assert len(chunks) > 1
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "ijklmnopqr"