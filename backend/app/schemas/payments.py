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


# ─── Payment Extensions (Refund, Webhook, History, Invoice) ──────────────


class PaymentRefundRequest(BaseModel):
    payment_id: int = Field(..., gt=0)
    reason: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)


class PaymentWebhookPayload(BaseModel):
    event: str
    payload: dict = Field(default_factory=dict)


class PaymentHistoryEntry(BaseModel):
    id: int
    booking_id: int
    booking_number: Optional[str] = None
    service_name: Optional[str] = None
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentHistoryResponse(BaseModel):
    items: list[PaymentHistoryEntry]
    total: int


class PaymentInvoiceResponse(BaseModel):
    invoice_id: int
    invoice_number: str
    booking_id: int
    customer_name: str
    technician_name: Optional[str] = None
    service_name: str
    subtotal: float
    gst_amount: float
    discount_amount: float
    total_amount: float
    payment_method: str
    status: str
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)