"""App settings, loaded from environment variables (see .env.example)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+asyncpg://jyotish:jyotish@localhost:5432/jyotish_guru"
    redis_url: str = "redis://localhost:6379/0"
    ai_provider: str = "none"  # claude | openai | gemini | none
    claude_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_access_token_minutes: int = 60 * 24 * 30  # 30 days

    # Fernet key for encrypting birth data at rest (DPDP). Generate with:
    # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = "ZNwkmDj4LapAt9MUyIIk6MCfBG8w_0xp4TKKqieEvPY="


@lru_cache
def get_settings() -> Settings:
    return Settings()
