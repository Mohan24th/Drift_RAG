from app.database.connection import SessionLocal
from app.generation.llm import LLM
from app.generation.qa import RAGAnswerer
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():

    session = SessionLocal()

    try:
        embedding_model = EmbeddingModel()

        retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        llm = LLM()

        rag = RAGAnswerer(
            retriever=retriever,
            llm=llm,
        )

        questions = [
            "How many vacation days do employees get?",
            "When should employees request leave?",
            "Who approves leave?",
            "What is the company's remote work policy?",
        ]

        for question in questions:

            print("\n" + "=" * 60)
            print(f"QUESTION: {question}")

            response = rag.answer(
                question,
                top_k=3,
            )

            print(
                f"\nANSWER: {response.answer}"
            )

            print("\nSOURCES:")

            for source in response.sources:
                print(
                    f"- {source.document_name} "
                    f"v{source.version_number} "
                    f"chunk={source.chunk_index} "
                    f"score={source.score:.4f}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()