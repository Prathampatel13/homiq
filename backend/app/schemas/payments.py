from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.models.payments import PaymentMethod, PaymentStatus


class PaymentCreateOrder(BaseModel):
    booking_id: Optional[int] = Field(None, gt=0)
    amount: Optional[int] = Field(None, description="Amount in paise (min 100 paise = 1 INR)")
    currency: Optional[str] = Field("INR", description="Currency code (e.g. INR)")
    receipt: Optional[str] = Field(None, description="Optional receipt identifier")
    notes: Optional[dict[str, Any]] = None


class DemoPayRequest(BaseModel):
    booking_id: int
    payment_method: str = "online_demo"


class StandardOrderCreateRequest(BaseModel):
    amount: int = Field(..., ge=100, description="Amount in paise (minimum 100 paise)")
    currency: str = Field(default="INR", description="Currency code (e.g. INR)")
    receipt: Optional[str] = Field(None, description="Receipt identifier")
    notes: Optional[dict[str, Any]] = None


class StandardOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    id: Optional[str] = None
    key_id: Optional[str] = None
    receipt: Optional[str] = None
    status: str = "created"

    @model_validator(mode="before")
    @classmethod
    def set_id_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("order_id"):
                data["id"] = data["order_id"]
            if not data.get("order_id") and data.get("id"):
                data["order_id"] = data["id"]
        return data


class PaymentVerify(BaseModel):
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None


class StandardVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_signature: str = Field(..., description="HMAC-SHA256 signature")


class StandardVerifyResponse(BaseModel):
    success: bool = True
    message: str = "Payment verified successfully."
    order_id: str
    payment_id: str
    status: str = "paid"


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