"""App settings, loaded from environment variables (see .env.example)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+asyncpg://jyotish:jyotish@localhost:5432/jyotish_guru"
    redis_url: str = "redis://localhost:6379/0"
    ai_provider: str = "none"  # claude | openai | gemini | none
    jwt_secret: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
