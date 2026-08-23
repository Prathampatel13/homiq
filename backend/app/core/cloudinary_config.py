"""
Centralized Cloudinary Configuration.

Ensures a single, secure source of configuration for all Cloudinary SDK interactions.
"""

from __future__ import annotations

import logging
from typing import Optional

try:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    HAS_CLOUDINARY = True
except ImportError:
    cloudinary = None
    HAS_CLOUDINARY = False

from app.core.config import settings

logger = logging.getLogger("homiq.cloudinary")

_is_configured = False


def init_cloudinary() -> bool:
    """Initialize Cloudinary SDK with environment settings if credentials are provided."""
    global _is_configured
    if not HAS_CLOUDINARY:
        logger.warning("Cloudinary package is not installed.")
        return False

    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    api_key = settings.CLOUDINARY_API_KEY
    api_secret = settings.CLOUDINARY_API_SECRET

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        _is_configured = True
        logger.info("Cloudinary configured securely with cloud_name: %s", cloud_name)
        return True
    else:
        logger.info("Cloudinary credentials not fully configured; using fallback mock mode.")
        _is_configured = False
        return False


def is_cloudinary_configured() -> bool:
    """Check whether Cloudinary credentials have been successfully loaded."""
    global _is_configured
    if not _is_configured:
        init_cloudinary()
    return _is_configured


# Auto-configure on import
init_cloudinary()