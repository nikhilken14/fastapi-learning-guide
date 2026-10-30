from fastapi import FastAPI

from app.api.routes import ping
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.limiter.middleware import RateLimitMiddleware, build_rate_limit_middleware

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(RateLimitMiddleware, limiter=build_rate_limit_middleware())
app.include_router(ping.router)


@app.get("/health", tags=["ops"])
def health_check():
    """Exempted from rate limiting - see app/limiter/middleware.py _EXEMPT_PATHS."""
    return {"status": "ok", "service": settings.APP_NAME}
