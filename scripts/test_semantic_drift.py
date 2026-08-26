from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text
from app.retrieval.embeddings import EmbeddingModel
from app.drift.semantic import SemanticDrift


def main():
    source = "company_policy.txt"

    v1_text = load_text_file(
        f"data/v1/{source}"
    )

    v2_text = load_text_file(
        f"data/v2/{source}"
    )

    v1_chunks = chunk_text(
        text=v1_text,
        source=source,
        version="v1",
        chunk_size=100,
    )

    v2_chunks = chunk_text(
        text=v2_text,
        source=source,
        version="v2",
        chunk_size=100,
    )

    embedding_model = EmbeddingModel()

    detector = SemanticDrift(
        embedding_model
    )

    v1_chunk = v1_chunks[0]
    v2_chunk = v2_chunks[0]

    drift = detector.calculate(
        v1_chunk.text,
        v2_chunk.text,
    )

    print("V1:")
    print(v1_chunk.text)

    print("\nV2:")
    print(v2_chunk.text)

    print(f"\nSemantic change: {drift:.4f}")


if __name__ == "__main__":
    main()