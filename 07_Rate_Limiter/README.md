# Rate Limiter Service — Distributed, Redis-backed Token Bucket

Enforces a per-client request rate using an **atomic Lua-script token
bucket** in Redis — the algorithm real API gateways use, not a naive
counter that breaks under concurrency or at window edges.

## Architecture

```
app/
├── main.py                     # wires the limiter into global middleware
├── core/
│   ├── config.py                  # bucket capacity + refill window, from env
│   └── logging.py                  # JSON structured logging
├── limiter/
│   ├── redis_client.py               # shared connection pool
│   ├── token_bucket.py                 # the algorithm: atomic Lua script + typed wrapper
│   └── middleware.py                    # applies it to every request; exempts /health
└── api/routes/
    └── ping.py                          # sample protected endpoint
tests/
└── test_rate_limiter.py           # algorithm tests + full HTTP middleware tests
```

## Why a Lua script, not `INCR`+`EXPIRE`?

The simple fixed-window version (`INCR` a counter per time window) has
two real problems:
1. **Edge bursts** — a client can spend the limit in the last instant
   of one window and the limit again in the first instant of the next,
   getting 2x the intended rate for a moment.
2. **Race conditions** — "read count, decide, write count" isn't atomic
   across separate Redis commands; concurrent requests can both read
   "room left" before either writes back.

A **token bucket** (bucket refills continuously, each request costs one
token) smooths bursts out naturally, and running the whole
read-refill-decide-write sequence as **one Lua script** makes Redis
execute it atomically — no interleaving, no race condition, even under
real concurrent load. See the big comment in `token_bucket.py` for the
full explanation and the script itself.

## What's "production" about this, vs. the simple version
- Token bucket instead of fixed window (see above).
- Applied as **global middleware**, not opt-in per route — new endpoints
  are protected automatically; `/health` is explicitly exempted.
- `Retry-After` and `X-RateLimit-Remaining` response headers — the same
  convention GitHub/Stripe use, so well-behaved clients can back off
  proactively instead of only learning the limit by getting 429s.
- Client identity respects `X-Forwarded-For` (for when this sits behind
  a real proxy/load balancer), not just the raw socket IP.
- `docker-compose.yml` runs **two instances** of the app against one
  Redis, so you can prove the limit is shared between them.

## Run locally
```bash
docker run -p 6379:6379 redis
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Hit `GET /ping` more than 5 times quickly — the 6th+ return `429` until
the bucket refills (watch `X-RateLimit-Remaining` count down first).

## Prove it's distributed
```bash
docker compose up --build
# instance A: http://localhost:8001/ping
# instance B: http://localhost:8002/ping
```
Exhaust the limit calling instance A, then immediately call instance B —
you'll still get 429s, because both instances check the same Redis bucket.

## Run tests (no real Redis needed — uses `fakeredis`)
```bash
pip install -r requirements-dev.txt
pytest -v
```
Includes a test that fakes the passage of time to verify the bucket
actually refills, not just that it blocks.

## Next steps toward "even more production"
- Different limits per route or per authenticated user tier (free vs paid).
- A Redis Cluster / Sentinel setup for HA instead of a single Redis node.
- Emit rate-limit-exceeded events as metrics (pairs naturally with the
  `08-observability-stack` project).
