from io import BytesIO

from app.api.main import app
from app.api.routes import documents


DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class FakeDocument:
    id = DOCUMENT_ID
    name = "Test Policy"


class FakeVersion:
    id = "version-123"
    version_number = 5
    status = "DRAFT"
    chunks = []


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
        return FakeResult(
            FakeDocument()
        )


class FakeRepository:
    def __init__(self, session):
        self.session = session

    def get_document_by_name(self, name):
        return None

    def create_document(self, document):
        return document

    def get_document_by_id(self, document_id):
        if document_id == DOCUMENT_ID:
            return FakeDocument()

        return None

    def get_next_version_number(self, document_id):
        return 5

    def get_version(
        self,
        document_id,
        version_number,
    ):
        if (
            document_id == DOCUMENT_ID
            and version_number == 5
        ):
            return FakeVersion()

        return None


class DuplicateRepository(FakeRepository):
    def get_document_by_name(self, name):
        return FakeDocument()


def test_create_document(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = client.post(
        "/documents/",
        json={
            "name": "New Policy",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "New Policy"
    assert "id" in data


def test_create_duplicate_document(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        DuplicateRepository,
    )

    response = client.post(
        "/documents/",
        json={
            "name": "Test Policy",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A document with this name already exists."
    )


def test_upload_unsupported_file(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.post(
        f"/documents/{DOCUMENT_ID}/versions",
        files={
            "file": (
                "test.exe",
                BytesIO(b"fake file"),
                "application/octet-stream",
            )
        },
        data={
            "version_number": "5",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only PDF and TXT files are supported."
    )


def test_upload_empty_file(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = admin_client.post(
        f"/documents/{DOCUMENT_ID}/versions",
        files={
            "file": (
                "empty.pdf",
                BytesIO(b""),
                "application/pdf",
            )
        },
        data={
            "version_number": "5",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Uploaded file is empty."
    )


def test_upload_forbidden_for_employee(
    employee_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/versions",
        files={
            "file": (
                "policy.pdf",
                BytesIO(b"fake pdf"),
                "application/pdf",
            )
        },
        data={
            "version_number": "5",
        },
    )

    assert response.status_code == 403


def test_approve_version_forbidden_for_employee(
    employee_client,
    monkeypatch,
):
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        FakeRepository,
    )

    response = employee_client.post(
        f"/documents/{DOCUMENT_ID}/versions/5/approve"
    )

    assert response.status_code == 403


def test_approve_version_not_found(
    admin_client,
    monkeypatch,
):
    class VersionNotFoundRepository(
        FakeRepository
    ):
        def get_version(
            self,
            document_id,
            version_number,
        ):
            return None

    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        VersionNotFoundRepository,
    )

    response = admin_client.post(
        f"/documents/{DOCUMENT_ID}/versions/99/approve"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Version v99 not found."
    )