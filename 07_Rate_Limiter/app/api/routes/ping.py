"""app/api/routes/ping.py - a trivial protected endpoint to demonstrate the limiter."""

from fastapi import APIRouter

router = APIRouter(tags=["demo"])


@router.get("/ping")
def ping():
    """Rate-limited by the global middleware - see app/limiter/middleware.py."""
    return {"message": "pong"}
