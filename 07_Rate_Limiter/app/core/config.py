"""app/core/config.py - typed, environment-driven configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "rate-limiter-service"
    LOG_LEVEL: str = "INFO"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Token bucket defaults: refill RATE_LIMIT_TOKENS every
    # RATE_LIMIT_WINDOW_SECONDS, per client. E.g. 5 tokens / 10s means a
    # sustained rate of 0.5 req/s with the ability to burst up to 5 at once.
    RATE_LIMIT_TOKENS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
