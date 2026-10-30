from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.products import router as product_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Mini Project 1: production-oriented FastAPI REST API",
)

app.include_router(product_router)

@app.get("/")
def home():
    return {"status" : "backend is running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "UP", "service": settings.app_name}

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )
