import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "all-MiniLM-L6-v2",
        )

        self.llm_model = os.getenv(
            "LLM_MODEL",
            "openai/gpt-oss-20b",
        )

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set"
            )

        if not self.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set"
            )


settings = Settings()