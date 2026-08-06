from __future__ import annotations

import logging
import time
from typing import Dict, Tuple

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger("homiq.security.rate_limiter")

# In-memory fallbacks for tests/environments without active Redis
_IN_MEMORY_RATELIMITS: Dict[str, list[float]] = {}
_IN_MEMORY_FAILED_LOGINS: Dict[str, int] = {}
_IN_MEMORY_LOCKOUTS: Dict[str, float] = {}


class RateLimiter:
    """Redis-backed rate limiter, IP throttler, and brute-force lockout manager."""

    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
                self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
            except Exception as exc:
                logger.warning(f"Redis connection unavailable for RateLimiter. Falling back to in-memory: {exc}")
                self.redis_client = None

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if `key` exceeds `max_requests` in `window_seconds`.
        Returns tuple (is_allowed, remaining_requests).
        """
        now = time.time()
        redis_key = f"homiq:ratelimit:{key}"

        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(redis_key, 0, now - window_seconds)
                pipe.zadd(redis_key, {str(now): now})
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds)
                res = pipe.execute()
                current_count = res[2]
                allowed = current_count <= max_requests
                remaining = max(0, max_requests - current_count)
                return allowed, remaining
            except Exception as exc:
                logger.warning(f"Redis rate limit check error: {exc}")

        # In-memory fallback
        timestamps = _IN_MEMORY_RATELIMITS.get(key, [])
        timestamps = [t for t in timestamps if now - t <= window_seconds]
        timestamps.append(now)
        _IN_MEMORY_RATELIMITS[key] = timestamps
        current_count = len(timestamps)
        allowed = current_count <= max_requests
        remaining = max(0, max_requests - current_count)
        return allowed, remaining

    def is_account_locked(self, identifier: str) -> bool:
        """Check if account/IP is currently locked out."""
        now = time.time()
        redis_key = f"homiq:lockout:{identifier}"

        if self.redis_client:
            try:
                return bool(self.redis_client.exists(redis_key))
            except Exception:
                pass

        lock_until = _IN_MEMORY_LOCKOUTS.get(identifier, 0)
        return now < lock_until

    def record_failed_login(self, identifier: str, max_attempts: int = 5, lockout_seconds: int = 900) -> int:
        """Record a failed login attempt. Locks account if max_attempts reached."""
        now = time.time()
        fail_key = f"homiq:failed_login:{identifier}"
        lock_key = f"homiq:lockout:{identifier}"

        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.incr(fail_key)
                pipe.expire(fail_key, lockout_seconds)
                res = pipe.execute()
                fails = res[0]
                if fails >= max_attempts:
                    self.redis_client.setex(lock_key, lockout_seconds, "locked")
                    logger.warning(f"Account/IP {identifier} locked out for {lockout_seconds} seconds after {fails} failed attempts.")
                return fails
            except Exception as exc:
                logger.warning(f"Redis record_failed_login error: {exc}")

        fails = _IN_MEMORY_FAILED_LOGINS.get(identifier, 0) + 1
        _IN_MEMORY_FAILED_LOGINS[identifier] = fails
        if fails >= max_attempts:
            _IN_MEMORY_LOCKOUTS[identifier] = now + lockout_seconds
            logger.warning(f"Account/IP {identifier} locked out in-memory.")
        return fails

    def reset_failed_logins(self, identifier: str):
        """Reset failed login counters upon successful authentication."""
        fail_key = f"homiq:failed_login:{identifier}"
        lock_key = f"homiq:lockout:{identifier}"

        if self.redis_client:
            try:
                self.redis_client.delete(fail_key, lock_key)
            except Exception:
                pass

        _IN_MEMORY_FAILED_LOGINS.pop(identifier, None)
        _IN_MEMORY_LOCKOUTS.pop(identifier, None)


rate_limiter = RateLimiter()
