# Observability Stack — Prometheus + Grafana

A FastAPI service instrumented with real production-shaped metrics
(request rate, latency percentiles, in-flight requests, error rate),
scraped by Prometheus, visualized in a Grafana dashboard that's already
there the moment you open Grafana — no manual data-source or dashboard
setup required.

## Architecture

```
app/
├── main.py                    # wires MetricsMiddleware + /metrics endpoint
├── core/
│   ├── config.py                 # typed Settings
│   └── logging.py                 # JSON structured logging
├── middleware/
│   └── metrics.py                  # Counter, Histogram, Gauge - the real instrumentation
└── api/routes/
    └── orders.py                    # sample business routes (fast / slow / flaky)
tests/
└── test_metrics.py               # asserts metrics are actually recorded, not just exposed

prometheus.yml                 # scrape config
grafana/
├── provisioning/
│   ├── datasources/datasource.yml   # auto-registers Prometheus - no UI clicking
│   └── dashboards/dashboard.yml      # tells Grafana to auto-load dashboards/*.json
└── dashboards/
    └── orders-service-overview.json   # request rate, p50/p95/p99 latency, error %, in-flight
```

## What's "production" about this, vs. the simple version
- **Four metric types, not just a request counter**: `Counter` for
  totals, `Histogram` for latency distribution (so you can compute
  p95/p99, not just an average), `Gauge` for concurrency
  (`http_requests_in_progress`), and a separate exception counter.
- **Route templates, not raw URLs, as labels** — `/orders/{order_id}`
  instead of `/orders/abc123`. Using raw paths/ids as Prometheus labels
  is one of the most common real mistakes ("cardinality explosion") —
  it silently creates unbounded numbers of time series and eventually
  makes Prometheus itself fall over.
- **Grafana fully auto-provisioned** — datasource and dashboard are
  defined as files, not manual UI configuration, so spinning up a fresh
  environment reproduces the exact same dashboard every time (this is
  how real teams manage Grafana — "dashboards as code").
- **A dashboard that answers real questions**: traffic by endpoint,
  latency percentiles (not just averages, which hide tail latency),
  error rate as a percentage, and current concurrency.

## Run everything
```bash
docker compose up --build
```
Generate some traffic:
```bash
for i in $(seq 1 50); do curl -s localhost:8000/orders/$i > /dev/null; done
for i in $(seq 1 20); do curl -s localhost:8000/orders/$i/slow-report > /dev/null; done
for i in $(seq 1 20); do curl -s localhost:8000/orders/$i/flaky > /dev/null; done
```
Then open:
- Prometheus: `http://localhost:9090` — try the query `http_requests_total`
- Grafana: `http://localhost:3000` (anonymous admin access enabled for
  this demo) — the "Orders Service - Overview" dashboard is already there.

## Run just the app + raw metrics (no Docker)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Hit a few routes, then check `http://127.0.0.1:8000/metrics`.

## Run tests
```bash
pip install -r requirements-dev.txt
pytest -v
```

## Next steps toward "even more production"
- Alertmanager rules (e.g. "page if error rate > 5% for 5 minutes").
- Distributed tracing (OpenTelemetry) to see a single request's path
  across services like the 07-kafka-orders producer/consumer pair.
- `GF_AUTH_ANONYMOUS_ENABLED` is fine for a local demo; a real
  deployment would use real Grafana auth (SSO, API-provisioned users).
