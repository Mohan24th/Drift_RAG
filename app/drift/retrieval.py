from app.retrieval.pg_retriever import PgRetriever


class DriftRetriever:
    """
    Retrieves chunks for a specific document version.
    """

    def __init__(
        self,
        retriever: PgRetriever,
    ):
        self.retriever = retriever

    def retrieve(
        self,
        query: str,
        version_id: str,
        top_k: int = 3,
    ):
        results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            version_id=version_id,
        )

        return [
            (chunk, score)
            for (
                chunk,
                version,
                document,
                score,
            ) in results
        ]