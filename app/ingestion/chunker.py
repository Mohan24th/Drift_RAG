from dataclasses import dataclass
import re


@dataclass
class Chunk:
    """
    A piece of a document along with metadata
    needed later for retrieval and drift analysis.
    """

    chunk_id: str
    text: str
    source: str
    version: str
    chunk_index: int


def _split_long_paragraph(
    paragraph: str,
    chunk_size: int,
) -> list[str]:
    """
    Split a paragraph into smaller pieces.

    Sentences are kept together whenever possible.
    Very long sentences are hard-split as a last resort.
    """

    if len(paragraph) <= chunk_size:
        return [paragraph]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        paragraph,
    )

    pieces: list[str] = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if len(sentence) > chunk_size:
            if current:
                pieces.append(current)
                current = ""

            for start in range(
                0,
                len(sentence),
                chunk_size,
            ):
                pieces.append(
                    sentence[start:start + chunk_size]
                )

            continue

        candidate = (
            f"{current} {sentence}"
            if current
            else sentence
        )

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                pieces.append(current)

            current = sentence

    if current:
        pieces.append(current)

    return pieces


def chunk_text(
    text: str,
    source: str,
    version: str,
    chunk_size: int = 100,
) -> list[Chunk]:
    """
    Split document text into retrieval-friendly chunks.

    Strategy:
    - Preserve paragraphs when possible.
    - Combine small paragraphs until chunk_size is reached.
    - Split oversized paragraphs by sentence.
    - Hard-split oversized sentences as a last resort.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            text,
        )
        if paragraph.strip()
    ]

    pieces: list[str] = []

    for paragraph in paragraphs:
        pieces.extend(
            _split_long_paragraph(
                paragraph,
                chunk_size,
            )
        )

    chunks: list[Chunk] = []

    current_parts: list[str] = []
    current_length = 0

    for piece in pieces:
        piece_length = len(piece)

        if (
            current_parts
            and current_length + piece_length + 2
            > chunk_size
        ):
            chunk_index = len(chunks)

            chunks.append(
                Chunk(
                    chunk_id=f"{source}-{chunk_index}",
                    text="\n\n".join(current_parts),
                    source=source,
                    version=version,
                    chunk_index=chunk_index,
                )
            )

            current_parts = []
            current_length = 0

        current_parts.append(piece)
        current_length += piece_length + 2

    if current_parts:
        chunk_index = len(chunks)

        chunks.append(
            Chunk(
                chunk_id=f"{source}-{chunk_index}",
                text="\n\n".join(current_parts),
                source=source,
                version=version,
                chunk_index=chunk_index,
            )
        )

    return chunks