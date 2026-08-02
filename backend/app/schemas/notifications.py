from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
    notification_ids: list[int] = Field(..., min_length=1, description="List of notification IDs to mark as read")

