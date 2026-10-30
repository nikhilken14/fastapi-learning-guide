from app.database.db import Base, engine
from app.routers import product
from fastapi import FastAPI

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Database initialization pending... Details: {e}")

app = FastAPI(title="Product & Order Management API")

app.include_router(product.router)

@app.get("/")
def health():
    return {"status":200}