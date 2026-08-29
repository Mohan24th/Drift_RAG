from io import BytesIO

from app.api.main import app
from app.api.dependencies import get_db
from app.api.routes import documents

DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class FakeDocument:
    id = DOCUMENT_ID
    name = "Test Policy"


class FakeVersion:
    id = "version-123"
    version_number = 4


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    def flush(self):
        pass

    def execute(self, statement):
        class Result:
            def scalar_one_or_none(self):
                return FakeDocument()
        return Result()


class FakeRepository:
    def __init__(self, session):
        self.session = session

    def get_document_by_name(self, name):
        return None

    def create_document(self, document):
        return document

    def get_next_version_number(self, document_id):
        return 5

    # ----- FIX: add this method -----
    def get_document_by_id(self, document_id):
        # Return a FakeDocument so the endpoint thinks the document exists
        return FakeDocument()


def override_get_db():
    session = FakeSession()
    try:
        yield session
    finally:
        session.close()


def test_create_document(client, monkeypatch):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = client.post(
        "/documents/",
        json={"name": "New Policy"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Policy"
    assert "id" in data


def test_create_duplicate_document(client, monkeypatch):
    class DuplicateRepository(FakeRepository):
        def get_document_by_name(self, name):
            return FakeDocument()

    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        DuplicateRepository,
    )

    response = client.post(
        "/documents/",
        json={"name": "Test Policy"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A document with this name already exists."
    )


def test_upload_unsupported_file(client, monkeypatch):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = client.post(
        f"/documents/{DOCUMENT_ID}/versions",
        files={
            "file": (
                "test.exe",
                BytesIO(b"fake file"),
                "application/octet-stream",
            )
        },
        data={"version_number": "5"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only PDF and TXT files are supported."
    )


def test_upload_empty_file(client, monkeypatch):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = client.post(
        f"/documents/{DOCUMENT_ID}/versions",
        files={
            "file": (
                "empty.pdf",
                BytesIO(b""),
                "application/pdf",
            )
        },
        data={"version_number": "5"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded file is empty."
    )