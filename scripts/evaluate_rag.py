import json

from app.database.connection import SessionLocal
from app.generation.llm import LLM
from app.generation.qa import RAGAnswerer
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def main():
    with open("data/rag_evaluation.json", "r") as file:
        cases = json.load(file)

    session = SessionLocal()

    try:
        embedding_model = EmbeddingModel()

        retriever = PgRetriever(
            session=session,
            embedding_model=embedding_model,
        )

        rag = RAGAnswerer(
            retriever=retriever,
            llm=LLM(),
        )

        passed = 0

        print("\n=== RAG Evaluation ===\n")

        for case in cases:
            question = case["question"]

            response = rag.answer(
                question,
                top_k=3,
            )

            answer = response.answer.lower()

            expected_terms = [
                term.lower()
                for term in case[
                    "expected_answer_contains"
                ]
            ]

            success = any(
                term in answer
                for term in expected_terms
            )

            if success:
                passed += 1

            print(f"Question: {question}")
            print(f"Answer: {response.answer}")
            print(f"Pass: {success}")
            print()

        total = len(cases)

        print("=== Summary ===")
        print(f"Cases: {total}")
        print(f"Passed: {passed}/{total}")

    finally:
        session.close()


if __name__ == "__main__":
    main()