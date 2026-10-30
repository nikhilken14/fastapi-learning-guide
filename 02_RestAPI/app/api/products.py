from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductNotFoundError, service

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(request: ProductCreate):
    return service.create(request)

@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    items, total = service.list(page, limit)
    return ProductListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    try:
        return service.get(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, request: ProductUpdate):
    try:
        return service.update(product_id, request)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    try:
        service.delete(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
