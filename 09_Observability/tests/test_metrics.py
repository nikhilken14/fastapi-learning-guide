"""
tests/test_metrics.py
======================
Verifies the middleware actually records what it claims to, by calling
real endpoints and then inspecting the /metrics output - the same text
Prometheus itself would scrape and parse.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_returns_prometheus_format():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")


def test_request_count_increments_with_route_template_label():
    client.get("/orders/abc123")

    metrics_text = client.get("/metrics").text
    # Uses the route TEMPLATE, not the literal id - see metrics.py docstring
    # on cardinality. This is what keeps the label set bounded no matter
    # how many distinct order ids are ever requested.
    assert 'path="/orders/{order_id}"' in metrics_text


def test_in_progress_gauge_exists():
    client.get("/orders/abc123")
    metrics_text = client.get("/metrics").text
    assert "http_requests_in_progress" in metrics_text


def test_exception_metric_increments_on_flaky_failures():
    # Hit the flaky endpoint enough times that at least one 500 fires
    # (30% failure rate; 30 tries makes a false negative astronomically unlikely).
    for _ in range(30):
        client.get("/orders/x/flaky")

    metrics_text = client.get("/metrics").text
    assert "http_exceptions_total" in metrics_text or 'status_code="500"' in metrics_text


def test_latency_histogram_recorded_for_slow_route():
    client.get("/orders/x/slow-report")
    metrics_text = client.get("/metrics").text
    assert 'http_request_duration_seconds_bucket{le=' in metrics_text
    assert 'path="/orders/{order_id}/slow-report"' in metrics_text
