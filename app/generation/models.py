from dataclasses import dataclass

@dataclass
class Source:
    document_name: str
    version_number: int
    chunk_index: int
    score: float | None
    text: str
    rrf_score: float | None = None

@dataclass
class RAGResponse:
    answer: str
    sources: list[Source]
    model_used: str | None = None
