from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional


class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int = 0

    model_config = {"from_attributes": True}


class NotificationMarkRead(BaseModel):
    notification_ids: list[int] = Field(default_factory=list)
    ids: Optional[list[int]] = None

    @model_validator(mode="before")
    @classmethod
    def handle_ids_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("notification_ids") and data.get("ids"):
                data["notification_ids"] = data["ids"]
        return data


# ─── Notification System Extensions ─────────────────────────────────────


class UnreadNotificationsResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int

    model_config = {"from_attributes": True}


class MultiChannelNotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    channels: list[str] = Field(default_factory=lambda: ["email", "sms", "push", "in_app"])
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    fcm_token: Optional[str] = None
    data: Optional[dict] = None


class NotificationDispatchResult(BaseModel):
    user_id: int
    title: str
    channels_sent: list[str]
    email_status: str = "skipped"
    sms_status: str = "skipped"
    push_status: str = "skipped"
    in_app_status: str = "skipped"


