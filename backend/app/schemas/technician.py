from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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
