from app.generation.llm import LLM
from app.generation.models import (
    RAGResponse,
    Source,
)
from app.retrieval.pg_retriever import PgRetriever


class RAGAnswerer:
    def __init__(
        self,
        retriever: PgRetriever,
        llm: LLM,
    ):
        self.retriever = retriever
        self.llm = llm

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
            )

        context_parts = []
        sources = []

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
                f"[Context {rank}]\n"
                f"{chunk.text}"
            )

            sources.append(
                Source(
                    document_name=document.name,
                    version_number=version.version_number,
                    chunk_index=chunk.chunk_index,
                    score=score,
                    text=chunk.text,
                )
            )

        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
You are a company knowledge assistant.

Answer the user's question using ONLY the
provided company context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the context does not contain enough information,
  say that you do not have enough information.
- Keep the answer concise and clear.

Company context:

{context}

User question:

{question}

Answer:
""".strip()

        answer = self.llm.generate(prompt)

        return RAGResponse(
            answer=answer,
            sources=sources,
        )