"""
Integration modules for third-party services.

Each module provides a client wrapper around external APIs:
- Razorpay: Payment gateway
- Cloudinary: Image / file hosting
- Google Maps: Geolocation, distance, ETA
- Email: SMTP / transactional email
- SMS: SMS notifications

Note: The imports below are intentionally lazy via ``__getattr__`` so that
optional third-party packages (e.g. ``cloudinary``) do not break importing
``app.main`` when they are not installed.
"""

from __future__ import annotations

from typing import Any


def __getattr__(name: str) -> Any:
    """Lazily import integration clients on attribute access.

    This keeps the package import-safe even when optional dependencies
    (cloudinary, etc.) are not installed.  The client classes are only
    imported when actually used.
    """
    if name == "RazorpayClient":
        from app.integrations.razorpay import RazorpayClient
        return RazorpayClient
    if name == "CloudinaryClient":
        from app.integrations.cloudinary import CloudinaryClient
        return CloudinaryClient
    if name == "GoogleMapsClient":
        from app.integrations.google_maps import GoogleMapsClient
        return GoogleMapsClient
    if name == "EmailClient":
        from app.integrations.email import EmailClient
        return EmailClient
    if name == "SMSClient":
        from app.integrations.sms import SMSClient
        return SMSClient
    raise AttributeError(f"module 'app.integrations' has no attribute {name!r}")


__all__ = [
    "RazorpayClient",
    "CloudinaryClient",
    "GoogleMapsClient",
    "EmailClient",
    "SMSClient",
]

