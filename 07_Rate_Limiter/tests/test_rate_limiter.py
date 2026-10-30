"""
tests/test_rate_limiter.py
===========================
Tests the token bucket algorithm directly (fast, precise, controls time
explicitly) and the middleware end-to-end (confirms it's wired up
correctly and returns proper 429s/headers).
"""

import fakeredis
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.limiter.middleware import RateLimitMiddleware
from app.limiter.token_bucket import TokenBucketLimiter


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


def test_allows_up_to_capacity_then_blocks(fake_redis):
    """A fresh bucket with capacity=3 allows exactly 3 requests before blocking."""
    limiter = TokenBucketLimiter(fake_redis, capacity=3, window_seconds=10)

    results = [limiter.check("client-a")[0] for _ in range(4)]
    assert results == [True, True, True, False]


def test_different_clients_have_independent_buckets(fake_redis):
    """Client B's requests aren't affected by client A exhausting their bucket."""
    limiter = TokenBucketLimiter(fake_redis, capacity=1, window_seconds=10)

    assert limiter.check("client-a")[0] is True
    assert limiter.check("client-a")[0] is False
    assert limiter.check("client-b")[0] is True  # unaffected by client-a


def test_bucket_refills_over_time(fake_redis, monkeypatch):
    """After enough simulated time passes, a token becomes available again."""
    import app.limiter.token_bucket as tb_module

    current_time = [1000.0]
    monkeypatch.setattr(tb_module.time, "time", lambda: current_time[0])

    limiter = TokenBucketLimiter(fake_redis, capacity=1, window_seconds=10)

    assert limiter.check("client-a")[0] is True
    assert limiter.check("client-a")[0] is False  # bucket empty

    current_time[0] += 10  # a full refill window has passed
    assert limiter.check("client-a")[0] is True  # refilled


def test_retry_after_is_reported_when_blocked(fake_redis):
    limiter = TokenBucketLimiter(fake_redis, capacity=1, window_seconds=10)
    limiter.check("client-a")
    allowed, _, retry_after = limiter.check("client-a")
    assert allowed is False
    assert retry_after > 0


# --------------------------------------------------------------------
# Middleware-level tests (real HTTP requests through a real FastAPI app)
# --------------------------------------------------------------------

@pytest.fixture
def app_client(fake_redis):
    app = FastAPI()
    limiter = TokenBucketLimiter(fake_redis, capacity=2, window_seconds=10)
    app.add_middleware(RateLimitMiddleware, limiter=limiter)

    @app.get("/ping")
    def ping():
        return {"message": "pong"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return TestClient(app)


def test_middleware_allows_requests_within_capacity(app_client):
    assert app_client.get("/ping").status_code == 200
    assert app_client.get("/ping").status_code == 200


def test_middleware_blocks_once_capacity_exceeded(app_client):
    app_client.get("/ping")
    app_client.get("/ping")
    r = app_client.get("/ping")
    assert r.status_code == 429
    assert "retry_after_seconds" in r.json()
    assert "Retry-After" in r.headers


def test_health_endpoint_is_exempt_from_rate_limiting(app_client):
    for _ in range(10):
        assert app_client.get("/health").status_code == 200


def test_remaining_tokens_header_present_on_success(app_client):
    r = app_client.get("/ping")
    assert "X-RateLimit-Remaining" in r.headers
