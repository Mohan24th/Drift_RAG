import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Establish project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "all-MiniLM-L6-v2",
        )
        self.embedding_device = os.getenv("EMBEDDING_DEVICE", "cpu")

        self.llm_model = os.getenv(
            "LLM_MODEL",
            "openai/gpt-oss-20b",
        )
        self.llm_fallback_model = os.getenv(
            "LLM_FALLBACK_MODEL",
            "llama-3.3-70b-versatile",
        )
        self.llm_timeout = float(os.getenv("LLM_TIMEOUT", "30.0"))
        self.llm_max_retries = int(os.getenv("LLM_MAX_RETRIES", "1"))

        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "75"))

        self.db_pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.db_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))

        self.api_host = os.getenv(
            "API_HOST",
            "127.0.0.1",
        )

        self.api_port = int(
            os.getenv(
                "API_PORT",
                "8000",
            )
        )

        self.document_storage = os.getenv(
            "DOCUMENT_STORAGE",
            "local",
        )

        self.document_storage_path = os.getenv(
            "DOCUMENT_STORAGE_PATH",
            "data/documents",
        )

        self.supabase_url = os.getenv(
            "SUPABASE_URL"
        )

        self.supabase_service_key = os.getenv(
            "SUPABASE_SERVICE_KEY"
        )

        self.supabase_storage_bucket = os.getenv(
            "SUPABASE_STORAGE_BUCKET",
            "drift-rag-documents",
        )

        self.cors_origins = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000",
            ).split(",")
            if origin.strip()
        ]

        self.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY"
        )
        
        self.prompt_path = PROJECT_ROOT / "prompts" / "rag_system_prompt.txt"

        if not self.jwt_secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY is not set"
            )

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set"
            )

        if not self.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set"
            )

        if self.document_storage == "supabase":
            if not self.supabase_url:
                raise RuntimeError(
                    "SUPABASE_URL is required "
                    "when DOCUMENT_STORAGE=supabase"
                )

            if not self.supabase_service_key:
                raise RuntimeError(
                    "SUPABASE_SERVICE_KEY is required "
                    "when DOCUMENT_STORAGE=supabase"
                )

settings = Settings()
