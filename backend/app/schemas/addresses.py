from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CustomerAddressCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=7, max_length=30, description="Recipient phone number")
    house_no: str = Field(..., min_length=1, max_length=100)
    building: Optional[str] = Field(None, max_length=255)
    landmark: Optional[str] = Field(None, max_length=255)
    area: str = Field(..., min_length=3, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=3, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_default: bool = Field(False, description="Mark this address as the default address")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Phone number cannot be empty")
        return normalized

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pincode cannot be empty")
        return normalized


class CustomerAddressUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=7, max_length=30)
    house_no: Optional[str] = Field(None, min_length=1, max_length=100)
    building: Optional[str] = Field(None, max_length=255)
    landmark: Optional[str] = Field(None, max_length=255)
    area: Optional[str] = Field(None, min_length=3, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, min_length=3, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_default: Optional[bool] = Field(None, description="Mark this address as default")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Phone number cannot be empty")
        return normalized

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pincode cannot be empty")
        return normalized


class CustomerAddressResponse(BaseModel):
    id: int
    customer_id: int
    full_name: str
    phone: str
    house_no: str
    building: Optional[str] = None
    landmark: Optional[str] = None
    area: str
    city: str
    state: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
