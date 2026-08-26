import numpy as np

from app.retrieval.embeddings import EmbeddingModel


class SemanticDrift:
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model

    def calculate(
        self,
        v1_text: str,
        v2_text: str,
    ) -> float:
        embeddings = self.embedding_model.encode(
            [v1_text, v2_text]
        )

        similarity = float(
            np.dot(
                embeddings[0],
                embeddings[1],
            )
        )

        return 1.0 - similarity