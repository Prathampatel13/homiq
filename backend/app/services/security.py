from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.schemas.security import AuditLogListResponse, AuditLogResponse

logger = logging.getLogger("homiq.security.audit")

SENSITIVE_KEYS = {
    "password", "old_password", "new_password", "confirm_password",
    "card_number", "cvv", "cvc", "pin", "token", "access_token", "refresh_token",
    "secret", "api_key"
}


def mask_sensitive_data(data: Any) -> Any:
    """Recursively mask sensitive keys in dictionaries/lists for security logging."""
    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if k.lower() in SENSITIVE_KEYS:
                masked[k] = "***MASKED***"
            else:
                masked[k] = mask_sensitive_data(v)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


class SecurityAuditService:
    """Service for persistent Security Audit Logging and Sensitive Data Masking."""

    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        action: str,
        user_id: Optional[int] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = "127.0.0.1",
        user_agent: Optional[str] = "Unknown",
        details: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        """Persist a security audit log entry with masked details."""
        masked_details_str = None
        if details is not None:
            masked = mask_sensitive_data(details)
            masked_details_str = json.dumps(masked)

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=masked_details_str,
        )
        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)
        return audit_entry

    def list_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        status_filter: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> AuditLogListResponse:
        """Query paginated security audit log entries."""
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)

        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)

        if status_filter:
            query = query.where(AuditLog.status == status_filter)
            count_query = count_query.where(AuditLog.status == status_filter)

        total = self.db.scalar(count_query) or 0
        rows = self.db.execute(
            query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        ).scalars().all()

        items = [AuditLogResponse.model_validate(row) for row in rows]
        return AuditLogListResponse(items=items, total=total)
