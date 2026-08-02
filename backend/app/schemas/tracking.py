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

