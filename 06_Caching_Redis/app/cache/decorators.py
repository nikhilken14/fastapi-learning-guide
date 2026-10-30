"""
app/cache/decorators.py
========================
A generic `@cached(...)` decorator that turns "fetch the cache, else
compute and store" into one line on any function - instead of hand
writing that logic inline every time you want to cache something (as
the simple version did).

Also demonstrates the pattern of DEGRADING GRACEFULLY: any Redis error
here is caught and logged, then treated as a cache miss - the real
function still runs and the caller still gets a correct answer, just
without the speed-up. A caching layer failing should never turn into
the whole feature failing.
"""

import contextvars
import functools
import json
import logging
from collections.abc import Callable

import redis

from app.cache.redis_client import get_redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Tracks whether the most recent @cached call was served from Redis or
# had to fall through to the real function, purely so routes can report
# it (e.g. as an `X-Cache-Status` response header) for observability.
# A contextvar (rather than a plain global) keeps this correct even
# under concurrent requests, since each request gets its own context.
_last_cache_status: contextvars.ContextVar[str] = contextvars.ContextVar("last_cache_status", default="unknown")


def get_last_cache_status() -> str:
    """Return "HIT" or "MISS" for the most recent @cached call in this request."""
    return _last_cache_status.get()


def cached(key_prefix: str, ttl_seconds: int | None = None):
    """Cache a function's return value in Redis, keyed by its arguments.

    Args:
        key_prefix: Namespace for cache keys from this function, e.g.
            "product" -> keys look like "product:101".
        ttl_seconds: How long entries live before expiring. Defaults to
            `settings.CACHE_TTL_SECONDS` if not given.

    Usage:
        @cached(key_prefix="product")
        def get_product(product_id: str) -> dict: ...

    Notes:
        - The wrapped function's positional/keyword arguments are joined
          into the cache key, so `get_product("101")` and
          `get_product("103")` are cached separately.
        - Only JSON-serializable return values can be cached (dicts,
          lists, strings, numbers) - this covers the vast majority of
          real API responses.
    """
    ttl = ttl_seconds or settings.CACHE_TTL_SECONDS

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _build_key(key_prefix, args, kwargs)

            # 1. Try the cache. ANY Redis failure here - including being
            #    unable to get a client at all - just means "treat this
            #    as a miss," never "fail the request."
            client = None
            cached_value = None
            try:
                client = get_redis()
                cached_value = client.get(cache_key)
            except redis.RedisError as exc:
                logger.warning("cache read failed, falling back to source", extra={"key": cache_key, "error": str(exc)})

            if cached_value is not None:
                logger.info("cache hit", extra={"key": cache_key})
                _last_cache_status.set("HIT")
                return json.loads(cached_value)

            # 2. Miss (or Redis unavailable) -> call the real function.
            logger.info("cache miss", extra={"key": cache_key})
            _last_cache_status.set("MISS")
            result = func(*args, **kwargs)

            # 3. Best-effort write-back. Never let a failed cache WRITE
            #    turn a successful computation into an error response.
            try:
                (client or get_redis()).set(cache_key, json.dumps(result), ex=ttl)
            except redis.RedisError as exc:
                logger.warning("cache write failed", extra={"key": cache_key, "error": str(exc)})

            return result

        return wrapper

    return decorator


def invalidate(key_prefix: str, *args, **kwargs) -> bool:
    """Manually remove one cached entry - call this when the underlying
    data changes, so stale results aren't served until the TTL expires.
    """
    cache_key = _build_key(key_prefix, args, kwargs)
    try:
        return bool(get_redis().delete(cache_key))
    except redis.RedisError as exc:
        logger.warning("cache invalidate failed", extra={"key": cache_key, "error": str(exc)})
        return False


def _build_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """Build a deterministic cache key from a function's call arguments."""
    parts = [prefix, *map(str, args)] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
    return ":".join(parts)
