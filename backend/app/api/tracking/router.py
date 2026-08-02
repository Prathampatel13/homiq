"""
Live tracking endpoints.

Technicians: Update their live location for a booking.
Customers: View technician's live location and ETA for their booking.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.tracking import (
    TechnicianLocationUpdate,
    TechnicianLocationResponse,
    TrackingHistoryResponse,
)
from app.services.tracking import TrackingService

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.put(
    "/{booking_id}/location",
    response_model=TechnicianLocationResponse,
    summary="Update technician location",
    description="**Technician only.** Updates the live location for a booking. Also updates the technician's stored location.",
)
def update_location(
    booking_id: int,
    payload: TechnicianLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update the live location for a booking (technician only)."""
    return TrackingService(db).update_location(current_user, booking_id, payload)


@router.get(
    "/{booking_id}/location",
    response_model=TechnicianLocationResponse,
    summary="Get technician location",
    description="Returns the latest tracked location for a booking. Includes approximate ETA. Accessible by the customer, technician, or admin.",
)
def get_latest_location(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get the latest location for a booking."""
    return TrackingService(db).get_latest_location(current_user, booking_id)


@router.get(
    "/{booking_id}/history",
    response_model=TrackingHistoryResponse,
    summary="Get tracking history",
    description="Returns the full tracking event history for a booking. Accessible by the customer, technician, or admin.",
)
def get_tracking_history(
    booking_id: int,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get tracking history for a booking."""
    return TrackingService(db).get_tracking_history(
        current_user, booking_id, offset=offset, limit=limit
    )


@router.get(
    "/me/location",
    response_model=TechnicianLocationResponse,
    summary="Get my current location (Technician)",
    description="**Technician only.** Returns the current tracked location of the authenticated technician.",
)
def get_my_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get the current location of the authenticated technician."""
    return TrackingService(db).get_technician_current_location(current_user)

