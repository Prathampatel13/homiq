"""Customer profile schemas.

The customer-address models live in :mod:`app.schemas.addresses` (the canonical
source).  They are re-exported here so existing imports such as
``from app.schemas.customer import CustomerAddressCreate`` keep working.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.addresses import (  # noqa: F401  (re-exported for backwards-compat)
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
)

__all__ = [
    "CustomerAddressCreate",
    "CustomerAddressResponse",
    "CustomerAddressUpdate",
    "CustomerProfileUpdate",
    "CustomerProfileResponse",
    "ProfileImageResponse",
]


class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=7, max_length=30)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    preferred_language: Optional[str] = Field(None, max_length=50)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Phone number cannot be empty")
        return normalized


class CustomerProfileResponse(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_language: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    addresses: list[CustomerAddressResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProfileImageResponse(BaseModel):
    profile_image: str
    message: str = "Profile image uploaded successfully"

