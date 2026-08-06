from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrackingEventCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    technician_id: Optional[int] = Field(None, gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    status: str = Field(..., min_length=1, max_length=50)


class TrackingEventResponse(BaseModel):
    id: int
    booking_id: int
    technician_id: Optional[int] = None
    latitude: float
    longitude: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TechnicianLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    status: str = Field(default="en_route", max_length=50)


class TechnicianLocationResponse(BaseModel):
    booking_id: int
    technician_id: int
    latitude: float
    longitude: float
    status: str
    last_updated: datetime
    eta_minutes: Optional[float] = None

    model_config = {"from_attributes": True}


class TrackingHistoryResponse(BaseModel):
    events: list[TrackingEventResponse]
    total: int

    model_config = {"from_attributes": True}


# ─── Location & Maps API Extensions ─────────────────────────────────────


class LocationUpdatePayload(BaseModel):
    booking_id: int = Field(..., gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0)
    status: str = Field(default="en_route", max_length=50)


class GeocodeResponse(BaseModel):
    formatted_address: str
    latitude: float
    longitude: float
    place_id: Optional[str] = None


class ReverseGeocodeResponse(BaseModel):
    formatted_address: str
    place_id: Optional[str] = None
    address_components: list[dict] = Field(default_factory=list)


class ETAResponse(BaseModel):
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    distance_km: Optional[float] = None
    duration_minutes: Optional[float] = None
    distance_text: str = "N/A"
    duration_text: str = "N/A"
    status: str = "OK"


class NearbyTechnicianItem(BaseModel):
    technician_id: int
    user_id: int
    full_name: str
    phone: Optional[str] = None
    latitude: float
    longitude: float
    distance_km: float
    eta_minutes: float
    is_online: bool
    is_busy: bool

    model_config = {"from_attributes": True}


class NearbyTechniciansResponse(BaseModel):
    technicians: list[NearbyTechnicianItem]
    total: int


