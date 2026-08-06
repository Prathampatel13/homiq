from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    device_name: str
    ip_address: str
    user_agent: str
    logged_in_at: str
    last_active_at: str

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    details: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
