from pathlib import Path


def load_text_file(file_path: str | Path) -> str:
    """
    Load a UTF-8 text file and return its contents.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    return path.read_text(encoding="utf-8")