import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import (
    documents,
    drift,
    query,
)
from app.config import settings


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("drift-rag")


app = FastAPI(
    title="Drift RAG API",
    description=(
        "Version-aware document RAG "
        "and knowledge drift detection API."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "detail": "An unexpected error occurred.",
        },
    )


app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

app.include_router(
    query.router,
    prefix="/documents",
    tags=["Query"],
)

app.include_router(
    drift.router,
    prefix="/documents",
    tags=["Drift"],
)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
        "service": "drift-rag",
    }


@app.get(
    "/ready",
    tags=["Health"],
)
def readiness_check():

    try:
        from sqlalchemy import text

        from app.database.connection import engine

        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "ready",
            "service": "drift-rag",
            "database": "ok",
        }

    except Exception:
        logger.exception(
            "Readiness check failed"
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "drift-rag",
                "database": "unavailable",
            },
        )