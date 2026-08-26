from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text


def test_load_text_file(tmp_path):
    file_path = tmp_path / "company_policy.txt"

    file_path.write_text(
        "Company Leave Policy\n\n"
        "Employees receive 20 days of annual leave.",
        encoding="utf-8",
    )

    text = load_text_file(file_path)

    assert "Company Leave Policy" in text
    assert "20 days" in text


def test_load_text_file_missing():
    missing_file = "this_file_does_not_exist.txt"

    try:
        load_text_file(missing_file)
        assert False
    except FileNotFoundError:
        assert True


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

    assert len(chunks) == 3

    assert chunks[0].text == "First paragraph."
    assert chunks[1].text == "Second paragraph."
    assert chunks[2].text == "Third paragraph."


def test_chunk_metadata():
    text = (
        "First paragraph.\n\n"
        "Second paragraph."
    )

    chunks = chunk_text(
        text=text,
        source="policy.pdf",
        version="v2",
        chunk_size=100,
    )

    assert len(chunks) == 1

    assert chunks[0].source == "policy.pdf"
    assert chunks[0].version == "v2"
    assert chunks[0].chunk_index == 0
    assert "First paragraph." in chunks[0].text
    assert "Second paragraph." in chunks[0].text


def test_empty_text():
    chunks = chunk_text(
        text="",
        source="empty.txt",
        version="v1",
    )

    assert chunks == []


def test_invalid_chunk_size():
    try:
        chunk_text(
            text="Some text.",
            source="test.txt",
            version="v1",
            chunk_size=0,
        )
        assert False
    except ValueError:
        assert True