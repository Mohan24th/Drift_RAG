from app.database.connection import SessionLocal
from app.database.document_service import DocumentService
from app.database.repositories.documents import (
    DocumentRepository,
)
from app.generation.llm import LLM
from app.generation.qa import RAGAnswerer
from app.generation.service import RAGService
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():
    session = SessionLocal()

    try:
        # Shared dependencies
        embedding_model = EmbeddingModel()

        # Database repository
        repository = DocumentRepository(
            session=session,
        )

        # Document service
        document_service = DocumentService(
            repository=repository,
            ingestion_service=IngestionService(),
            embedding_model=embedding_model,
            session=session,
        )

        # PostgreSQL retriever
        retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        # LLM
        llm = LLM()

        # Low-level RAG answerer
        answerer = RAGAnswerer(
            retriever=retriever,
            llm=llm,
        )

        # Application-level RAG service
        rag_service = RAGService(
            document_service=document_service,
            answerer=answerer,
        )

        # Existing Leave Policy document
        document = repository.get_document_by_name(
            "Leave Policy"
        )

        if document is None:
            raise ValueError(
                "Leave Policy document not found"
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

            response = rag_service.answer(
                document_id=document.id,
                question=question,
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