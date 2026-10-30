"""app/schemas/product.py - the API's public shape for a Product."""

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    price: float


class ProductResponse(BaseModel):
    """Wraps a Product with cache metadata, so clients (and this demo)
    can see whether a response was served from cache or from the source."""
    source: str  # "cache" | "database"
    took_ms: float
    data: Product
