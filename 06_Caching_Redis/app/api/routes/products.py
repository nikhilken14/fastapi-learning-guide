"""
app/api/routes/products.py
===========================
Product endpoints. Notice the route itself has NO caching logic in it -
that all lives in app/services/product_service.py via the `@cached`
decorator. The route's only extra responsibility is reporting whether
this particular request was a cache hit or miss, the same way a real
CDN/reverse-proxy reports `X-Cache: HIT` - a standard, low-noise way to
make caching behavior observable without cluttering the response body.
"""

import time

from fastapi import APIRouter, HTTPException, Response

from app.cache.decorators import get_last_cache_status
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}")
def read_product(product_id: str, response: Response):
    """Fetch a product by id. Cached transparently via product_service.

    Check the `X-Cache-Status` response header: "MISS" the first time
    you request a given id, "HIT" on subsequent requests within the TTL.
    """
    start = time.perf_counter()

    data = product_service.get_product(product_id)

    response.headers["X-Cache-Status"] = get_last_cache_status()
    response.headers["X-Response-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"

    if data is None:
        raise HTTPException(status_code=404, detail=f"No product with id '{product_id}'")
    return data


@router.delete("/{product_id}/cache", status_code=204)
def clear_product_cache(product_id: str):
    """Manually invalidate the cached entry for one product.

    Call this right after updating a product's data in a real system,
    so the next read reflects the change immediately instead of waiting
    out the TTL.
    """
    product_service.invalidate_product_cache(product_id)
