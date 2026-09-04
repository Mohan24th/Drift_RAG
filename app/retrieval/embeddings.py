from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingModel:
    def __init__(
        self,
        model_name: str | None = None,
    ):
        self.model = SentenceTransformer(
            model_name
            or settings.embedding_model,
            device="cpu",
        )

    def encode(
        self,
        texts: list[str],
    ):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )