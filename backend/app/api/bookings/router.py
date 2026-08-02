"""
Booking management endpoints.

All endpoints are JWT-protected and require a valid Bearer token.
Admins have full access; customers and technicians have role-scoped access.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.bookings import (
    BookingAssignTechnician,
    BookingCreate,
    BookingListResponse,
    BookingResponse,
    BookingStatusUpdate,
    BookingUpdate,
)
from app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ─── CREATE ────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description=(
        "Creates a new service booking for the authenticated customer. "
        "A unique booking number is auto-generated. "
        "The booking date must not be in the past. "
        "The service and address must exist and belong to the customer."
    ),
    response_description="The created booking details.",
)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new booking for the authenticated customer.

    Args:
        payload: Booking creation payload (service_id, address_id, booking_date, etc.).
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        BookingResponse: The newly created booking.

    Raises:
        401: If not authenticated.
        404: If the service or address is not found.
        400: If the booking date is in the past or validation fails.
    """
    return BookingService(db).create_booking(current_user, payload)


# ─── LIST ──────────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=BookingListResponse,
    summary="List bookings",
    description=(
        "Returns a paginated list of bookings visible to the current user. "
        "Admins see all bookings. Customers see only their own bookings. "
        "Technicians see bookings assigned to them."
    ),
    response_description="Paginated list of bookings with total count.",
)
def list_bookings(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List bookings with pagination, scoped to the current user's role.

    Args:
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (default 100).
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        BookingListResponse: A list of bookings and the total count.

    Raises:
        401: If not authenticated.
    """
    return BookingService(db).list_bookings(current_user, offset=offset, limit=limit)


# ─── GET BY ID ─────────────────────────────────────────────────────────


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking by ID",
    description=(
        "Returns the full details of a single booking by its ID. "
        "Access is restricted to the booking owner (customer), "
        "the assigned technician, or an admin."
    ),
    response_description="The requested booking details.",
)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a single booking by its ID.

    Args:
        booking_id: The unique booking ID.
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        BookingResponse: The booking details.

    Raises:
        401: If not authenticated.
        403: If not authorized to view this booking.
        404: If the booking is not found.
    """
    return BookingService(db).get_booking(current_user, booking_id)


# ─── UPDATE ────────────────────────────────────────────────────────────


@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Update booking",
    description=(
        "Updates one or more fields of an existing booking. "
        "Only the booking owner (customer) or an admin can update. "
        "Customers cannot change the technician. "
        "Supports partial updates \u2014 only provided fields are modified."
    ),
    response_description="The updated booking details.",
)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update an existing booking with partial payload.

    Args:
        booking_id: The unique booking ID.
        payload: Fields to update (partial).
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        BookingResponse: The updated booking.

    Raises:
        401: If not authenticated.
        403: If not authorized to update.
        404: If the booking is not found.
        400: If no valid fields provided or validation fails.
    """
    return BookingService(db).update_booking(current_user, booking_id, payload)


# ─── DELETE ────────────────────────────────────────────────────────────


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete booking",
    description=(
        "Deletes a booking by its ID. "
        "Only the booking owner (customer) or an admin can delete. "
        "Returns a confirmation message on success."
    ),
    response_description="Confirmation message.",
)
def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a booking by its ID.

    Args:
        booking_id: The unique booking ID.
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        dict: A confirmation message.

    Raises:
        401: If not authenticated.
        403: If not authorized to delete.
        404: If the booking is not found.
    """
    return BookingService(db).delete_booking(current_user, booking_id)


# ─── ASSIGN TECHNICIAN ────────────────────────────────────────────────


@router.put(
    "/{booking_id}/assign",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign technician to booking",
    description=(
        "**Admin-only.** Assigns a technician to a booking. "
        "The booking must be in 'pending' status. "
        "The booking status is automatically updated to 'assigned'. "
        "The technician must exist in the system."
    ),
    response_description="The updated booking with assigned technician.",
)
def assign_technician(
    booking_id: int,
    payload: BookingAssignTechnician,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Assign a technician to a booking (admin only).

    Args:
        booking_id: The unique booking ID.
        payload: Contains the technician_id to assign.
        current_user: Authenticated user (JWT-protected, must be admin).
        db: Database session.

    Returns:
        BookingResponse: The updated booking with technician assigned.

    Raises:
        401: If not authenticated.
        403: If not an admin.
        404: If the booking is not found.
        400: If the booking is not in pending status or assignment fails.
    """
    return BookingService(db).assign_technician(current_user, booking_id, payload)


# ─── UPDATE STATUS ─────────────────────────────────────────────────────


@router.put(
    "/{booking_id}/status",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Update booking status",
    description=(
        "Updates the status of a booking following the allowed state machine. "
        "Only the assigned technician or an admin can change the status. "
        "Valid transitions:\n"
        "- pending \u2192 (no direct transitions; use admin assign)\n"
        "- assigned \u2192 accepted | cancelled\n"
        "- accepted \u2192 in_progress | cancelled\n"
        "- in_progress \u2192 completed | cancelled\n"
        "- completed \u2192 (no further transitions)\n"
        "- cancelled \u2192 (no further transitions)"
    ),
    response_description="The updated booking with new status.",
)
def update_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update the status of a booking using the allowed state machine.

    Valid transitions:
    - Pending -> (no direct transition; use assign endpoint)
    - Assigned -> Accepted | Cancelled
    - Accepted -> In Progress | Cancelled
    - In Progress -> Completed | Cancelled

    Args:
        booking_id: The unique booking ID.
        payload: Contains the new status and optional admin note.
        current_user: Authenticated user (JWT-protected, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The updated booking with new status.

    Raises:
        401: If not authenticated.
        403: If not authorized to update status.
        404: If the booking is not found.
        400: If the status transition is invalid.
    """
    return BookingService(db).update_status(
        current_user, booking_id, payload.status, admin_note=payload.admin_note
    )

