"""
app/limiter/token_bucket.py
============================
A distributed token-bucket rate limiter backed by Redis, using an
atomic Lua script instead of separate GET/SET/INCR calls.

WHY A LUA SCRIPT (and not just Redis INCR, like the "simple" version)?
------------------------------------------------------------------------
The simple fixed-window approach (`INCR` a counter, `EXPIRE` it) has two
real weaknesses in production:

1. **Bursty edges**: a client can send `LIMIT` requests in the last
   100ms of one window, then `LIMIT` more in the first 100ms of the
   next window - 2x the intended rate in a fraction of a second.
2. **Multi-step race conditions**: anything that reads a value, decides
   something, then writes a new value (read -> compute -> write) is
   NOT atomic across two separate Redis commands - two concurrent
   requests could both read "4 tokens left," both decide "allowed,"
   and both proceed, even though only one token remained.

A **token bucket** models a bucket that continuously refills at a fixed
rate and holds up to `capacity` tokens; every request costs 1 token,
and requests are rejected once the bucket is empty. This smooths out
bursts (you can spend a saved-up burst, but then you're limited to the
refill rate) and better matches how real traffic behaves.

Running the whole "read state, compute new state, write state" sequence
as a single Lua script makes Redis execute it atomically - no other
command can interleave in the middle, which is what closes the race
condition INCR-based limiters are vulnerable to under real concurrency.
"""

import time

import redis

# KEYS[1] = the Redis key for this client's bucket (a Redis HASH: tokens, ts)
# ARGV[1] = bucket capacity (max tokens / max burst size)
# ARGV[2] = refill rate, in tokens per second
# ARGV[3] = current unix timestamp (passed in, not read via Lua's clock,
#           so this script's behavior is deterministic and testable)
#
# Returns: {allowed (1/0), tokens_remaining, seconds_until_next_token}
_TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(bucket[1])
local last_ts = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_ts = now
end

-- Refill: however much time has passed since we last checked, add that
-- many tokens (proportionally), capped at the bucket's capacity.
local elapsed = math.max(0, now - last_ts)
tokens = math.min(capacity, tokens + (elapsed * refill_rate))

local allowed = 0
if tokens >= 1 then
    allowed = 1
    tokens = tokens - 1
end

redis.call("HMSET", key, "tokens", tokens, "ts", now)
-- Expire the whole key once the bucket would be fully refilled anyway
-- and idle, so we don't keep counters around forever for one-off clients.
redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) + 1)

local retry_after = 0
if allowed == 0 then
    retry_after = (1 - tokens) / refill_rate
end

return {allowed, tokens, retry_after}
"""


class TokenBucketLimiter:
    """Wraps the Lua script above behind a small, typed Python API."""

    def __init__(self, redis_client: redis.Redis, capacity: int, window_seconds: int):
        """
        Args:
            redis_client: A connected Redis client.
            capacity: Max tokens (burst size) per client.
            window_seconds: Time to fully refill an empty bucket.
        """
        self._redis = redis_client
        self._capacity = capacity
        self._refill_rate = capacity / window_seconds
        self._script = redis_client.register_script(_TOKEN_BUCKET_LUA)

    def check(self, client_id: str) -> tuple[bool, float, float]:
        """Attempt to consume one token for `client_id`.

        Args:
            client_id: Identifies the caller (IP, API key, user id, ...).

        Returns:
            (allowed, tokens_remaining, retry_after_seconds)
        """
        key = f"rate_limit:{client_id}"
        allowed, tokens_remaining, retry_after = self._script(
            keys=[key],
            args=[self._capacity, self._refill_rate, time.time()],
        )
        return bool(allowed), float(tokens_remaining), float(retry_after)
