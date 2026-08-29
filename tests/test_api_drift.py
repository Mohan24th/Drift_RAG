from app.api.dependencies import get_drift_service
from app.api.main import app
from app.drift.report import DriftReport


DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class FakeDriftService:

    def analyze(
        self,
        document_id: str,
        v1_number: int,
        v2_number: int,
        query: str,
        top_k: int = 3,
    ):
        return DriftReport(
            query=query,
            retrieval_overlap=1.0,
            rank_change=0.2,
            semantic_change=0.07,
        )


def override_drift_service():
    return FakeDriftService()


def test_drift_document(client):
    app.dependency_overrides[
        get_drift_service
    ] = override_drift_service

    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 1,
            "to_version": 3,
            "queries": [
                "How many vacation days do employees get?",
                "When should employees request leave?",
            ],
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == DOCUMENT_ID
    assert data["from_version"] == 1
    assert data["to_version"] == 3

    assert data["queries_evaluated"] == 2

    assert len(data["reports"]) == 2

    assert data["reports"][0]["query"] == (
        "How many vacation days do employees get?"
    )


def test_drift_same_version(client):
    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 3,
            "to_version": 3,
            "queries": [
                "How many vacation days?"
            ],
            "top_k": 3,
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "from_version and to_version "
        "must be different."
    )


def test_drift_reverse_versions(client):
    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 3,
            "to_version": 1,
            "queries": [
                "How many vacation days?"
            ],
            "top_k": 3,
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "from_version must be less than "
        "to_version."
    )


def test_drift_empty_queries(client):
    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 1,
            "to_version": 3,
            "queries": [],
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_drift_invalid_top_k(client):
    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 1,
            "to_version": 3,
            "queries": [
                "How many vacation days?"
            ],
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_drift_not_found(client):
    class NotFoundDriftService:

        def analyze(
            self,
            document_id: str,
            v1_number: int,
            v2_number: int,
            query: str,
            top_k: int = 3,
        ):
            raise ValueError(
                f"Version {v2_number} not found"
            )

    def override_not_found_service():
        return NotFoundDriftService()

    app.dependency_overrides[
        get_drift_service
    ] = override_not_found_service

    response = client.post(
        f"/documents/{DOCUMENT_ID}/drift",
        json={
            "from_version": 1,
            "to_version": 99,
            "queries": [
                "How many vacation days?"
            ],
            "top_k": 3,
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Version 99 not found"
    )