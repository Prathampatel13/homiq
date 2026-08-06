"""Company profile schemas.

Defines the update request and response models for the ``Company`` profile.
The ``Company`` model lives in :mod:`app.models.users` and the ``companies``
table already exists in the database.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    website: Optional[str] = Field(None, max_length=255)

    @field_validator("website")
    @classmethod
    def validate_website(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Website cannot be empty")
        return normalized


class CompanyProfileResponse(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
