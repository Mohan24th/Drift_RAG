import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.api.main import app
from app.auth.dependencies import get_current_user
from app.auth.models import User


class DummySession:

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

            def scalar_one_or_none(self):
                return None

        return Result()


@pytest.fixture
def client():

    def override_get_db():
        session = DummySession()

        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return User(
            id="test-user",
            username="test-user",
            role="EMPLOYEE",
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def employee_client():

    def override_get_db():
        session = DummySession()

        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return User(
            id="employee-1",
            username="employee",
            role="EMPLOYEE",
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():

    def override_get_db():
        session = DummySession()

        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return User(
            id="admin-1",
            username="admin",
            role="ADMIN",
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()