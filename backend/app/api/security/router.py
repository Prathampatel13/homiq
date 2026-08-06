from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.schemas.security import (
    AuditLogListResponse,
    SessionListResponse,
    SessionResponse,
)
from app.security.deps import get_current_user
from app.security.sessions import session_tracker
from app.services.security import SecurityAuditService

router = APIRouter(prefix="/security", tags=["Enterprise Security Management"])


# ── 1. ACTIVE SESSIONS ─────────────────────────────────────────────────────

@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List active device sessions",
    description="Returns all active login device sessions for the authenticated user.",
)
def get_active_sessions(
    current_user: User = Depends(get_current_user),
) -> Any:
    """List all active login device sessions for the current user."""
    sessions_data = session_tracker.get_active_sessions(current_user.id)
    items = [SessionResponse.model_validate(s) for s in sessions_data]
    return SessionListResponse(items=items, total=len(items))


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Revoke a specific device session",
    description="Revokes a single active login session by session_id.",
)
def revoke_device_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Revoke a specific device session."""
    revoked = session_tracker.revoke_session(current_user.id, session_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found or already revoked.",
        )
    return {"status": "success", "message": f"Session {session_id} revoked successfully."}


@router.delete(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Revoke all active device sessions",
    description="Logs out all active device sessions for the authenticated user.",
)
def logout_all_devices(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Revoke all active sessions for the current user."""
    count = session_tracker.revoke_all_sessions(current_user.id)
    return {
        "status": "success",
        "message": f"All {count} active sessions revoked successfully.",
        "revoked_count": count,
    }


# ── 2. AUDIT LOGS ──────────────────────────────────────────────────────────

@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="Query security audit logs",
    description="Returns paginated security audit log entries. Admins view all logs, regular users view their own logs.",
)
def query_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action type (LOGIN, FAILED_LOGIN, etc.)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (SUCCESS, FAILURE, DENIED)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Query security audit logs."""
    service = SecurityAuditService(db)
    user_id_filter = None if current_user.is_superuser else current_user.id
    return service.list_logs(
        user_id=user_id_filter,
        action=action,
        status_filter=status_filter,
        offset=offset,
        limit=limit,
    )
