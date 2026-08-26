from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text


def test_load_text_file():
    text = load_text_file("data/v1/company_policy.txt")

    assert text
    assert "20 days" in text


def test_chunk_text():
    text = (
        "First paragraph.\n\n"
        "Second paragraph.\n\n"
        "Third paragraph."
    )

    chunks = chunk_text(
        text=text,
        source="test.txt",
        version="v1",
        chunk_size=35,
    )

    assert len(chunks) == 2

    assert chunks[0].version == "v1"
    assert chunks[0].source == "test.txt"
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "First paragraph.\n\nSecond paragraph."

    assert chunks[1].chunk_index == 1
    assert chunks[1].text == "Third paragraph."


def test_empty_text():
    chunks = chunk_text(
        text="",
        source="test.txt",
        version="v1",
    )

    assert chunks == []