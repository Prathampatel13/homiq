"""Password hashing and verification.

Uses ``bcrypt`` directly (rather than ``passlib``) because passlib 1.7.4 is
incompatible with bcrypt >= 4.1 (raises ``AttributeError`` on wrap).  Using the
native library avoids the version conflict entirely.
"""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    if password is None:
        raise ValueError("Password cannot be None")
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False

