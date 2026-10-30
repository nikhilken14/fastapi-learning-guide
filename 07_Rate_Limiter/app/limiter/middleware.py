"""
app/limiter/middleware.py
==========================
Applies the token-bucket limiter to every incoming request, as
middleware - not as a per-route dependency.

Doing it as middleware (rather than `Depends(rate_limit)` on each route)
means new endpoints are protected automatically, the same way the
Prometheus metrics middleware in the observability project instruments
every route for free. Routes that should be exempt (health checks,
metrics scraping) are explicitly skipped, rather than everything
needing to opt in.
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.limiter.redis_client import get_redis
from app.limiter.token_bucket import TokenBucketLimiter

logger = logging.getLogger(__name__)
settings = get_settings()

# Paths that should never be rate limited - orchestrators/load balancers
# hit these frequently and shouldn't get locked out.
_EXEMPT_PATHS = {"/health"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rejects requests over the configured rate with 429, per client.

    Client identity here is the caller's IP address. In a real system
    fronted by an API gateway, you'd more likely key on an API key or
    authenticated user id, which `_client_id` is the one place to change.
    """

    def __init__(self, app, limiter: TokenBucketLimiter):
        super().__init__(app)
        self._limiter = limiter

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        client_id = self._client_id(request)
        allowed, tokens_remaining, retry_after = self._limiter.check(client_id)

        if not allowed:
            logger.info("rate limit exceeded", extra={"client_id": client_id})
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "retry_after_seconds": round(retry_after, 2)},
                headers={"Retry-After": str(max(1, round(retry_after)))},
            )

        response = await call_next(request)
        # Exposing remaining capacity lets well-behaved clients back off
        # proactively instead of learning the limit only by hitting 429 -
        # the same convention used by GitHub's/Stripe's public APIs.
        response.headers["X-RateLimit-Remaining"] = str(int(tokens_remaining))
        return response

    @staticmethod
    def _client_id(request: Request) -> str:
        """Identify the caller. Prefers a real client IP behind a proxy
        (X-Forwarded-For) but falls back to the direct connection IP."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def build_rate_limit_middleware():
    """Factory used by app/main.py to construct the middleware with a
    real TokenBucketLimiter wired to the shared Redis connection pool."""
    limiter = TokenBucketLimiter(
        redis_client=get_redis(),
        capacity=settings.RATE_LIMIT_TOKENS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    return limiter
