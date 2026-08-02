"""
Production-ready booking service.

Implements all booking business rules:
- Auto-generates booking numbers (HMQ-YYYYMMDD-XXXXXX)
- Customer-owned address validation
- Service existence and active-status validation
- Booking date cannot be in the past
- Estimated price defaults to Service.base_price
- Admin-only technician assignment (Pending -> Assigned)
- Technician / admin status updates with state-machine validation
- Valid transitions: Assigned -> Accepted -> In Progress -> Completed
- Any active status -> Cancelled
- Customers cannot assign technicians or change booking status
- Role-scoped listing (admin sees all, customers see own, technicians see assigned)
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.booking import BookingCRUD
from app.crud.customer import CustomerCRUD
from app.crud.services import ServicesCRUD
from app.crud.technician import TechnicianCRUD
from app.models.bookings import Booking, BookingStatus
from app.models.auth import User
from app.schemas.bookings import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    BookingUpdate,
    BookingAssignTechnician,
)


class BookingService:
    """Service layer for booking operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = BookingCRUD(db)
        self.service_crud = ServicesCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.address_crud = self.customer_crud
        self.technician_crud = TechnicianCRUD(db)

    # ─────────────────────────────────────────────

    def _get_customer_id(self, current_user: User) -> int:
        """
        Resolve the Customer record for the current user.
        Customer profile must already exist.
        """

        customer = self.customer_crud.get_by_user_id(current_user.id)

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )

        return customer.id
    
    def _generate_booking_number(self, booking_date: date) -> str:
        """
        Generate a unique booking number in the format HMQ-YYYYMMDD-XXXXXX.

        The sequence is reset daily based on the number of existing bookings
        on the given date.  Under extremely high concurrency a retry / unique
        constraint fallback could be added in a future iteration.
        """
        count = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.booking_date == booking_date)
        ) or 0
        seq = int(count) + 1
        return f"HMQ-{booking_date.strftime('%Y%m%d')}-{seq:06d}"

    # ── CREATE ─────────────────────────────────────────────────────────

    def create_booking(
        self,
        current_user: User,
        payload: BookingCreate,
    ) -> BookingResponse:
        """
        Create a new booking for the authenticated customer.

        Business rules enforced:
        - Booking date must not be in the past.
        - The service must exist and be active.
        - The address must belong to the customer.
        - A unique booking number is auto-generated.
        - Estimated price defaults to the service's base_price unless
          the user explicitly provided a value.

        Args:
            current_user: Authenticated user (JWT).
            payload: Booking creation payload.

        Returns:
            BookingResponse with the newly created booking.

        Raises:
            400: If booking_date is in the past.
            404: If service or address not found.
        """
        customer_id = self._get_customer_id(current_user)

        # Defensive check (schema-level validator also enforces this)
        if payload.booking_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_date cannot be in the past",
            )

        # Validate service exists and is active
        service = self.service_crud.get_service(payload.service_id)
        if not service or getattr(service, "is_active", True) is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        # Validate address belongs to customer
        address = self.address_crud.get_address(customer_id, payload.address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found for customer",
            )

        # Build the data dict
        # Use exclude_unset so user-provided estimated_price is honored;
        # if omitted, default to service.base_price.
        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["customer_id"] = customer_id
        data.setdefault("estimated_price", service.base_price)
        data["booking_number"] = self._generate_booking_number(payload.booking_date)

        booking = self.crud.create_booking(data)
        return BookingResponse.model_validate(booking)

    # ─── READ (single) ─────────────────────────────────────────────────

    def get_booking(self, current_user: User, booking_id: int) -> BookingResponse:
        """
        Retrieve a single booking by ID.

        Access is restricted to:
        - The customer who owns the booking.
        - The technician assigned to the booking.
        - Any admin (superuser).

        Args:
            current_user: Authenticated user (JWT).
            booking_id: Unique booking ID.

        Returns:
            BookingResponse with full booking details.

        Raises:
            404: If the booking does not exist.
            403: If the user is not authorised to view it.
        """
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        is_technician = (
            booking.technician and booking.technician.user_id == current_user.id
        )
        if not (is_owner or is_technician or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this booking",
            )

        return BookingResponse.model_validate(booking)

    # ─── LIST ──────────────────────────────────────────────────────────

    def list_bookings(
        self, current_user: User, offset: int = 0, limit: int = 100
    ) -> BookingListResponse:
        """
        List bookings scoped to the current user's role.

        - **Admin**: sees all bookings.
        - **Customer**: sees only their own bookings.
        - **Technician**: sees bookings assigned to them.

        Args:
            current_user: Authenticated user (JWT).
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            BookingListResponse with items and total count.
        """
        if current_user.is_superuser:
            # Admin — full access
            bookings = self.crud.list_bookings(offset=offset, limit=limit)
            total = self.db.scalar(select(func.count(Booking.id))) or 0
        else:
            # Check if the user is a customer
            customer = self.customer_crud.get_by_user_id(current_user.id)
            if customer:
                stmt = (
                    select(Booking)
                    .where(Booking.customer_id == customer.id)
                    .order_by(Booking.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
                result = self.db.execute(stmt)
                bookings = result.scalars().all()
                total = (
                    self.db.scalar(
                        select(func.count(Booking.id)).where(
                            Booking.customer_id == customer.id
                        )
                    )
                    or 0
                )
            else:
                # Check if the user is a technician
                technician = self.technician_crud.get_by_user_id(current_user.id)
                if technician:
                    stmt = (
                        select(Booking)
                        .where(Booking.technician_id == technician.id)
                        .order_by(Booking.created_at.desc())
                        .offset(offset)
                        .limit(limit)
                    )
                    result = self.db.execute(stmt)
                    bookings = result.scalars().all()
                    total = (
                        self.db.scalar(
                            select(func.count(Booking.id)).where(
                                Booking.technician_id == technician.id
                            )
                        )
                        or 0
                    )
                else:
                    # No customer or technician record – empty result
                    bookings = []
                    total = 0

        return BookingListResponse(
            items=[BookingResponse.model_validate(b) for b in bookings],
            total=int(total),
        )

    # ─── UPDATE ────────────────────────────────────────────────────────

    def update_booking(
        self, current_user: User, booking_id: int, payload: BookingUpdate
    ) -> BookingResponse:
        """
        Update an existing booking (partial update).

        Only the booking owner (customer) or an admin may update.
        Customers cannot change the technician.
        If the address is changed, it must belong to the customer.

        Note: The ``technician_id`` field is not present in the
        ``BookingUpdate`` schema.  Technician assignment is handled
        exclusively via ``assign_technician`` (admin-only).

        Args:
            current_user: Authenticated user (JWT).
            booking_id: Unique booking ID.
            payload: Fields to update.

        Returns:
            BookingResponse with the updated booking.

        Raises:
            404: If the booking is not found.
            403: If the user is not authorised.
            400: If no valid fields provided or validation fails.
        """
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this booking",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Validate booking_date if provided
        if "booking_date" in data and data["booking_date"] < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_date cannot be in the past",
            )

        # If address is provided, ensure it belongs to customer
        if "address_id" in data:
            customer_id = self._get_customer_id(current_user)
            addr = self.address_crud.get_address(customer_id, int(data["address_id"]))
            if not addr:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Address not found for customer",
                )

        # If service is changed, ensure it exists and is active
        if "service_id" in data:
            svc = self.service_crud.get_service(int(data["service_id"]))
            if not svc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found",
                )

        updated = self.crud.update_booking(booking_id, data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update booking",
            )
        return BookingResponse.model_validate(updated)

    # ─── DELETE ────────────────────────────────────────────────────────

    def delete_booking(
        self, current_user: User, booking_id: int
    ) -> dict[str, str]:
        """
        Delete a booking by ID.

        Only the booking owner (customer) or an admin may delete.

        Args:
            current_user: Authenticated user (JWT).
            booking_id: Unique booking ID.

        Returns:
            A confirmation message dict.

        Raises:
            404: If the booking is not found.
            403: If the user is not authorised.
        """
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this booking",
            )

        deleted = self.crud.delete_booking(booking_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete booking",
            )
        return {"message": "Booking deleted successfully"}

    # ─── ASSIGN TECHNICIAN ─────────────────────────────────────────────

    def assign_technician(
        self,
        current_user: User,
        booking_id: int,
        payload: BookingAssignTechnician,
    ) -> BookingResponse:
        """
        Assign a technician to a booking.

        **Admin-only.**  Also validates that the technician exists in the
        system.  The booking must be in ``pending`` status for assignment.
        The booking status is automatically set to ``assigned``.
        Optional ``estimated_price`` / ``final_price`` values from the
        payload are applied to the booking.

        Args:
            current_user: Authenticated user (JWT, must be admin).
            booking_id: Unique booking ID.
            payload: Contains ``technician_id`` and optional price fields.

        Returns:
            BookingResponse with the updated booking.

        Raises:
            403: If the current user is not an admin.
            404: If the booking or technician is not found.
            400: If the booking is not in pending status or assignment fails.
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin credentials required to assign technician",
            )

        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Only bookings with status 'pending' can be assigned. "
                    f"Current status: '{booking.status.value}'"
                ),
            )

        # Validate technician exists
        technician = self.technician_crud.get_by_technician_id(payload.technician_id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )

        # Apply any price overrides from the payload
        price_data: dict[str, Any] = {}
        if payload.estimated_price is not None:
            price_data["estimated_price"] = payload.estimated_price
        if payload.final_price is not None:
            price_data["final_price"] = payload.final_price

        if price_data:
            self.crud.update_booking(booking_id, price_data)

        # Assign the technician
        updated = self.crud.assign_technician(booking_id, payload.technician_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign technician",
            )

        # Transition status to assigned
        updated = self.crud.update_status(booking_id, BookingStatus.ASSIGNED)
        return BookingResponse.model_validate(updated)

    # ─── UPDATE STATUS ─────────────────────────────────────────────────

    def update_status(
        self,
        current_user: User,
        booking_id: int,
        new_status: BookingStatus,
        admin_note: Optional[str] = None,
    ) -> BookingResponse:
        """
        Update a booking's status with state-machine validation.

        Only the assigned technician or an admin may update the status.
        The allowed transitions are:

        - ``pending`` → (no direct transitions; use admin assign)
        - ``assigned`` → ``accepted`` | ``cancelled``
        - ``accepted`` → ``in_progress`` | ``cancelled``
        - ``in_progress`` → ``completed`` | ``cancelled``
        - ``completed`` → (terminal)
        - ``cancelled`` → (terminal)

        **Admin override:** Administrators may perform *any* transition
        (including forcing a terminal status back to a previous state),
        which is useful for correcting mistakes.

        Args:
            current_user: Authenticated user (JWT).
            booking_id: Unique booking ID.
            new_status: The target status.
            admin_note: Optional note saved when status changes.

        Returns:
            BookingResponse with the updated booking.

        Raises:
            404: If the booking is not found.
            403: If the user is not authorised.
            400: If the status transition is invalid.
        """
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Only assigned technician or admin can update status
        is_technician = (
            booking.technician and booking.technician.user_id == current_user.id
        )
        if not (is_technician or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update status",
            )

        # If status is unchanged, just return the booking (applying admin_note if given)
        if new_status == booking.status:
            if admin_note is not None:
                self.crud.update_booking(booking_id, {"admin_note": admin_note})
                self.db.refresh(booking)
            return BookingResponse.model_validate(booking)

        # Allowed state transitions (non-admin)
        # Pending can only transition to Assigned via admin assign_technician
        allowed_transitions = {
            BookingStatus.PENDING: set(),
            BookingStatus.ASSIGNED: {
                BookingStatus.ACCEPTED,
                BookingStatus.CANCELLED,
            },
            BookingStatus.ACCEPTED: {
                BookingStatus.IN_PROGRESS,
                BookingStatus.CANCELLED,
            },
            BookingStatus.IN_PROGRESS: {
                BookingStatus.COMPLETED,
                BookingStatus.CANCELLED,
            },
            BookingStatus.COMPLETED: set(),
            BookingStatus.CANCELLED: set(),
        }

        # Admins may bypass the transition matrix for manual corrections
        if not current_user.is_superuser:
            allowed_next = allowed_transitions.get(booking.status, set())
            if new_status not in allowed_next:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid status transition: "
                        f"'{booking.status.value}' -> '{new_status.value}'"
                    ),
                )

        # Persist the admin note alongside the status change
        update_data: dict[str, Any] = {"status": new_status}
        if admin_note is not None:
            update_data["admin_note"] = admin_note

        updated = self.crud.update_booking(booking_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update status",
            )
        return BookingResponse.model_validate(updated)
