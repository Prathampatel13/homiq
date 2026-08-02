from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CouponCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, description="Unique coupon code")
    description: Optional[str] = Field(None, max_length=1000)
    discount_type: str = Field(default="percentage", pattern=r"^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0, description="Discount value (percentage or fixed amount)")
    min_order_value: Optional[float] = Field(0, ge=0)
    max_discount: Optional[float] = Field(None, ge=0, description="Maximum discount for percentage coupons")
    usage_limit: Optional[int] = Field(None, ge=1, description="Total usage limit")
    per_user_limit: int = Field(default=1, ge=1)
    is_active: bool = Field(default=True)
    valid_from: date = Field(..., description="Start date of coupon validity")
    valid_until: date = Field(..., description="End date of coupon validity")
    applicable_services: Optional[str] = Field(None, description="JSON list of applicable service IDs")

    @field_validator("valid_until")
    @classmethod
    def validate_valid_until(cls, v: date, info) -> date:
        values = info.data
        if "valid_from" in values and v < values["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v


class CouponUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    discount_type: Optional[str] = Field(None, pattern=r"^(percentage|fixed)$")
    discount_value: Optional[float] = Field(None, gt=0)
    min_order_value: Optional[float] = Field(None, ge=0)
    max_discount: Optional[float] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    per_user_limit: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    applicable_services: Optional[str] = None

    @field_validator("valid_until")
    @classmethod
    def validate_valid_until(cls, v: Optional[date], info) -> Optional[date]:
        if v is None:
            return v
        values = info.data
        if "valid_from" in values and values["valid_from"] and v < values["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v


class CouponResponse(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    usage_count: int
    per_user_limit: int
    is_active: bool
    valid_from: date
    valid_until: date
    applicable_services: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CouponListResponse(BaseModel):
    items: list[CouponResponse]
    total: int

    model_config = {"from_attributes": True}


class CouponValidateRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    booking_id: int = Field(..., gt=0)


class CouponValidateResponse(BaseModel):
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: float = 0.0
    message: str = ""

