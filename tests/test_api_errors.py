from fastapi import Request

from app.api.main import unhandled_exception_handler


def test_unhandled_exception_handler():

    class FakeRequest:
        method = "GET"

        class URL:
            path = "/test"

        url = URL()

    response = __import__(
        "asyncio"
    ).run(
        unhandled_exception_handler(
            FakeRequest(),
            RuntimeError("boom"),
        )
    )

    assert response.status_code == 500

    assert response.body == (
        b'{"error":"internal_server_error",'
        b'"detail":"An unexpected error occurred."}'
    )