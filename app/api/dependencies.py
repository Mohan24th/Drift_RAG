from collections.abc import Generator
from fastapi import Depends, Request
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
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.pg_retriever import PgRetriever

def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_embedding_model(request: Request) -> EmbeddingModel:
    # Pull the pre-loaded model from application state
    return request.app.state.embedding_model

def get_llm(request: Request) -> LLM:
    # Pull the pre-loaded LLM client from application state
    return request.app.state.llm

def get_document_service(
    request: Request,
    session: Session = Depends(get_db),
) -> DocumentService:
    embedding_model = get_embedding_model(request)
    
    return DocumentService(
        repository=DocumentRepository(
            session=session
        ),
        ingestion_service=IngestionService(),
        embedding_model=embedding_model,
        session=session,
    )

def get_rag_service(
    request: Request,
    session: Session = Depends(get_db),
) -> RAGService:
    embedding_model = get_embedding_model(request)
    llm = get_llm(request)
    
    vector_retriever = PgRetriever(
        session=session,
        embedding_model=embedding_model,
    )
    retriever = HybridRetriever(vector_retriever)

    answerer = RAGAnswerer(
        retriever=retriever,
        llm=llm,
    )

    return RAGService(
        document_service=Depends(get_document_service),
        answerer=answerer,
    )

def get_drift_service(
    request: Request,
    session: Session = Depends(get_db),
) -> DriftService:
    embedding_model = get_embedding_model(request)
    
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
