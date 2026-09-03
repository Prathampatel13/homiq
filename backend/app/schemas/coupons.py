from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    applicable_services: Optional[str] = Field(None, description="JSON list of applicable service IDs")

    @model_validator(mode="before")
    @classmethod
    def handle_aliases_and_dates(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "max_discount_amount" in data and "max_discount" not in data:
                data["max_discount"] = data["max_discount_amount"]
            if "min_order_amount" in data and "min_order_value" not in data:
                data["min_order_value"] = data["min_order_amount"]
            if "usage_limit_per_user" in data and "per_user_limit" not in data:
                data["per_user_limit"] = data["usage_limit_per_user"]
            if not data.get("valid_from"):
                data["valid_from"] = date.today()
            if not data.get("valid_until"):
                data["valid_until"] = date.today() + timedelta(days=365)
        return data

    @field_validator("valid_until")
    @classmethod
    def validate_valid_until(cls, v: Optional[date], info) -> Optional[date]:
        values = info.data
        if v and "valid_from" in values and values["valid_from"] and v < values["valid_from"]:
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
    booking_id: Optional[int] = None
    amount: Optional[float] = None
    service_id: Optional[int] = None


class CouponValidateResponse(BaseModel):
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: float = 0.0
    message: str = ""

