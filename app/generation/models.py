from dataclasses import dataclass


@dataclass
class Source:
    document_name: str
    version_number: int
    chunk_index: int
    score: float
    text: str


@dataclass
class RAGResponse:
    answer: str
    sources: list[Source]