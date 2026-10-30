"""
tests/test_caching.py
======================
Uses `fakeredis` in place of a real Redis server, so these tests run
anywhere with no external dependency - while still exercising the real
Redis client interface (get/set/delete/ttl), not a hand-rolled mock.
"""

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app import main
from app.cache import redis_client
from app.services import product_service


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Swap the real Redis connection for an in-memory fake for every test."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(redis_client, "get_redis", lambda: fake)
    monkeypatch.setattr("app.cache.decorators.get_redis", lambda: fake)
    monkeypatch.setattr("app.services.product_service.time.sleep", lambda _: None)  # skip the simulated delay
    yield fake


@pytest.fixture
def client():
    return TestClient(main.app)


def test_health_reports_cache_up(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["cache"] == "up"


def test_first_request_is_a_cache_miss(client):
    r = client.get("/products/101")
    assert r.status_code == 200
    assert r.headers["X-Cache-Status"] == "MISS"
    assert r.json()["name"] == "KeyBoard"


def test_second_request_is_a_cache_hit(client):
    client.get("/products/101")  # populate cache
    r = client.get("/products/101")
    assert r.headers["X-Cache-Status"] == "HIT"


def test_unknown_product_returns_404(client):
    r = client.get("/products/does-not-exist")
    assert r.status_code == 404


def test_invalidate_forces_next_request_to_miss(client):
    client.get("/products/103")  # MISS, then cached
    assert client.get("/products/103").headers["X-Cache-Status"] == "HIT"

    client.delete("/products/103/cache")

    assert client.get("/products/103").headers["X-Cache-Status"] == "MISS"


def test_graceful_degradation_when_redis_unavailable(client, monkeypatch):
    """If Redis is completely unreachable, requests should still succeed
    (just without caching) instead of the API returning a 500."""
    import redis as redis_module

    def broken_redis():
        raise redis_module.RedisError("simulated outage")

    # Simulate get_redis() itself failing to connect.
    monkeypatch.setattr("app.cache.decorators.get_redis", lambda: (_ for _ in ()).throw(redis_module.RedisError("down")))

    r = client.get("/products/107")
    assert r.status_code == 200
    assert r.json()["name"] == "Screen"
