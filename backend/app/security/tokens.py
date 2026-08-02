from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import jwt

from app.core.config import settings


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:

    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": str(subject),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:

    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    payload = {
        "sub": str(subject),
        "type": "refresh",
        "jti": uuid4().hex,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )


def get_expiration_time(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)