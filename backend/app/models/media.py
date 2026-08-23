"""
Media Asset Database Model & Enums.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MediaAssetType(str, Enum):
    """Controlled system for all supported media and document asset types."""
    PROFILE_AVATAR = "profile_avatar"
    COMPANY_LOGO = "company_logo"
    SERVICE_IMAGE = "service_image"
    SERVICE_GALLERY = "service_gallery"
    TECHNICIAN_PORTFOLIO = "technician_portfolio"
    TECHNICIAN_CERTIFICATE = "technician_certificate"
    IDENTITY_DOCUMENT = "identity_document"
    BOOKING_BEFORE = "booking_before"
    BOOKING_AFTER = "booking_after"
    BOOKING_ATTACHMENT = "booking_attachment"
    COMPLAINT_ATTACHMENT = "complaint_attachment"
    REVIEW_IMAGE = "review_image"
    PROPERTY_IMAGE = "property_image"
    JOB_RESUME = "job_resume"
    JOB_DOCUMENT = "job_document"


class MediaAsset(Base):
    """
    Central Media Asset model representing uploaded images and documents in Cloudinary.
    """
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    asset_type: Mapped[MediaAssetType] = mapped_column(
        SAEnum(MediaAssetType, name="media_asset_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    
    cloudinary_asset_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cloudinary_public_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    secure_url: Mapped[str] = mapped_column(String(500), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(30), default="image", nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
