from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.bookings import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    BookingUpdate,
    BookingAssignTechnician,
    BookingStatusUpdate,
)
from app.services.booking import BookingService


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description="Create a booking as an authenticated customer.",
)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).create_booking(current_user, payload)


@router.get(
    "/",
    response_model=BookingListResponse,
    summary="List bookings",
    description="List bookings visible to the current user (admin sees all).",
)
def list_bookings(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).list_bookings(current_user, offset=offset, limit=limit)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking",
)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).get_booking(current_user, booking_id)


@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Update booking",
)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).update_booking(current_user, booking_id, payload)


@router.delete(
    "/{booking_id}",
    summary="Delete booking",
)
def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).delete_booking(current_user, booking_id)


@router.put(
    "/{booking_id}/assign",
    response_model=BookingResponse,
    summary="Assign technician",
    description="Admin-only: assign a technician to a booking.",
)
def assign_technician(
    booking_id: int,
    payload: BookingAssignTechnician,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).assign_technician(current_user, booking_id, payload.technician_id)


@router.put(
    "/{booking_id}/status",
    response_model=BookingResponse,
    summary="Update booking status",
)
def update_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BookingService(db).update_status(current_user, booking_id, payload.status)
