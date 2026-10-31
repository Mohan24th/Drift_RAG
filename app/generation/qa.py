import re
import logging
from pathlib import Path
from app.generation.llm import LLM
from app.generation.models import (
    RAGResponse,
    Source,
)
from app.retrieval.pg_retriever import PgRetriever
from app.config import settings

logger = logging.getLogger(__name__)

class RAGAnswerer:
    def __init__(
        self,
        retriever: PgRetriever,
        llm: LLM,
    ):
        self.retriever = retriever
        self.llm = llm
        # Token estimation constant (approx 4 chars per token for Llama-3/Groq models)
        self.CHARS_PER_TOKEN = 4
        # Model context window limit (conservative estimate for Llama-3-70b / Groq)
        self.MAX_CONTEXT_TOKENS = 8192
        self.OUTPUT_RESERVE_TOKENS = 1024

    def _load_prompt_template(self) -> str:
        prompt_path = settings.prompt_path
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _estimate_tokens(self, text: str) -> int:
        """Approximate token count based on characters."""
        return len(text) // self.CHARS_PER_TOKEN

    def _validate_citations(self, answer: str, provided_indices: list[int]) -> list[str]:
        """Detect citation identifiers [X] not present in the supplied context."""
        found_citations = re.findall(r"\[(\d+)\]", answer)
        invalid_citations = []
        for cit in found_citations:
            if int(cit) not in provided_indices:
                invalid_citations.append(f"[{cit}]")
        return invalid_citations

    def answer(
        self,
        question: str,
        version_id: str,
        top_k: int = 3,
    ) -> RAGResponse:

        results = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            version_id=version_id,
        )

        if not results:
            return RAGResponse(
                answer=(
                    "I don't have enough information "
                    "to answer that question."
                ),
                sources=[],
                model_used=None
            )

        # 1. Context construction with stable identifiers
        context_parts = []
        sources = []
        
        # we track which chunks actually make it into the prompt
        included_indices = []

        for rank, (
            chunk,
            version,
            document,
            score,
        ) in enumerate(
            results,
            start=1,
        ):
            context_parts.append(
                f"[Context {rank}]\n{chunk.text}"
            )

            sources.append(
                Source(
                    document_name=document.name,
                    version_number=version.version_number,
                    chunk_index=chunk.chunk_index,
                    score=score,
                    text=chunk.text,
                    rrf_score=getattr(chunk, "rrf_score", None),
                )
            )
            included_indices.append(rank)

        context = "\n\n".join(context_parts)
        prompt_template = self._load_prompt_template()
        
        # 2. Token Budget Enforcement
        system_prompt_est = self._estimate_tokens(prompt_template)
        question_est = self._estimate_tokens(question)
        
        overhead = system_prompt_est + question_est + self.OUTPUT_RESERVE_TOKENS
        if overhead > self.MAX_CONTEXT_TOKENS:
            logger.error("Impossible budget: Overhead exceeds model context window.")
            return RAGResponse(
                answer=(
                    "I don't have enough information "
                    "to answer that question."
                ),
                sources=[],
                model_used=None
            )
        
        available_tokens = self.MAX_CONTEXT_TOKENS - overhead
        
        current_context_est = self._estimate_tokens(context)
        
        if current_context_est > available_tokens:
            logger.warning("Context overflow detected. Truncating least relevant chunks.")
            while len(context_parts) > 0 and self._estimate_tokens("\n\n".join(context_parts)) > available_tokens:
                context_parts.pop()
                sources.pop() 
                included_indices.pop()
            
            context = "\n\n".join(context_parts)

        if not context_parts:
            return RAGResponse(
                answer=(
                    "I don't have enough information "
                    "to answer that question."
                ),
                sources=[],
                model_used=None
            )

        prompt = prompt_template.format(
            context=context,
            question=question
        )

        answer, model_used = self.llm.generate(prompt)

        # 3. Citation Validation
        invalid_cits = self._validate_citations(answer, included_indices)
        if invalid_cits:
            logger.warning("LLM invented citations: %s", invalid_cits)

        return RAGResponse(
            answer=answer,
            sources=sources,
            model_used=model_used
        )
