from datetime import datetime

from app.api.main import app
from app.api.routes import documents


DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class FakeDocument:
    id = DOCUMENT_ID
    name = "Leave Policy"
    created_at = datetime(
        2026,
        8,
        30,
    )


class FakeVersion:
    id = "version-1"
    version_number = 4
    status = "APPROVED"
    file_path = (
        f"{DOCUMENT_ID}/v4/company_policy_4.pdf"
    )
    created_at = datetime(
        2026,
        8,
        30,
    )
    approved_at = datetime(
        2026,
        8,
        30,
    )


class FakeRepository:

    def __init__(self, session):
        self.session = session

    def get_documents(self):
        return [
            FakeDocument()
        ]

    def get_document_by_id(
        self,
        document_id,
    ):
        if document_id == DOCUMENT_ID:
            return FakeDocument()

        return None

    def get_versions(
        self,
        document_id,
    ):
        if document_id == DOCUMENT_ID:
            return [
                FakeVersion()
            ]

        return []

    def get_document_by_name(self, name):
        return None

    def create_document(self, document):
        return document


def test_list_documents(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.get(
        "/documents/"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == DOCUMENT_ID
    assert data[0]["name"] == "Leave Policy"


def test_get_document(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.get(
        f"/documents/{DOCUMENT_ID}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == DOCUMENT_ID
    assert data["name"] == "Leave Policy"
    assert data["versions_count"] == 1


def test_get_document_versions(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.get(
        f"/documents/{DOCUMENT_ID}/versions"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["version_number"] == 4
    assert data[0]["status"] == "APPROVED"


def test_list_documents_forbidden(
    employee_client,
):
    response = employee_client.get(
        "/documents/"
    )

    assert response.status_code == 403


def test_get_document_forbidden(
    employee_client,
):
    response = employee_client.get(
        f"/documents/{DOCUMENT_ID}"
    )

    assert response.status_code == 403


def test_get_versions_forbidden(
    employee_client,
):
    response = employee_client.get(
        f"/documents/{DOCUMENT_ID}/versions"
    )

    assert response.status_code == 403


def test_get_document_not_found(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.get(
        "/documents/nonexistent"
    )

    assert response.status_code == 404