from collections.abc import Generator

from app.database.connection import SessionLocal


def get_db() -> Generator:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()