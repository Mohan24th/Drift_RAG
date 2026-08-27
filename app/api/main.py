from fastapi import FastAPI

from app.api.routes import (
    documents,
    query,
    drift,
)


app = FastAPI(
    title="Drift RAG API",
    description=(
        "Version-aware document RAG "
        "and knowledge drift detection API."
    ),
    version="1.0.0",
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