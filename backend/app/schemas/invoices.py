from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.invoices import InvoiceStatus


class InvoiceCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    subtotal: float = Field(..., ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    coupon_code: Optional[str] = Field(None, max_length=50)
    tax_percentage: float = Field(default=0.0, ge=0)
    total_amount: float = Field(..., ge=0)
    amount_paid: float = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    due_at: Optional[datetime] = None


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    amount_paid: Optional[float] = Field(None, ge=0)
    amount_due: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    booking_id: int
    customer_id: int
    payment_id: Optional[int] = None
    subtotal: float
    discount_amount: float
    coupon_code: Optional[str] = None
    tax_percentage: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    amount_due: float
    status: InvoiceStatus
    notes: Optional[str] = None
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int

    model_config = {"from_attributes": True}

