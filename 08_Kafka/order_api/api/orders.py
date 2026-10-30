import os
import random
import uuid
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from kafka.producers import kafka_producer_service

router = APIRouter(prefix="/orders", tags=["Orders"])

# Read target topic from environment variable (defaults to 'orders')
KAFKA_ORDERS_TOPIC = os.getenv("KAFKA_ORDERS_TOPIC", "orders")

# 1. Product catalog dictionary
products = {
    "Keyboard": 23.99,
    "Mouse": 14.50,
    "Monitor": 199.99,
    "Headphones": 45.00,
    "Webcam": 35.75,
    "USB Drive": 12.99,
    "Desk Pad": 18.50,
    "Laptop Stand": 29.99,
    "Microphone": 55.00,
    "External Hard Drive": 79.99,
}

quantities = [1, 2, 3, 4, 5, 6, 7]


# 2. Helper function to generate a random order payload
def generate_random_order() -> Dict[str, Any]:
    product_name, unit_price = random.choice(list(products.items()))
    qty = random.choice(quantities)
    total_price = round(unit_price * qty, 2)

    return {
        "order_id": str(uuid.uuid4()),
        "product": product_name,
        "price_per_unit": unit_price,
        "quantity": qty,
        "total": total_price,
    }


# 3. FastAPI Endpoint utilizing the shared producer service
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order():
    order_data = generate_random_order()

    try:
        # Use the reusable global connection instance
        await kafka_producer_service.send_order(
            topic=KAFKA_ORDERS_TOPIC, data=order_data
        )
        return {
            "status": "success",
            "message": "Order published to Kafka successfully",
            "order": order_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to produce message to Kafka: {str(e)}",
        )