from app.database.document_service import DocumentService
from app.generation.models import RAGResponse
from app.generation.qa import RAGAnswerer


class RAGService:
    def __init__(
        self,
        document_service: DocumentService,
        answerer: RAGAnswerer,
    ):
        self.document_service = document_service
        self.answerer = answerer

    def answer(
        self,
        document_id: str,
        question: str,
        top_k: int = 3,
    ) -> RAGResponse:

        self.document_service.get_document(
            document_id
        )

        latest_approved_version = (
            self.document_service.get_latest_approved_version(
                document_id
            )
        )

        return self.answerer.answer(
            question=question,
            version_id=latest_approved_version.id,
            top_k=top_k,
        )