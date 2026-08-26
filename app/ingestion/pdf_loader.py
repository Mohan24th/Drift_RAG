from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str | Path) -> str:
    """
    Extract text from a text-based PDF.

    Returns all extracted page text as one string.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)