"""
A small sample "orders" API whose only real purpose is to generate
realistic, varied traffic to observe in Grafana: some fast requests,
some slow ones, and a route that sometimes fails - notice this file has
ZERO metrics code in it. All instrumentation happens automatically via
app/middleware/metrics.py.
"""

import random
import time

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{order_id}")
def get_order(order_id: str):
    """Simulates a normal, moderately fast lookup."""
    time.sleep(random.uniform(0.01, 0.1))
    return {"order_id": order_id, "status": "shipped"}


@router.get("/{order_id}/slow-report")
def slow_report(order_id: str):
    """Simulates a slow endpoint (e.g. a heavy report/join), to give the
    latency histogram an obviously different shape from the fast route above."""
    time.sleep(random.uniform(0.2, 0.6))
    return {"order_id": order_id, "report": "generated"}


@router.get("/{order_id}/flaky")
def flaky_endpoint(order_id: str):
    """Fails ~30% of the time, to populate the exception/error-rate metrics."""
    if random.random() < 0.3:
        raise HTTPException(status_code=500, detail="simulated downstream failure")
    return {"order_id": order_id, "status": "ok"}
