"""app/limiter/redis_client.py - shared Redis connection pool."""

import redis

from app.core.config import get_settings

settings = get_settings()

_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)
