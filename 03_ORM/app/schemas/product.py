from pydantic import BaseModel, ConfigDict

# --- PRODUCT SCHEMAS ---


class ProductCreate(BaseModel):
    name: str
    price: float


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    # Enables automatic mapping from ORM models to Pydantic objects
    model_config = ConfigDict(from_attributes=True)


# --- ORDER SCHEMAS ---


class OrderCreate(BaseModel):
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    quantity: int
    product_id: int
    product: ProductResponse  # Includes nested product DTO details

    model_config = ConfigDict(from_attributes=True)