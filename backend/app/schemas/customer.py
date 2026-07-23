from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CustomerAddressCreate(BaseModel):
    label: str = Field(default="home", description="Address label: home, work, other")
    address_line1: str = Field(..., min_length=3, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="India", max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_default: bool = False

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        allowed = {"home", "work", "other"}
        if v.lower() not in allowed:
            raise ValueError(f"Label must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Postal code cannot be empty")
        return v.strip()


class CustomerAddressUpdate(BaseModel):
    label: Optional[str] = Field(None, description="Address label: home, work, other")
    address_line1: Optional[str] = Field(None, min_length=3, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=3, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_default: Optional[bool] = None

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"home", "work", "other"}
            if v.lower() not in allowed:
                raise ValueError(f"Label must be one of: {', '.join(allowed)}")
            return v.lower()
        return v


class CustomerAddressResponse(BaseModel):
    id: int
    customer_id: int
    label: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=3, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    preferred_language: Optional[str] = Field(None, max_length=50)


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

    model_config = {"from_attributes": True}


class ProfileImageResponse(BaseModel):
    profile_image: str
    message: str = "Profile image uploaded successfully"

