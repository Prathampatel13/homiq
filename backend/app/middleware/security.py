from __future__ import annotations

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("homiq.security.middleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Enterprise Security Middleware.

    - Keeps production security headers.
    - Allows Swagger UI and ReDoc to load their CDN assets.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Modern browsers ignore X-XSS-Protection, but harmless to keep.
        response.headers["X-XSS-Protection"] = "1; mode=block"

        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Allow Swagger/ReDoc CDN assets while keeping the app secure.
        response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "font-src 'self' data: https://cdn.jsdelivr.net; "
    "connect-src 'self' https://cdn.jsdelivr.net; "
)

        return response