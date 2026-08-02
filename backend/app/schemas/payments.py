from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.payments import PaymentMethod, PaymentStatus


class PaymentCreateOrder(BaseModel):
    booking_id: int = Field(..., gt=0)


class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    customer_id: int

    amount: float
    currency: str

    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None

    payment_method: PaymentMethod
    status: PaymentStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int