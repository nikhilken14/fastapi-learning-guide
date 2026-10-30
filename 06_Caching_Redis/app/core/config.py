"""
app/core/config.py
===================
Typed, environment-driven configuration. See the auth-service project's
config.py for the full rationale - same pattern, applied here.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "caching-service"
    LOG_LEVEL: str = "INFO"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    # How long a normal cached value stays valid before recomputation.
    CACHE_TTL_SECONDS: int = 30
    # Redis connection/read/write timeout, so a dead Redis fails fast
    # instead of hanging every request.
    REDIS_TIMEOUT_SECONDS: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
