from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Availability / Online status ───────────────────────────────────────


class TechnicianAvailabilityUpdate(BaseModel):
    availability: Optional[bool] = Field(None, description="Whether the technician is available for new jobs")
    is_online: Optional[bool] = Field(None, description="Whether the technician is currently online")


class TechnicianAvailabilityResponse(BaseModel):
    availability: bool
    is_online: bool


# ── Technician Jobs ────────────────────────────────────────────────────


class TechnicianJobCustomer(BaseModel):
    id: int
    full_name: str
    phone: Optional[str] = None


class TechnicianJobService(BaseModel):
    id: int
    name: str


class TechnicianJobAddress(BaseModel):
    house_no: Optional[str] = None
    building: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TechnicianJobResponse(BaseModel):
    id: int
    booking_number: str
    status: str
    payment_status: str
    booking_date: date
    preferred_time: Optional[time] = None
    estimated_price: Optional[float] = None
    final_price: Optional[float] = None
    customer_note: Optional[str] = None
    admin_note: Optional[str] = None
    created_at: datetime
    customer: Optional[TechnicianJobCustomer] = None
    service: Optional[TechnicianJobService] = None
    address: Optional[TechnicianJobAddress] = None


class TechnicianJobListResponse(BaseModel):
    items: list[TechnicianJobResponse]
    total: int


# ── Earnings ───────────────────────────────────────────────────────────


class TechnicianEarningsResponse(BaseModel):
    total_earnings: float = 0.0
    pending_earnings: float = 0.0
    completed_jobs: int = 0
    paid_jobs: int = 0
    pending_jobs: int = 0


class TechnicianCreate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=255)
    experience_years: Optional[int] = Field(None, ge=0, le=100)
    skills: Optional[list[str]] = Field(None, description="List of skills")
    languages: Optional[list[str]] = Field(None, description="Supported languages")
    working_hours: Optional[str] = Field(None, max_length=255)
    availability: Optional[bool] = Field(None)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    service_radius_km: Optional[float] = Field(None, ge=0, le=500)
    is_online: Optional[bool] = Field(None)


class TechnicianUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    specialization: Optional[str] = Field(None, max_length=255)
    experience_years: Optional[int] = Field(None, ge=0, le=100)
    skills: Optional[list[str]] = Field(None, description="List of skills")
    languages: Optional[list[str]] = Field(None, description="Supported languages")
    working_hours: Optional[str] = Field(None, max_length=255)
    availability: Optional[bool] = Field(None)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    service_radius_km: Optional[float] = Field(None, ge=0, le=500)
    is_online: Optional[bool] = Field(None)


class TechnicianResponse(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    specialization: Optional[str] = None
    experience_years: int
    skills: list[str] = []
    languages: list[str] = []
    working_hours: Optional[str] = None
    availability: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_radius_km: Optional[float] = None
    is_online: bool
    is_verified: bool = False
    rating: float
    reviews_count: int
    profile_image: Optional[str] = None
    government_id_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileImageResponse(BaseModel):
    profile_image: str
    message: str = "Profile image uploaded successfully"


class GovernmentIdImageResponse(BaseModel):
    government_id_image: str
    message: str = "Government ID uploaded successfully"


class TechnicianActionRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Optional reason or note for the status change")

