"""
Booking management endpoints.

All endpoints are JWT-protected and require a valid Bearer token.
Admins have full access; customers and technicians have role-scoped access.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.bookings import (
    AssignedTechnicianResponse,
    BookingAssignTechnician,
    BookingCancelRequest,
    BookingCreate,
    BookingHistoryResponse,
    BookingListResponse,
    BookingRejectRequest,
    BookingRescheduleRequest,
    BookingResponse,
    BookingStatusUpdate,
    BookingUpdate,
    OTPGenerateResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
    QRGenerateResponse,
    QRScanRequest,
    QRScanResponse,
    SmartVerifyStatusResponse,
    VerificationDetailsResponse,
    VerifyCodeRequest,
)
from app.services.booking import BookingService
from app.services.smart_verify import SmartVerifyService

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
        BookingListResponse: Paginated list of bookings.
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


# ─── CUSTOMER: CANCEL ────────────────────────────────────────────────


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a booking",
    description=(
        "Cancels an existing booking. The booking owner (customer) or an "
        "admin may cancel. Customers may only cancel from the "
        "pending / assigned / accepted / on_the_way statuses. "
        "Returns 409 if the booking cannot be cancelled from its current status."
    ),
    response_description="The cancelled booking details.",
)
def cancel_booking(
    booking_id: int,
    payload: BookingCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Cancel a booking.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for cancellation.
        current_user: Authenticated user (JWT).
        db: Database session.

    Returns:
        BookingResponse: The cancelled booking.

    Raises:
        401: If not authenticated.
        403: If not authorized to cancel.
        404: If the booking is not found.
        409: If the booking cannot be cancelled from its current status.
    """
    return BookingService(db).cancel_booking(current_user, booking_id, payload)


# ─── CUSTOMER: RESCHEDULE ────────────────────────────────────────────


