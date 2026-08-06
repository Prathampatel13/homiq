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


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password against enterprise security policy.
    Requires minimum 8 characters, uppercase, lowercase, digit, and special character.
    """
    import re
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, "Password meets security requirements."


def generate_secure_otp(length: int = 6) -> str:
    """Generate cryptographically secure numeric OTP string."""
    import secrets
    return "".join(secrets.choice("0123456789") for _ in range(length))


def sanitize_input(text: str) -> str:
    """Sanitize string input against basic HTML/XSS injection."""
    if not text:
        return ""
    import html
    return html.escape(text.strip())

