from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.document_service import DocumentService
from app.database.repositories.documents import DocumentRepository
from app.drift.analyzer import DriftAnalyzer
from app.drift.retrieval import DriftRetriever
from app.drift.semantic import SemanticDrift
from app.drift.service import DriftService
from app.drift.version_loader import VersionLoader
from app.generation.llm import LLM
from app.generation.qa import RAGAnswerer
from app.generation.service import RAGService
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()


def get_document_service(
    session: Session = Depends(get_db),
    embedding_model: EmbeddingModel = Depends(
        get_embedding_model
    ),
) -> DocumentService:

    return DocumentService(
        repository=DocumentRepository(
            session=session
        ),
        ingestion_service=IngestionService(),
        embedding_model=embedding_model,
        session=session,
    )


def get_rag_service(
    session: Session = Depends(get_db),
    embedding_model: EmbeddingModel = Depends(
        get_embedding_model
    ),
    document_service: DocumentService = Depends(
        get_document_service
    ),
) -> RAGService:

    retriever = PgRetriever(
        session=session,
        embedding_model=embedding_model,
    )

    answerer = RAGAnswerer(
        retriever=retriever,
        llm=LLM(),
    )

    return RAGService(
        document_service=document_service,
        answerer=answerer,
    )


def get_drift_service(
    session: Session = Depends(get_db),
    embedding_model: EmbeddingModel = Depends(
        get_embedding_model
    ),
) -> DriftService:

    retriever = PgRetriever(
        session=session,
        embedding_model=embedding_model,
    )

    drift_retriever = DriftRetriever(
        retriever=retriever,
    )

    version_loader = VersionLoader(
        session=session,
    )

    analyzer = DriftAnalyzer(
        semantic_detector=SemanticDrift(
            embedding_model=embedding_model,
        ),
    )

    return DriftService(
        version_loader=version_loader,
        drift_retriever=drift_retriever,
        analyzer=analyzer,
    )