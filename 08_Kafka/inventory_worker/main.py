import asyncio
import logging
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, status
from kafka.consumers import InventoryConsumer
from contextlib import asynccontextmanager
from config.handlers import PROCESSED_ORDERS_DB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await consumer_worker.initialize()
    consumer_task = asyncio.create_task(
        consumer_worker.start_listening()
    )

    try:
        yield
    finally:
        consumer_task.cancel()
        await asyncio.gather(consumer_task, return_exceptions=True)
        await consumer_worker.stop()


app = FastAPI(
    title="Inventory Worker API",
    description="Query orders consumed from Kafka",
    lifespan=lifespan,
)

consumer_worker = InventoryConsumer()


@app.get("/")
async def home():
    return { "status" : "consumer service is running"}


@app.get("/consumed-orders", status_code=status.HTTP_200_OK)
async def get_all_consumed_orders():
    """Returns all orders consumed and processed from Kafka."""
    return {
        "count": len(PROCESSED_ORDERS_DB),
        "orders": list(PROCESSED_ORDERS_DB.values()),
    }


@app.get("/consumed-orders/{order_id}", status_code=status.HTTP_200_OK)
async def get_consumed_order_by_id(order_id: str):
    """Returns a specific order by its order_id."""
    order = PROCESSED_ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order ID '{order_id}' has not been consumed yet.",
        )
    return order


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)