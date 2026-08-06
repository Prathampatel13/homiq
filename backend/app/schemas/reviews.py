from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    technician_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=2000)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    technician_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int

    model_config = {"from_attributes": True}


# ─── Reviews & Ratings Extensions ─────────────────────────────────────────


class RatingDistributionBreakdown(BaseModel):
    star_5: int = 0
    star_4: int = 0
    star_3: int = 0
    star_2: int = 0
    star_1: int = 0


class TechnicianRatingSummaryResponse(BaseModel):
    technician_id: int
    average_rating: float = 0.0
    total_reviews: int = 0
    distribution: RatingDistributionBreakdown

    model_config = {"from_attributes": True}


class ReviewPatch(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


