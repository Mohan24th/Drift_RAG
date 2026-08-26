from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel


def main():
    embedding_model = EmbeddingModel()

    pipeline = IngestionPipeline(
        ingestion_service=IngestionService(),
        embedding_model=embedding_model,
    )

    retriever = pipeline.process(
        file_path="data/test_documents/company_policy.pdf",
        source="company_policy.pdf",
        version="v1",
        chunk_size=100,
    )

    queries = [
        "How many vacation days do employees get?",
        "When should employees request leave?",
        "Who approves leave?",
    ]

    for query in queries:

        print(f"\nQUERY: {query}")

        results = retriever.retrieve(
            query,
            top_k=2,
        )

        for rank, (chunk, score) in enumerate(
            results,
            start=1,
        ):
            print(
                f"\n{rank}. "
                f"{chunk.chunk_id} "
                f"score={score:.4f}"
            )

            print(chunk.text)


if __name__ == "__main__":
    main()