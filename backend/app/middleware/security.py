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

        # Allow frontend assets, fonts, CDN, QR codes and localhost connections
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: http: https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net http: https:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net http: https:; "
            "img-src 'self' data: blob: https: http:; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net http: https:; "
            "connect-src 'self' ws: wss: http: https:; "
        )

        return response