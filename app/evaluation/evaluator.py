from dataclasses import dataclass


@dataclass
class EvaluationResult:
    query: str
    expected_chunk: str
    retrieved_chunks: list[str]

    @property
    def hit_at_1(self) -> bool:
        if not self.retrieved_chunks:
            return False

        return self.retrieved_chunks[0] == self.expected_chunk

    @property
    def hit_at_k(self) -> bool:
        return self.expected_chunk in self.retrieved_chunks


def evaluate_retrieval(
    retriever,
    queries: list[dict],
    top_k: int = 3,
) -> list[EvaluationResult]:

    results = []

    for item in queries:
        query = item["query"]
        expected_chunk = item["expected_chunk"]

        retrieved = retriever.retrieve(
            query,
            top_k=top_k,
        )

        retrieved_ids = [
            chunk.chunk_id
            for chunk, _ in retrieved
        ]

        results.append(
            EvaluationResult(
                query=query,
                expected_chunk=expected_chunk,
                retrieved_chunks=retrieved_ids,
            )
        )

    return results