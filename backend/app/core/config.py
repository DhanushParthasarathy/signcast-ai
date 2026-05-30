from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url


def normalize_database_url(value: str) -> str:
    if not value:
        raise ValueError("DATABASE_URL is required")

    normalized = value.strip()
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql+psycopg://", 1)
    elif normalized.startswith("postgresql://"):
        normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        make_url(normalized)
    except Exception as exc:
        raise ValueError(f"Invalid DATABASE_URL: {exc}") from exc

    return normalized


class Settings(BaseSettings):
    app_env: str = "local"
    frontend_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./signcast.db"
    redis_url: str = "redis://localhost:6379/0"
    news_api_key: str = Field(default="", validation_alias="NEWS_API_KEY")
    openai_api_key: str = ""
    llm_provider: str = "rule_based"
    llm_model: str = "gpt-4.1-mini"
    llm_max_retries: int = 3
    llm_retry_base_delay_seconds: float = 0.5
    article_cache_ttl_seconds: int = 900
    redis_cache_ttl_seconds: int = 300
    news_refresh_interval_minutes: int = 30
    news_default_country: str = "us"
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    supabase_url: AnyHttpUrl | None = None
    supabase_service_role_key: str = ""
    supabase_sign_bucket: str = "sign-videos"
    ffmpeg_path: str = "ffmpeg"
    sequence_max_retries: int = 3
    admin_api_token: str = ""
    require_production_secrets: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        return normalize_database_url(value)

    def validate_production(self) -> None:
        if self.app_env != "production" or not self.require_production_secrets:
            return
        missing: list[str] = []
        for name in (
            "news_api_key",
            "openai_api_key",
            "supabase_service_role_key",
            "admin_api_token",
        ):
            if not getattr(self, name):
                missing.append(name.upper())
        if self.database_url.startswith("sqlite"):
            missing.append("DATABASE_URL_POSTGRES")
        if self.llm_provider != "openai":
            missing.append("LLM_PROVIDER_OPENAI")
        if missing:
            raise RuntimeError(f"Missing production configuration: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    return Settings()
