import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# In-memory storage acting as a database for processed orders
PROCESSED_ORDERS_DB: Dict[str, Dict[str, Any]] = {}


class OrderHandler:
    @staticmethod
    async def process_order(order_data: Dict[str, Any]):
        """Processes an incoming order and saves it into memory/database."""
        order_id = order_data.get("order_id")
        product = order_data.get("product")
        quantity = order_data.get("quantity")
        total = order_data.get("total")

        if not order_id or not product or quantity is None:
            raise ValueError(f"Malformed order payload: {order_data}")

        # Save processed order status into memory
        PROCESSED_ORDERS_DB[order_id] = {
            **order_data,
            "status": "PROCESSED",
            "inventory_updated": True,
        }

        logger.info(
            f"✅ Saved Order {order_id} to DB | Item: {product} x {quantity} | Total: ${total}"
        )