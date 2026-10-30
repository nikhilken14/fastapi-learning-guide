from fastapi import FastAPI,HTTPException
from contextlib import asynccontextmanager

from app.service import *

from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")
    print("Loading seed data...")

    seed_data()

    print("Seed data loaded successfully")

    yield

    print("Application shutting down...")


app = FastAPI(
    title="Simple Product Service",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/")
def home():
    return {"status": "Backend is running..."}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "api-service"
    }


# ---------------------------------------------------------
# Product - GET
# ---------------------------------------------------------

@app.get("/products/list")
def get_all_product_names():
    """Return only product names."""
    return getList()


@app.get("/products")
def get_products():
    """Return all products."""
    return getProducts()


@app.get("/products/{product_id}")
def get_product(product_id: str):
    """Return a single product by ID."""

    product = getProductById(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id '{product_id}' not found"
        )

    return product


# ---------------------------------------------------------
# Sales - GET
# ---------------------------------------------------------

@app.get("/sales")
def get_all_sales():
    """Return all sales."""
    return getAllSales()


@app.get("/sales/total")
def total_sales():
    """Return total revenue."""
    return {
        "total_sales": getTotalSales()
    }


@app.get("/sales/by-product")
def sales_by_product():
    """Return revenue grouped by product."""
    return getSalesByProduct()


@app.get("/sales/quantity")
def sales_quantity():
    """Return quantity sold grouped by product."""
    return getQuantityByProduct()


# ---------------------------------------------------------
# Product - POST
# ---------------------------------------------------------

@app.post("/products")
def create_product(
    product_id: str,
    name: str,
    price: float
):
    """Create a new product."""

    try:
        return addProduct(
            product_id=product_id,
            name=name,
            price=price
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------------
# Sales - POST
# ---------------------------------------------------------

@app.post("/sales")
def create_sale(
    product_id: str,
    quantity: int
):
    """Create a new sale."""

    try:
        return addSale(
            product_id=product_id,
            quantity=quantity
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------------
# Product - PUT
# ---------------------------------------------------------

@app.put("/products/{product_id}/price")
def update_price(
    product_id: str,
    new_price: float
):
    """Update product price."""

    try:
        return updateProductPrice(
            product_id=product_id,
            new_price=new_price
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ---------------------------------------------------------
# Product - DELETE
# ---------------------------------------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    """Delete a product."""

    deleted = deleteProduct(product_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id '{product_id}' not found"
        )

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }