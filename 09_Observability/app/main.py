from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.routes import orders
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.metrics import MetricsMiddleware

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.add_middleware(MetricsMiddleware)
app.include_router(orders.router)

@app.get("/")
def home():
    return {"status" : "backend is running"}


@app.get("/metrics", tags=["ops"])
def metrics():
    """The endpoint Prometheus scrapes - see prometheus.yml."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health", tags=["ops"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
