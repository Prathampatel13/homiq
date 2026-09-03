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


class BookingServiceNested(BaseModel):
    id: int
    name: str
    base_price: float
    model_config = {"from_attributes": True}

class BookingTechnicianNested(BaseModel):
    id: int
    user_id: int
    model_config = {"from_attributes": True}

class BookingAddressNested(BaseModel):
    id: int
    full_name: str
    phone: str
    house_no: str
    area: str
    city: str
    state: str
    pincode: str
    model_config = {"from_attributes": True}

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

    service: Optional[BookingServiceNested] = None
    technician: Optional[BookingTechnicianNested] = None
    address: Optional[BookingAddressNested] = None

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int = Field(..., ge=0)

    model_config = {"from_attributes": True}


# ─── Booking Lifecycle (cancel / reschedule / reject) ─────────────────


class BookingCancelRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional reason for cancelling the booking.",
    )


class BookingRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional reason for rejecting the booking.",
    )


class BookingRescheduleRequest(BaseModel):
    booking_date: date = Field(..., description="New booking date")
    preferred_time: Optional[time] = Field(None, description="New preferred time slot")

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        today = date.today()
        if v < today:
            raise ValueError("booking_date cannot be in the past")
        return v


# ─── Booking History ──────────────────────────────────────────────────


class BookingHistoryEntry(BaseModel):
    id: int
    booking_id: int
    old_status: Optional[BookingStatus]
    new_status: BookingStatus
    changed_by_user_id: Optional[int]
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingHistoryResponse(BaseModel):
    items: List[BookingHistoryEntry]
    total: int = Field(..., ge=0)

    model_config = {"from_attributes": True}


# ─── Assigned Technician ──────────────────────────────────────────────


class AssignedTechnicianResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── SmartVerify QR & OTP Schemas ─────────────────────────────────────


class QRDataPayload(BaseModel):
    booking_id: int
    booking_uuid: str
    verification_token: str
    expires_at: datetime
    version: str = "1.0"


class QRGenerateResponse(BaseModel):
    booking_id: int
    qr_code_data: str
    verification_token: str
    expires_at: datetime
    version: str = "1.0"
    message: str = "QR code generated successfully"


from pydantic import model_validator
from typing import Any

class QRScanRequest(BaseModel):
    verification_token: str = ""
    qr_token: Optional[str] = None
    device_info: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_token_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("verification_token") and data.get("qr_token"):
                data["verification_token"] = data["qr_token"]
        return data


class QRScanResponse(BaseModel):
    booking_id: int
    scanned_at: datetime
    technician_id: int
    status: str = "qr_verified"
    message: str = "QR code verified successfully. Please enter OTP to start service."


class OTPGenerateResponse(BaseModel):
    booking_id: int
    otp_code: Optional[str] = None
    expires_at: datetime
    message: str = "OTP generated successfully and sent to customer"


class OTPVerifyRequest(BaseModel):
    otp_code: str = ""
    otp: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_otp_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("otp_code") and data.get("otp"):
                data["otp_code"] = str(data["otp"])
        return data


class OTPVerifyResponse(BaseModel):
    booking_id: int
    verified_at: datetime
    status: str = "in_progress"
    message: str = "OTP verified successfully. Service is now in progress."


class SmartVerifyStatusResponse(BaseModel):
    booking_id: int
    booking_status: str
    is_qr_generated: bool = False
    is_qr_scanned: bool = False
    is_otp_generated: bool = False
    is_otp_verified: bool = False
    qr_expires_at: Optional[datetime] = None
    otp_expires_at: Optional[datetime] = None
    attempts_remaining: int = 3

