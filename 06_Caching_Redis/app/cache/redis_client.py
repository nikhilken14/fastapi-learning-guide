"""
app/cache/redis_client.py
==========================
Shared Redis connection pool + a couple of production-hardening choices
that the "simple" version skipped:

1. **Connection pooling**: `redis.ConnectionPool` is created once and
   shared across the whole app, instead of opening a new TCP connection
   per request - this is what actually makes Redis usage fast at scale.

2. **Timeouts**: without `socket_timeout`, a Redis server that hangs
   (network partition, overloaded box) would make every request that
   touches the cache hang too. A short timeout turns "Redis is stuck"
   into "this one cache lookup failed fast", which the decorator in
   app/cache/decorators.py then treats as a cache miss.

3. **Graceful degradation**: if Redis is down entirely, this service
   keeps working (just slower, since every request falls through to
   the real data source) instead of returning 500s to every client.
   Caching should make things faster, not become a single point of failure.
"""

import logging

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# One pool, shared for the lifetime of the process.
_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
    socket_timeout=settings.REDIS_TIMEOUT_SECONDS,
    socket_connect_timeout=settings.REDIS_TIMEOUT_SECONDS,
)


def get_redis() -> redis.Redis:
    """Return a Redis client bound to the shared connection pool.

    Cheap to call repeatedly - it does NOT open a new connection, it
    just borrows one from the pool for the duration of each command.
    """
    return redis.Redis(connection_pool=_pool)


def is_redis_healthy() -> bool:
    """Used by the /health endpoint to report cache availability.

    Never raises - a health check that itself can crash the health
    endpoint defeats the purpose.
    """
    try:
        get_redis().ping()
        return True
    except redis.RedisError as exc:
        logger.warning("Redis health check failed", extra={"error": str(exc)})
        return False