@router.put(
    "/{booking_id}/reschedule",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Reschedule a booking",
    description=(
        "Reschedules an existing booking to a new date/time. The booking "
        "owner (customer) or an admin may reschedule. Customers may only "
        "reschedule from the pending / assigned / accepted statuses."
    ),
    response_description="The rescheduled booking details.",
)
def reschedule_booking(
    booking_id: int,
    payload: BookingRescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Reschedule a booking.

    Args:
        booking_id: The unique booking ID.
        payload: New booking date and preferred time.
        current_user: Authenticated user (JWT).
        db: Database session.

    Returns:
        BookingResponse: The rescheduled booking.

    Raises:
        401: If not authenticated.
        403: If not authorized to reschedule.
        404: If the booking is not found.
        409: If the booking cannot be rescheduled from its current status.
    """
    return BookingService(db).reschedule_booking(current_user, booking_id, payload)


# ─── CUSTOMER: HISTORY ───────────────────────────────────────────────


@router.get(
    "/{booking_id}/history",
    response_model=BookingHistoryResponse,
    summary="Booking history",
    description=(
        "Returns the status-change history (audit trail) for a booking. "
        "Access is restricted to the booking owner, the assigned "
        "technician, or an admin."
    ),
    response_description="The booking's status-change history.",
)
def get_booking_history(
    booking_id: int,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get the status-change history for a booking.

    Args:
        booking_id: The unique booking ID.
        offset: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        current_user: Authenticated user (JWT).
        db: Database session.

    Returns:
        BookingHistoryResponse: The booking's status-change history.

    Raises:
        401: If not authenticated.
        403: If not authorized to view.
        404: If the booking is not found.
    """
    return BookingService(db).get_booking_history(
        current_user, booking_id, offset=offset, limit=limit
    )


# ─── CUSTOMER: TRACK ─────────────────────────────────────────────────


@router.get(
    "/{booking_id}/track",
    response_model=BookingResponse,
    summary="Track a booking",
    description=(
        "Returns the current state of a booking for live tracking. "
        "Access is restricted to the booking owner, the assigned "
        "technician, or an admin."
    ),
    response_description="The current booking details.",
)
def track_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Track a booking.

    Args:
        booking_id: The unique booking ID.
        current_user: Authenticated user (JWT).
        db: Database session.

    Returns:
        BookingResponse: The current booking details.

    Raises:
        401: If not authenticated.
        403: If not authorized to view.
        404: If the booking is not found.
    """
    return BookingService(db).track_booking(current_user, booking_id)


# ─── CUSTOMER: ASSIGNED TECHNICIAN ───────────────────────────────────


@router.get(
    "/{booking_id}/technician",
    response_model=AssignedTechnicianResponse,
    summary="View assigned technician",
    description=(
        "Returns the technician assigned to a booking. Access is "
        "restricted to the booking owner, the assigned technician, or an admin."
    ),
    response_description="The assigned technician's details.",
)
def get_assigned_technician(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """View the technician assigned to a booking.

    Args:
        booking_id: The unique booking ID.
        current_user: Authenticated user (JWT).
        db: Database session.

    Returns:
        AssignedTechnicianResponse: The assigned technician's details.

    Raises:
        401: If not authenticated.
        403: If not authorized to view.
        404: If the booking or technician is not found.
    """
    return BookingService(db).get_assigned_technician(current_user, booking_id)


# ─── TECHNICIAN: ACCEPT ──────────────────────────────────────────────


@router.post(
    "/{booking_id}/accept",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept a booking",
    description=(
        "Accepts an assigned booking. Only the assigned technician or an "
        "admin may accept. The booking must be in 'assigned' status."
    ),
    response_description="The accepted booking details.",
)
def accept_booking(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Accept an assigned booking.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the action.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The accepted booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).accept_booking(current_user, booking_id, payload)


# ─── TECHNICIAN: REJECT ──────────────────────────────────────────────


@router.post(
    "/{booking_id}/reject",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a booking",
    description=(
        "Rejects an assigned booking. Only the assigned technician or an "
        "admin may reject. The booking must be in 'assigned' status."
    ),
    response_description="The rejected booking details.",
)
def reject_booking(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Reject an assigned booking.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the rejection.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The rejected booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).reject_booking(current_user, booking_id, payload)


# ─── TECHNICIAN: START TRIP ──────────────────────────────────────────


@router.post(
    "/{booking_id}/start-trip",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Start trip",
    description=(
        "Marks the technician as 'on the way'. Only the assigned "
        "technician or an admin may start the trip. The booking must be "
        "in 'accepted' status."
    ),
    response_description="The updated booking details.",
)
def start_trip(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark the technician as on the way.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the action.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The updated booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).start_trip(current_user, booking_id, payload)


# ─── TECHNICIAN: ARRIVED ─────────────────────────────────────────────


@router.post(
    "/{booking_id}/arrived",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark arrived",
    description=(
        "Marks the technician as arrived. Only the assigned technician or "
        "an admin may mark arrived. The booking must be in 'on_the_way' status."
    ),
    response_description="The updated booking details.",
)
def mark_arrived(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark the technician as arrived.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the action.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The updated booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).mark_arrived(current_user, booking_id, payload)


# ─── TECHNICIAN: START SERVICE ───────────────────────────────────────


@router.post(
    "/{booking_id}/start-service",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Start service",
    description=(
        "Starts the service for a booking. Only the assigned technician or "
        "an admin may start the service. The booking must be in "
        "'qr_verified' status."
    ),
    response_description="The updated booking details.",
)
def start_service(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Start the service for a booking.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the action.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The updated booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).start_service(current_user, booking_id, payload)


# ─── TECHNICIAN: COMPLETE SERVICE ────────────────────────────────────


@router.post(
    "/{booking_id}/complete",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete service",
    description=(
        "Completes the service for a booking. Only the assigned technician "
        "or an admin may complete. The booking must be in 'in_progress' status."
    ),
    response_description="The completed booking details.",
)
def complete_service(
    booking_id: int,
    payload: Optional[BookingRejectRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Complete the service for a booking.

    Args:
        booking_id: The unique booking ID.
        payload: Reason for the action.
        current_user: Authenticated user (JWT, must be technician or admin).
        db: Database session.

    Returns:
        BookingResponse: The completed booking.

    Raises:
        401: If not authenticated.
        403: If not the assigned technician or admin.
        404: If the booking is not found.
        409: If the transition is invalid.
    """
    return BookingService(db).complete_service(current_user, booking_id, payload)



@router.post(
    "/{booking_id}/verify-code",
    response_model=BookingResponse,
    summary="Verify arrival passcode or QR token",
    description="Technician enters customer 6-digit passcode or scans QR token to confirm arrival and start service.",
)
def verify_code_endpoint(
    booking_id: int,
    payload: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    from app.services.booking import BookingService
    return BookingService(db).verify_arrival_code(current_user, booking_id, payload.code)


@router.get(
    "/{booking_id}/verification-details",
    response_model=VerificationDetailsResponse,
    summary="Get arrival verification details",
    description="Customer and technician retrieve 6-digit code, QR token, and live verification status.",
)
def get_verification_details_endpoint(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    from app.services.booking import BookingService
    return BookingService(db).get_verification_details(current_user, booking_id)


# ─── BOOKING MEDIA ENDPOINTS (Before, After, Attachments) ─────────────────

from fastapi import File, UploadFile
from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/{booking_id}/before-images",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload before-work photo",
    description="Uploads a photo of the site before service begins (Customer or Technician).",
)
def upload_booking_before_image(
    booking_id: int,
    file: UploadFile = File(..., description="Before image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload before-service photo."""
    return MediaService(db).upload_booking_before_image(current_user, booking_id, file)


@router.post(
    "/{booking_id}/after-images",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload after-work photo",
    description="Uploads a photo of completed work (Technician or Customer).",
)
def upload_booking_after_image(
    booking_id: int,
    file: UploadFile = File(..., description="After image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload after-service photo."""
    return MediaService(db).upload_booking_after_image(current_user, booking_id, file)


@router.post(
    "/{booking_id}/attachments",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload booking attachment/document",
    description="Uploads an invoice, blueprint, or document for the booking (Image or PDF).",
)
def upload_booking_attachment(
    booking_id: int,
    file: UploadFile = File(..., description="Attachment file (Image or PDF)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload booking attachment."""
    return MediaService(db).upload_booking_attachment(current_user, booking_id, file)


@router.get(
    "/{booking_id}/media",
    response_model=list[MediaAssetResponse],
    summary="List all booking media",
    description="Returns all before, after, and attachment media associated with the booking.",
)
def list_booking_media(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List booking media."""
    return MediaService(db).list_booking_media(current_user, booking_id)


@router.delete(
    "/{booking_id}/media/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete booking media asset",
    description="Deletes a media asset from a booking.",
)
def delete_booking_media(
    booking_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete booking media asset."""
    return MediaService(db).delete_booking_media(current_user, booking_id, asset_id)



