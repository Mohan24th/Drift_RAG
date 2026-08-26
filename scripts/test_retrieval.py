from app.ingestion.loader import load_text_file
from app.ingestion.chunker import chunk_text
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.retriever import Retriever


def main():
    source = "company_policy.txt"
    version = "v1"

    text = load_text_file(f"data/{version}/{source}")

    chunks = chunk_text(
        text=text,
        source=source,
        version=version,
        chunk_size=100,
    )

    print(f"Loaded {len(chunks)} chunks")

    embedding_model = EmbeddingModel()

    retriever = Retriever(embedding_model)
    retriever.build_index(chunks)

    queries = [
        "How many vacation days do employees get?",
        "When should employees request leave?",
        "Who approves leave?",
    ]

    for query in queries:
        print(f"\nQUERY: {query}")

        results = retriever.retrieve(
            query,
            top_k=3,
        )

        for rank, (chunk, score) in enumerate(results, start=1):
            print(
                f"\n{rank}. "
                f"[{chunk.chunk_id}] "
                f"score={score:.4f}"
            )
            print(chunk.text)


if __name__ == "__main__":
    main()