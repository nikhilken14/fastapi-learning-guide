from app.database.db import Base
from sqlalchemy import Column, ForeignKey, Float, Integer, String
from sqlalchemy.orm import relationship


# ORM Model maps to the "products" table in Postgres
class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # Establishes relationship to OrderModel
    orders = relationship("OrderModel", back_populates="product")


# ORM Model maps to the "orders" table in Postgres
class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Establishes relationship back to ProductModel
    product = relationship("ProductModel", back_populates="orders")