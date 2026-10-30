from app.database.db import get_db
from app.models.product import OrderModel, ProductModel
from app.schemas.product import OrderCreate, OrderResponse, ProductCreate, ProductResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

# --- PRODUCT ENDPOINTS ---


@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Create ORM Instance from incoming DTO
    db_product = ProductModel(name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Get generated ID back from Database
    return db_product


@router.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    # Query Database using ORM
    return db.query(ProductModel).all()


# --- ORDER ENDPOINTS ---


@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(ProductModel).filter(ProductModel.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_order = OrderModel(product_id=order.product_id, quantity=order.quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    # Fetches orders along with their related product via ORM relationship
    return db.query(OrderModel).all()