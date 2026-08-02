from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.tracking import TrackingCRUD
from app.crud.booking import BookingCRUD
from app.crud.technician import TechnicianCRUD
from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.schemas.tracking import (
    TechnicianLocationUpdate,
    TechnicianLocationResponse,
    TrackingEventResponse,
    TrackingHistoryResponse,
)


class TrackingService:
    """Service layer for live tracking operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = TrackingCRUD(db)
        self.booking_crud = BookingCRUD(db)
        self.technician_crud = TechnicianCRUD(db)
        self.customer_crud = CustomerCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    def _get_technician_id(self, current_user: User) -> int:
        technician = self.technician_crud.get_by_user_id(current_user.id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )
        return technician.id

    # ── Update Technician Location ─────────────────────────────────────

    def update_location(
        self,
        current_user: User,
        booking_id: int,
        payload: TechnicianLocationUpdate,
    ) -> TechnicianLocationResponse:
        """Update the live location of a technician for a booking."""
        technician_id = self._get_technician_id(current_user)

        # Verify technician is assigned to this booking
        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.technician_id != technician_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this booking.",
            )

        # Create tracking event
        event = self.crud.create_event({
            "booking_id": booking_id,
            "technician_id": technician_id,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "status": payload.status,
        })

        # Update technician's current location
        self.technician_crud.update(
            technician_id,
            {"latitude": payload.latitude, "longitude": payload.longitude},
        )

        return TechnicianLocationResponse(
            booking_id=booking_id,
            technician_id=technician_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status=payload.status,
            last_updated=event.created_at,
        )

    # ── Get Latest Location ────────────────────────────────────────────

    def get_latest_location(
        self,
        current_user: User,
        booking_id: int,
    ) -> TechnicianLocationResponse:
        """Get the latest tracked location for a booking."""
        # Verify access
        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        # Check if user is customer (owner) or technician or admin
        is_customer = False
        is_technician = False
        if not current_user.is_superuser:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            if customer and booking.customer_id == customer.id:
                is_customer = True
            technician = self.technician_crud.get_by_user_id(current_user.id)
            if technician and booking.technician_id == technician.id:
                is_technician = True
            if not (is_customer or is_technician):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view tracking for this booking.",
                )

        event = self.crud.get_latest_event(booking_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tracking data available for this booking.",
            )

        # Calculate ETA if coordinates are available
        eta_minutes = None
        if booking.customer and booking.customer.latitude and booking.customer.longitude:
            try:
                from math import atan2, cos, radians, sin, sqrt
                # Haversine approximation for ETA (rough)
                lat1 = radians(event.latitude)
                lon1 = radians(event.longitude)
                lat2 = radians(booking.customer.latitude)
                lon2 = radians(booking.customer.longitude)
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance_km = 6371 * c  # Earth radius in km
                # Assume average speed of 30 km/h for urban areas
                eta_minutes = round((distance_km / 30) * 60, 1)
            except (TypeError, ValueError):
                pass

        return TechnicianLocationResponse(
            booking_id=booking_id,
            technician_id=event.technician_id or 0,
            latitude=event.latitude,
            longitude=event.longitude,
            status=event.status,
            last_updated=event.created_at,
            eta_minutes=eta_minutes,
        )

    # ── Get Tracking History ───────────────────────────────────────────

    def get_tracking_history(
        self,
        current_user: User,
        booking_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> TrackingHistoryResponse:
        """Get the full tracking history for a booking."""
        # Verify access (same as get_latest_location)
        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if not current_user.is_superuser:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            is_customer = customer and booking.customer_id == customer.id
            technician = self.technician_crud.get_by_user_id(current_user.id)
            is_technician = technician and booking.technician_id == technician.id
            if not (is_customer or is_technician):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view tracking for this booking.",
                )

        events = self.crud.list_events(booking_id, offset=offset, limit=limit)
        total = self.crud.count_events(booking_id)

        return TrackingHistoryResponse(
            events=[TrackingEventResponse.model_validate(e) for e in events],
            total=total,
        )

    # ── Technician Dashboard Location ──────────────────────────────────

    def get_technician_current_location(
        self,
        current_user: User,
    ) -> Optional[TechnicianLocationResponse]:
        """Get the current location of the authenticated technician."""
        technician_id = self._get_technician_id(current_user)
        event = self.crud.get_latest_technician_event(technician_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No location data available.",
            )

        return TechnicianLocationResponse(
            booking_id=event.booking_id,
            technician_id=technician_id,
            latitude=event.latitude,
            longitude=event.longitude,
            status=event.status,
            last_updated=event.created_at,
        )

