from dataclasses import dataclass


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


def chunk_text(
    text: str,
    source: str,
    version: str,
    chunk_size: int = 500,
) -> list[Chunk]:
    """
    Split a document into paragraph-aware chunks.

    Paragraphs are kept together whenever possible.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks: list[Chunk] = []
    current_parts: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if (
            current_parts
            and current_length + paragraph_length + 2 > chunk_size
        ):
            chunk_text_value = "\n\n".join(current_parts)

            chunk_index = len(chunks)

            chunks.append(
                Chunk(
                    chunk_id=f"{version}-{chunk_index}",
                    text=chunk_text_value,
                    source=source,
                    version=version,
                    chunk_index=chunk_index,
                )
            )

            current_parts = []
            current_length = 0

        current_parts.append(paragraph)
        current_length += paragraph_length + 2

    if current_parts:
        chunk_text_value = "\n\n".join(current_parts)
        chunk_index = len(chunks)

        chunks.append(
            Chunk(
                chunk_id=f"{version}-{chunk_index}",
                text=chunk_text_value,
                source=source,
                version=version,
                chunk_index=chunk_index,
            )
        )

    return chunks