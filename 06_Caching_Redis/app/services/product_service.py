"""
app/services/product_service.py
================================
Simulates a slow upstream data source (e.g. a heavy SQL join, a
third-party API) and wraps it with the `@cached` decorator from
app/cache/decorators.py.

This is where the caching CONCEPT gets applied to a real piece of
business logic - contrast with the raw cache-get/cache-set code you'd
otherwise have to repeat inside every endpoint that needs caching.
"""

import time

from app.cache.decorators import cached, invalidate

# Stand-in for a real database.
_FAKE_DB = {
    "101": {"id": "101", "name": "KeyBoard", "price": 45.0},
    "103": {"id": "103", "name": "Computer", "price": 165.0},
    "107": {"id": "107", "name": "Screen", "price": 85.0},
}


@cached(key_prefix="product")
def get_product(product_id: str) -> dict | None:
    """Fetch a single product, transparently caching the result in Redis.

    The FIRST call for a given `product_id` pays the full 1.5s cost and
    populates the cache; every call after that (within the TTL) returns
    almost instantly straight from Redis - this function's body doesn't
    run again until the cache entry expires.
    """
    time.sleep(1.5)  # simulated expensive lookup
    return _FAKE_DB.get(product_id)


def invalidate_product_cache(product_id: str) -> bool:
    """Clear the cached entry for one product.

    Needed after any write that changes product data (e.g. an
    `update_product` call elsewhere) - otherwise clients could keep
    seeing the old cached value until the TTL naturally expires.
    """
    return invalidate("product", product_id)
