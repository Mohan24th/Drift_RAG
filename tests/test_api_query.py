from app.api.dependencies import get_rag_service
from app.api.main import app
from app.generation.models import RAGResponse, Source


DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class FakeRAGService:

    def answer(
        self,
        document_id: str,
        question: str,
        top_k: int = 3,
    ):
        return RAGResponse(
            answer="Employees receive 30 days of annual leave.",
            sources=[
                Source(
                    document_name="Test Policy",
                    version_number=3,
                    chunk_index=0,
                    score=0.65,
                    text=(
                        "Employees receive 30 days "
                        "of annual leave."
                    ),
                )
            ],
        )


def override_rag_service():
    return FakeRAGService()


def test_query_document(employee_client):
    app.dependency_overrides[
        get_rag_service
    ] = override_rag_service

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/query",
        json={
            "question": "How many vacation days do employees get?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Employees receive 30 days of annual leave."
    )

    assert len(data["sources"]) == 1

    assert data["sources"][0]["document_name"] == (
        "Test Policy"
    )

    assert data["sources"][0]["version_number"] == 3

    assert data["sources"][0]["chunk_index"] == 0


def test_query_document_not_found(employee_client):
    class NotFoundRAGService:

        def answer(
            self,
            document_id: str,
            question: str,
            top_k: int = 3,
        ):
            raise ValueError(
                f"Document not found: {document_id}"
            )

    def override_not_found_service():
        return NotFoundRAGService()

    app.dependency_overrides[
        get_rag_service
    ] = override_not_found_service

    response = employee_client.post(
        "/documents/nonexistent/query",
        json={
            "question": "How many vacation days?",
            "top_k": 3,
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Document not found: nonexistent"
    )


def test_query_empty_question(employee_client):
    app.dependency_overrides[
        get_rag_service
    ] = override_rag_service

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/query",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_query_invalid_top_k(employee_client):
    app.dependency_overrides[
        get_rag_service
    ] = override_rag_service

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/query",
        json={
            "question": "How many vacation days?",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_query_top_k_too_large(employee_client):
    app.dependency_overrides[
        get_rag_service
    ] = override_rag_service

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/query",
        json={
            "question": "How many vacation days?",
            "top_k": 11,
        },
    )

    assert response.status_code == 422