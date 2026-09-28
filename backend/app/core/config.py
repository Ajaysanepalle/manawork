from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    app_name: str = "ManaWorks API"
    app_env: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg://manaworks:local-only@localhost:5432/manaworks"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:3000"
    jwt_secret: str = "local-only-change-before-deployment-32-bytes"
    session_secret: str = "local-session-only-change-before-deployment"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    auth_cookie_domain: str | None = None
    google_client_id: str = ""
    google_client_secret: str = ""
    google_callback_url: str = "http://localhost:8000/api/v1/auth/google/callback"
    admin_username: str = "ajay"
    admin_password: str = "ajay123"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_jobs_collection: str = "manaworks_jobs"
    qdrant_resumes_collection: str = "manaworks_resumes"
    qdrant_career_collection: str = "manaworks_career"
    qdrant_vector_size: int = 768
    ai_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    general_model: str = "qwen2.5:7b"
    resume_model: str = "qwen2.5:7b"
    matching_model: str = "qwen2.5:7b"
    embedding_model: str = "nomic-embed-text"

    model_config = SettingsConfigDict(env_file=_PROJECT_ENV, extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.app_env.lower() in {"uat", "prod", "production"}:
            weak_values = {
                "local-only-change-before-deployment-32-bytes",
                "local-session-only-change-before-deployment",
                "",
            }
            if self.jwt_secret in weak_values or self.session_secret in weak_values:
                raise ValueError("UAT and production require unique JWT_SECRET and SESSION_SECRET values")
            if len(self.jwt_secret) < 32 or len(self.session_secret) < 32:
                raise ValueError("UAT and production signing secrets must each contain at least 32 characters")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def secure_cookies(self) -> bool:
        return self.app_env.lower() not in {"local", "development", "test"}


@lru_cache
def get_settings() -> Settings:
    return Settings()