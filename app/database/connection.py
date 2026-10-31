from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

DATABASE_URL = settings.database_url

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set"
    )

# SQLAlchemy must use the Psycopg 3 driver.
if DATABASE_URL.startswith(
    "postgresql://"
):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
