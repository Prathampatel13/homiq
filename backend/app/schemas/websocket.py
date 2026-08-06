from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WSEventTypeEnum(str, Enum):
    PING = "ping"
    PONG = "pong"
    STATUS_UPDATE = "status_update"
    LOCATION_UPDATE = "location_update"
    CHAT_MESSAGE = "chat_message"
    TYPING = "typing"
    READ_RECEIPT = "read_receipt"
    NOTIFICATION = "notification"
    ADMIN_ALERT = "admin_alert"
    ERROR = "error"


class WSMessage(BaseModel):
    event_type: WSEventTypeEnum
    payload: dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LocationPayload(BaseModel):
    booking_id: int
    technician_id: int
    latitude: float
    longitude: float
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    eta_minutes: Optional[int] = None

    model_config = {"from_attributes": True}


class ChatMessagePayload(BaseModel):
    message_id: str
    booking_id: int
    sender_id: int
    sender_role: str  # "customer", "technician", "admin"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "sent"  # "sent", "delivered", "read"

    model_config = {"from_attributes": True}


class TypingPayload(BaseModel):
    booking_id: int
    sender_id: int
    is_typing: bool

    model_config = {"from_attributes": True}


class StatusUpdatePayload(BaseModel):
    booking_id: int
    booking_number: str
    old_status: str
    new_status: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = {"from_attributes": True}


class SystemAlertPayload(BaseModel):
    alert_id: str
    severity: str = "info"  # "info", "warning", "critical"
    title: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = {"from_attributes": True}
