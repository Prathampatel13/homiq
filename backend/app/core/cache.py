"""
Redis Response Caching & High-Performance Cache Decorator.
"""

from __future__ import annotations

import functools
import json
import logging
import time
from typing import Any, Callable, Optional

from app.security.rate_limiter import rate_limiter

logger = logging.getLogger("homiq.cache")

# In-memory cache fallback
_IN_MEMORY_CACHE: dict[str, tuple[float, Any]] = {}


def cache_response(ttl: int = 300, key_prefix: str = "api_cache"):
    """
    Decorator for caching endpoint responses in Redis with specified TTL.
    Supports in-memory fallback if Redis is unavailable.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from func name and kwargs
            kwargs_str = json.dumps({k: str(v) for k, v in sorted(kwargs.items())})
            cache_key = f"homiq:cache:{key_prefix}:{func.__name__}:{kwargs_str}"

            # 1. Check Redis / In-Memory Cache
            if rate_limiter.redis_client:
                try:
                    cached_val = rate_limiter.redis_client.get(cache_key)
                    if cached_val:
                        return json.loads(cached_val)
                except Exception as exc:
                    logger.warning(f"Cache lookup error: {exc}")
            else:
                if cache_key in _IN_MEMORY_CACHE:
                    exp, val = _IN_MEMORY_CACHE[cache_key]
                    if time.time() < exp:
                        return val

            # 2. Execute target function
            result = await func(*args, **kwargs)

            # 3. Store result in Redis / In-Memory
            if result is not None:
                if rate_limiter.redis_client:
                    try:
                        rate_limiter.redis_client.setex(
                            cache_key,
                            ttl,
                            json.dumps(result, default=str),
                        )
                    except Exception as exc:
                        logger.warning(f"Cache write error: {exc}")
                else:
                    _IN_MEMORY_CACHE[cache_key] = (time.time() + ttl, result)

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            kwargs_str = json.dumps({k: str(v) for k, v in sorted(kwargs.items())})
            cache_key = f"homiq:cache:{key_prefix}:{func.__name__}:{kwargs_str}"

            if rate_limiter.redis_client:
                try:
                    cached_val = rate_limiter.redis_client.get(cache_key)
                    if cached_val:
                        return json.loads(cached_val)
                except Exception:
                    pass
            else:
                if cache_key in _IN_MEMORY_CACHE:
                    exp, val = _IN_MEMORY_CACHE[cache_key]
                    if time.time() < exp:
                        return val

            result = func(*args, **kwargs)

            if result is not None:
                if rate_limiter.redis_client:
                    try:
                        rate_limiter.redis_client.setex(
                            cache_key,
                            ttl,
                            json.dumps(result, default=str),
                        )
                    except Exception:
                        pass
                else:
                    _IN_MEMORY_CACHE[cache_key] = (time.time() + ttl, result)

            return result

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate all Redis / In-Memory cache keys matching pattern."""
    if not rate_limiter.redis_client:
        keys_to_del = [k for k in list(_IN_MEMORY_CACHE.keys()) if pattern in k]
        for k in keys_to_del:
            del _IN_MEMORY_CACHE[k]
        return len(keys_to_del)

    try:
        keys = rate_limiter.redis_client.keys(f"homiq:cache:*{pattern}*")
        if keys:
            return rate_limiter.redis_client.delete(*keys)
    except Exception as exc:
        logger.warning(f"Cache invalidation error: {exc}")
    return 0
