from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Project Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | production

    # ── Server ─────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ── Database ───────────────────────────────────────────────────────────
    # SQLite for dev, PostgreSQL for prod
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_project_gen.db"
    # Example prod: postgresql+asyncpg://user:pass@localhost:5432/ai_proj

    # ── Redis / Celery ─────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── Auth ───────────────────────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_SECRETS_TOOL"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── LLM Provider ───────────────────────────────────────────────────────
    LLM_PROVIDER: str = "gemini"       # gemini | openai | anthropic
    LLM_MODEL: str = "gemini-1.5-pro"  # model name for the chosen provider

    # Google Gemini
    GEMINI_API_KEY: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # ── Dataset APIs ───────────────────────────────────────────────────────
    KAGGLE_USERNAME: Optional[str] = None
    KAGGLE_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None

    # ── Storage ────────────────────────────────────────────────────────────
    GENERATED_FILES_DIR: str = "./generated_projects"
    MAX_FILE_SIZE_MB: int = 50

    # ── Rate Limiting ──────────────────────────────────────────────────────
    RATE_LIMIT_FREE: str = "5/minute"
    RATE_LIMIT_PRO: str = "30/minute"

    # ── Admin ──────────────────────────────────────────────────────────────
    ADMIN_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
