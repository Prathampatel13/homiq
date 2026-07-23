from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.bookings import BookingStatus, PaymentStatus


class BookingCreate(BaseModel):
    service_id: int = Field(..., description="Service id for this booking")
    address_id: int = Field(..., description="Customer address id")
    booking_date: date = Field(..., description="Booking date")
    preferred_time: Optional[time] = Field(None, description="Preferred time slot")
    estimated_price: Optional[float] = Field(None, ge=0)
    customer_note: Optional[str] = Field(None, max_length=2000)

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        today = date.today()
        if v < today:
            raise ValueError("booking_date cannot be in the past")
        return v


class BookingUpdate(BaseModel):
    booking_date: Optional[date] = None
    preferred_time: Optional[time] = None
    address_id: Optional[int] = None
    estimated_price: Optional[float] = Field(None, ge=0)
    final_price: Optional[float] = Field(None, ge=0)
    customer_note: Optional[str] = Field(None, max_length=2000)
    admin_note: Optional[str] = Field(None, max_length=2000)

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = date.today()
        if v < today:
            raise ValueError("booking_date cannot be in the past")
        return v


class BookingAssignTechnician(BaseModel):
    technician_id: int = Field(..., description="Technician user id to assign")
    estimated_price: Optional[float] = Field(None, ge=0)
    final_price: Optional[float] = Field(None, ge=0)


class BookingStatusUpdate(BaseModel):
    status: BookingStatus = Field(..., description="New booking status")
    admin_note: Optional[str] = Field(None, max_length=2000)


class BookingResponse(BaseModel):
    id: int
    booking_number: str
    customer_id: int
    technician_id: Optional[int]
    service_id: int
    address_id: int
    booking_date: date
    preferred_time: Optional[time]
    estimated_price: Optional[float]
    final_price: Optional[float]
    status: BookingStatus
    payment_status: PaymentStatus
    customer_note: Optional[str]
    admin_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int = Field(..., ge=0)

    model_config = {"from_attributes": True}
