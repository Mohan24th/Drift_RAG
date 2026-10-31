from dataclasses import dataclass
from app.config import settings

@dataclass
class Chunk:
    """
    A document chunk with metadata for retrieval
    and version-drift analysis.
    """
    chunk_id: str
    text: str
    source: str
    version: str
    chunk_index: int

def _find_chunk_end(
    text: str,
    start: int,
    chunk_size: int,
) -> int:
    """
    Find a chunk boundary near chunk_size.
    """
    target = min(start + chunk_size, len(text))

    if target == len(text):
        return target

    minimum = start + int(chunk_size * 0.60)
    segment = text[minimum:target]

    separators = ["\n\n", "\n", ". ", "? ", "! ", " "]

    candidates = []

    for separator in separators:
        position = segment.rfind(separator)
        if position >= 0:
            boundary = minimum + position + len(separator)
            candidates.append(boundary)

    if candidates:
        return max(candidates)

    return target

def chunk_text(
    text: str,
    source: str,
    version: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    Split text into overlapping chunks.
    """
    # Use system defaults if no override provided
    actual_chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    actual_overlap = overlap if overlap is not None else settings.chunk_overlap

    if actual_chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if actual_overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if actual_overlap >= actual_chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0

    while start < len(text):
        end = _find_chunk_end(text, start, actual_chunk_size)
        chunk_content = text[start:end].strip()

        if chunk_content:
            chunk_index = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=f"{source}-{chunk_index}",
                    text=chunk_content,
                    source=source,
                    version=version,
                    chunk_index=chunk_index,
                )
            )

        if end >= len(text):
            break

        next_start = max(start + 1, end - actual_overlap)
        while next_start < end and text[next_start].isspace():
            next_start += 1

        start = next_start

    return chunks
