from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = Field(default="development")
    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    secret_key: str = Field(default="change-me-in-production")

    database_url: str = Field(default="sqlite:///./data/lara.db")
    storage_root: str = Field(default="./storage")
    documents_root: str = Field(default="./storage/documents")
    max_upload_mb: int = Field(default=100)

    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_default_model: str = Field(default="qwen2.5:3b-instruct")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")

    embedding_model: str = Field(default="nomic-embed-text")
    retrieval_top_k: int = Field(default=5)
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=120)

    ocr_enabled: bool = Field(default=True)
    ocr_language: str = Field(default="eng+ara")

    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_database_url(self) -> str:
        url = self.database_url
        if url.startswith("sqlite:///./"):
            rel = url.replace("sqlite:///./", "")
            abs_path = (BASE_DIR / rel).resolve()
            return f"sqlite:///{abs_path.as_posix()}"
        return url

    @property
    def resolved_storage_root(self) -> Path:
        p = Path(self.storage_root)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def resolved_documents_root(self) -> Path:
        p = Path(self.documents_root)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def project_root(self) -> Path:
        """Project root directory."""
        return BASE_DIR


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()