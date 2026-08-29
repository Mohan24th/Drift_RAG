import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.api.main import app


DOCUMENT_ID = "647e4ef2-d359-4a93-8a27-f4bece148ee1"


class DummySession:

    def __init__(self, document=None):
        self.document = document

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def flush(self):
        pass

    def execute(self, statement):

        class Result:
            def __init__(self, document):
                self.document = document

            def scalar_one_or_none(self):
                return self.document

        return Result(self.document)


@pytest.fixture
def client():

    def override_get_db():
        session = DummySession()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()