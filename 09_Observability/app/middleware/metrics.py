"""
A more complete instrumentation setup than "count requests + time them":
this is the shape real production services use so Grafana dashboards
can answer more than one question.

Metrics exposed:
    - http_requests_total{method,path,status_code} (Counter)
        "How much traffic, broken down by outcome?"
    - http_request_duration_seconds{path} (Histogram)
        "How fast are we, and what does the distribution (p50/p95/p99) look like?"
    - http_requests_in_progress (Gauge)
        "How many requests are being handled RIGHT NOW?" - a Counter can
        only go up, so concurrency/load needs a Gauge instead.
    - http_exceptions_total{path,exception_type} (Counter)
        "What's actually crashing, and where?" - separate from status
        codes, since a route can return a clean error status without
        raising, or raise something FastAPI turns into a 500.

Using route templates (`request.scope["route"].path`, e.g. `/orders/{id}`)
rather than the raw URL for the `path` label is deliberate: using the
raw path would create a new, ever-growing set of Prometheus label
values for every distinct order id ever requested ("cardinality
explosion"), which is one of the most common real Prometheus mistakes.
"""

import time

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
)

EXCEPTION_COUNT = Counter(
    "http_exceptions_total",
    "Total unhandled exceptions raised while processing requests",
    ["path", "exception_type"],
)


def _route_template(request: Request) -> str:
    """Return the route's path TEMPLATE (e.g. '/orders/{order_id}'),
    falling back to the raw path only for genuinely unmatched routes
    (404s), which are low-cardinality by nature."""
    route = request.scope.get("route")
    return route.path if route is not None else request.url.path


class MetricsMiddleware(BaseHTTPMiddleware):
    """Instruments every request with the metrics defined above."""

    async def dispatch(self, request: Request, call_next):
        REQUESTS_IN_PROGRESS.inc()
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            path = _route_template(request)
            EXCEPTION_COUNT.labels(path=path, exception_type=type(exc).__name__).inc()
            REQUESTS_IN_PROGRESS.dec()
            raise

        duration = time.perf_counter() - start_time
        path = _route_template(request)

        REQUEST_LATENCY.labels(path=path).observe(duration)
        REQUEST_COUNT.labels(method=request.method, path=path, status_code=response.status_code).inc()
        REQUESTS_IN_PROGRESS.dec()

        return response
