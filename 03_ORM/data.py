import os
import sys

# Add parent directory to Python path so 'app' imports work smoothly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.db import Base, SessionLocal, engine
from app.models.product import OrderModel, ProductModel


def seed_database():
    # Ensure database tables are created before seeding
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Clear existing data (optional - helps prevent duplicate key errors)
        db.query(OrderModel).delete()
        db.query(ProductModel).delete()
        db.commit()

        print("Cleared existing data...")

        # 2. Create Initial Product ORM Instances
        product1 = ProductModel(name="Wireless Mouse", price=29.99)
        product2 = ProductModel(name="Mechanical Keyboard", price=89.99)
        product3 = ProductModel(name="27-inch Monitor", price=249.50)

        db.add_all([product1, product2, product3])
        # Commit products first so PostgreSQL generates primary key IDs for them
        db.commit()

        # Refresh products to read back generated IDs
        db.refresh(product1)
        db.refresh(product2)
        db.refresh(product3)

        print(f"Seeded 3 products (IDs: {product1.id}, {product2.id}, {product3.id})")

        # 3. Create Initial Order ORM Instances using seeded Product IDs
        orders = [
            OrderModel(product_id=product1.id, quantity=2),
            OrderModel(product_id=product1.id, quantity=1),
            OrderModel(product_id=product2.id, quantity=5),
            OrderModel(product_id=product3.id, quantity=1),
        ]

        db.add_all(orders)
        db.commit()

        print(f"Seeded {len(orders)} initial orders successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()