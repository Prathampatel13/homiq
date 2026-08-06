from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
