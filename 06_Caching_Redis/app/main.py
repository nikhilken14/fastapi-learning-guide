from fastapi import FastAPI

from app.api.routes import products
from app.cache.redis_client import is_redis_healthy
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.include_router(products.router)

@app.get("/")
def home():
    return {"status" : "Backend is running"}


@app.get("/health", tags=["ops"])
def health_check():
    """Reports both app liveness AND cache availability separately.

    This distinction matters operationally: if Redis is down but the
    app still responds (in degraded, uncached mode - see
    app/cache/decorators.py), you want your monitoring to show
    "cache: down" as a warning, not flip the whole service to "unhealthy"
    and trigger a restart that won't actually fix anything.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "cache": "up" if is_redis_healthy() else "down",
    }
