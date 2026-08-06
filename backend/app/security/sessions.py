from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger("homiq.security.sessions")

# In-memory fallbacks
_IN_MEMORY_BLACKLIST: Set[str] = set()
_IN_MEMORY_SESSIONS: Dict[int, Dict[str, dict[str, Any]]] = {}


class TokenBlacklist:
    """Redis-backed JWT Token Blacklist Manager."""

    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
                self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            except Exception:
                self.redis_client = None

    def blacklist_token(self, jti: str, ttl_seconds: int = 86400):
        """Revoke a JWT token by adding its unique JTI to the blacklist."""
        if not jti:
            return
        key = f"homiq:blacklist:{jti}"
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl_seconds, "revoked")
                return
            except Exception as exc:
                logger.warning(f"Redis blacklist error: {exc}")

        _IN_MEMORY_BLACKLIST.add(jti)

    def is_blacklisted(self, jti: str) -> bool:
        """Check if token JTI is in the blacklist."""
        if not jti:
            return False
        key = f"homiq:blacklist:{jti}"
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception:
                pass

        return jti in _IN_MEMORY_BLACKLIST


class SessionTracker:
    """Multi-device session tracking and session revocation manager."""

    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
                self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            except Exception:
                self.redis_client = None

    def register_session(
        self,
        user_id: int,
        session_id: str,
        device_name: str = "Unknown Device",
        ip_address: str = "127.0.0.1",
        user_agent: str = "Unknown",
    ):
        """Record an active user login session."""
        now_str = datetime.now(timezone.utc).isoformat()
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "device_name": device_name,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "logged_in_at": now_str,
            "last_active_at": now_str,
        }

        key = f"homiq:session:{user_id}:{session_id}"
        if self.redis_client:
            try:
                self.redis_client.setex(key, 86400 * 7, json.dumps(session_data))
                return
            except Exception as exc:
                logger.warning(f"Redis session tracking error: {exc}")

        if user_id not in _IN_MEMORY_SESSIONS:
            _IN_MEMORY_SESSIONS[user_id] = {}
        _IN_MEMORY_SESSIONS[user_id][session_id] = session_data

    def get_active_sessions(self, user_id: int) -> list[dict[str, Any]]:
        """List active login sessions for a user."""
        if self.redis_client:
            try:
                pattern = f"homiq:session:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                sessions = []
                for k in keys:
                    val = self.redis_client.get(k)
                    if val:
                        sessions.append(json.loads(val))
                return sessions
            except Exception as exc:
                logger.warning(f"Redis get_active_sessions error: {exc}")

        user_sessions = _IN_MEMORY_SESSIONS.get(user_id, {})
        return list(user_sessions.values())

    def revoke_session(self, user_id: int, session_id: str) -> bool:
        """Revoke a specific device session."""
        key = f"homiq:session:{user_id}:{session_id}"
        if self.redis_client:
            try:
                deleted = self.redis_client.delete(key)
                return bool(deleted)
            except Exception:
                pass

        if user_id in _IN_MEMORY_SESSIONS and session_id in _IN_MEMORY_SESSIONS[user_id]:
            del _IN_MEMORY_SESSIONS[user_id][session_id]
            return True
        return False

    def revoke_all_sessions(self, user_id: int) -> int:
        """Revoke all active device sessions for a user."""
        count = 0
        if self.redis_client:
            try:
                pattern = f"homiq:session:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
                return count
            except Exception:
                pass

        user_sessions = _IN_MEMORY_SESSIONS.pop(user_id, {})
        return len(user_sessions)


token_blacklist = TokenBlacklist()
session_tracker = SessionTracker()
