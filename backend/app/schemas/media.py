"""
Pydantic Schemas for Media Asset Management & Cloudinary Integration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.media import MediaAssetType


class MediaFolderEnum(str, Enum):
    PROFILES = "homiq/profiles"
    TECHNICIAN_DOCS = "homiq/technician_docs"
    SERVICES = "homiq/services"
    BOOKINGS = "homiq/bookings"
    INVOICES = "homiq/invoices"


class DocumentTypeEnum(str, Enum):
    AADHAAR = "aadhaar"
    PAN = "pan"
    DRIVING_LICENSE = "driving_license"
    CERTIFICATE = "certificate"
    OTHER = "other"


class DocumentStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ─── CENTRAL MEDIA ASSET SCHEMAS ──────────────────────────────────────────


class StandardMediaResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class MediaAssetBase(BaseModel):
    owner_id: int
    owner_type: str
    asset_type: MediaAssetType


class MediaAssetCreate(MediaAssetBase):
    pass


class MediaAssetResponse(MediaAssetBase):
    id: int
    cloudinary_asset_id: Optional[str] = None
    cloudinary_public_id: str
    secure_url: str
    thumbnail_url: Optional[str] = None
    resource_type: str = "image"
    format: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MediaAssetListResponse(BaseModel):
    total: int
    items: list[MediaAssetResponse]


class MediaOptimizedUrlRequest(BaseModel):
    width: Optional[int] = Field(None, ge=10, le=4000)
    height: Optional[int] = Field(None, ge=10, le=4000)
    crop: str = Field("fill", description="Cloudinary crop mode: fill, fit, limit, thumb, scale")
    quality: str = Field("auto", description="Quality: auto, best, good, eco, low")
    fetch_format: str = Field("auto", description="Format: auto, webp, png, jpg, avif")
    gravity: str = Field("auto", description="Gravity: auto, face, center, north, south")


class MediaOptimizedUrlResponse(BaseModel):
    public_id: str
    optimized_url: str
    thumbnail_url: str


# ─── LEGACY / COMPATIBILITY SCHEMAS ──────────────────────────────────────


class MediaResponse(BaseModel):
    public_id: str
    url: str
    secure_url: str
    thumbnail_url: str
    format: str = ""
    width: int = 0
    height: int = 0
    bytes: int = 0
    folder: str = "homiq"
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}


class MediaReplacePayload(BaseModel):
    old_public_id: Optional[str] = None
    folder: Optional[str] = "homiq"


class TechnicianDocumentResponse(BaseModel):
    id: str
    technician_id: int
    doc_type: DocumentTypeEnum
    url: str
    public_id: str
    status: DocumentStatusEnum = DocumentStatusEnum.PENDING
    rejection_reason: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}


class DocumentApprovalPayload(BaseModel):
    status: DocumentStatusEnum
    rejection_reason: Optional[str] = None
