# 🚀 Production-Grade Redis Caching Service in FastAPI

A clean, production-ready Python/FastAPI service demonstrating real-world Redis caching patterns. 

Rather than polluting API route handlers with manual `get`/`set` boilerplate, this project showcases **decoupled, resilient caching architecture** featuring a reusable custom decorator, connection pooling, fast failover timeouts, and automatic graceful degradation.

---

## ✨ Key Features & Architecture Highlights

* **Decoupled Decorator (`@cached`)**: Declarative function annotation for caching key generation, serialization, and TTL handling—keeping business logic clean.
* **Graceful Degradation (Circuit Breaker Behavior)**: If Redis goes offline or times out, requests automatically fall back to the underlying database/service with zero 500 errors.
* **Connection Pooling & Fast Timeouts**: Fails fast on network partitions or slow Redis responses, preventing API worker thread starvation.
* **Standard `X-Cache-Status` Headers**: Exposes `HIT` vs `MISS` via clean HTTP response headers (similar to Cloudflare/Fastly) instead of polluting JSON response bodies.
* **Decoupled `/health` Endpoint**: Reports application status and cache status independently, enabling fine-grained alerting (e.g., alert on *Cache Degraded* without triggering *Service Down*).

---

## 🏗️ Project Architecture

```
app/
├── main.py                 # App factory & decoupled /health check endpoint
├── core/
│   ├── config.py           # Typed settings (pydantic-settings)
│   └── logging.py          # Structured JSON logging
├── cache/
│   ├── redis_client.py     # Shared connection pool & health checks
│   └── decorators.py      # Declarative @cached decorator implementation
├── schemas/
│   └── product.py         # Pydantic schemas / API response shapes
├── services/
│   └── product_service.py # Mock "expensive" database layer wrapped in @cached
└── api/routes/
    └── products.py        # Endpoints with cache invalidation (GET/DELETE)
```

---

## ⚡ Quick Start

### 1. Run Locally

```bash
# Start a local Redis instance
docker run -p 6379:6379 -d redis

# Install dependencies and start server
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Verify Cache Hits/Misses

**First call (Cache Miss):**
```bash
curl -i http://localhost:8000/products/101
# Header: X-Cache-Status: MISS
# Response time: ~1.0s (simulated DB latency)
```

**Second call (Cache Hit):**
```bash
curl -i http://localhost:8000/products/101
# Header: X-Cache-Status: HIT
# Response time: ~2ms
```

---

## 🐳 Run with Docker Compose

Run the API and Redis together in isolated containers:

```bash
docker compose up --build
```

---

## 🧪 Testing

Unit & integration tests use `fakeredis`—no running Redis instance required. Includes resilience tests asserting the API remains fully functional even when Redis is completely unreachable.

```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## 📈 Future Enhancements / Roadmap

- [ ] **Cache Stampede Protection**: Single-flight locking via Redis locks so only one request recomputes expired keys while others wait.
- [ ] **TTL Jitter**: Randomizing expiration windows slightly to prevent synchronized cache invalidation waves across high-volume keys.
- [ ] **Proactive Cache Warming**: Background worker pipelines to pre-warm critical hot keys upon service deployment.