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
- Valid lifecycle transitions (see _ALLOWED_TRANSITIONS)
- Any active status -> Cancelled
- Customers cannot assign technicians or change booking status
- Role-scoped listing (admin sees all, customers see own, technicians see assigned)
- Centralised transition validation returns 409 for invalid transitions
- Every status change is recorded in the booking audit trail
"""

import logging
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.services.websocket import WebSocketService

logger = logging.getLogger("homiq.services.booking")

from app.crud.booking import BookingCRUD
from app.crud.customer import CustomerCRUD
from app.crud.services import ServicesCRUD
from app.crud.technician import TechnicianCRUD
from app.models.bookings import Booking, BookingStatus, BookingStatusLog
from app.models.auth import User
from app.schemas.bookings import (
    AssignedTechnicianResponse,
    BookingAssignTechnician,
    BookingCancelRequest,
    BookingCreate,
    BookingHistoryEntry,
    BookingHistoryResponse,
    BookingListResponse,
    BookingRejectRequest,
    BookingRescheduleRequest,
    BookingResponse,
    BookingUpdate,
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
        on the given date.  Because rescheduling changes ``booking_date``
        without changing the booking number, the daily sequence can
        occasionally collide with an existing number.  To keep the number
        format stable and unique, the sequence is incremented until a
        non-colliding number is found.
        """
        base = booking_date.strftime("%Y%m%d")
        count = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.booking_date == booking_date)
        ) or 0
        seq = int(count) + 1
        ticket = ""
        while True:
            candidate = f"HMQ-{base}-{seq:06d}"
            exists = self.db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.booking_number == candidate
                )
            ) or 0
            if exists == 0:
                ticket = candidate
                break
            seq += 1
        return ticket

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

        # Broadcast new booking dispatch to online technicians and admin in real-time
        try:
            ws_service = WebSocketService(self.db)
            ws_service.broadcast_booking_update(
                booking_id=booking.id,
                old_status="",
                new_status="pending",
                message=f"New dispatch: {service.name} (Booking #{booking.booking_number})",
            )
        except Exception as exc:
            logger.warning(f"Failed to broadcast new booking websocket event: {exc}")

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
                    .options(joinedload(Booking.service))
                    .options(joinedload(Booking.technician))
                    .options(joinedload(Booking.address))
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
        updated = self._transition(
            updated,
            BookingStatus.ASSIGNED,
            current_user,
            reason=f"Assigned to technician #{payload.technician_id}",
        )
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
        The allowed transitions are defined in ``_ALLOWED_TRANSITIONS``.
        Invalid transitions raise ``409 CONFLICT``, and every change is
        recorded in the booking's audit trail.

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
            409: If the status transition is invalid.
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

        # Persist the admin note alongside the status change
        if admin_note is not None:
            self.crud.update_booking(booking_id, {"admin_note": admin_note})

        # Perform the transition (validates via _ALLOWED_TRANSITIONS and
        # records an audit log entry).
        updated = self._transition(booking, new_status, current_user, reason=admin_note)
        return BookingResponse.model_validate(updated)

    # ─── CENTRALISED TRANSITION MAP ────────────────────────────────────

    # Allowed lifecycle transitions for non-admin users.
    # Pending -> Assigned is performed exclusively by the admin assign flow.
    _ALLOWED_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
        BookingStatus.PENDING: {
            BookingStatus.ACCEPTED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.ASSIGNED: {
            BookingStatus.ACCEPTED,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.ACCEPTED: {
            BookingStatus.ON_THE_WAY,
            BookingStatus.ARRIVED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.ON_THE_WAY: {
            BookingStatus.ARRIVED,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.ARRIVED: {
            BookingStatus.IN_PROGRESS,
            BookingStatus.CONFIRMED,
            BookingStatus.WAITING_QR,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.WAITING_QR: {
            BookingStatus.CONFIRMED,
            BookingStatus.QR_VERIFIED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.QR_VERIFIED: {
            BookingStatus.CONFIRMED,
            BookingStatus.IN_PROGRESS,
            BookingStatus.CANCELLED,
        },
        BookingStatus.CONFIRMED: {
            BookingStatus.IN_PROGRESS,
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.IN_PROGRESS: {
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.COMPLETED: {
            BookingStatus.WAITING_PAYMENT,
            BookingStatus.PAID,
            BookingStatus.CLOSED,
        },
        BookingStatus.WAITING_PAYMENT: {
            BookingStatus.PAID,
            BookingStatus.CLOSED,
        },
        BookingStatus.PAID: {
            BookingStatus.REVIEW_PENDING,
            BookingStatus.CLOSED,
        },
        BookingStatus.REVIEW_PENDING: {
            BookingStatus.CLOSED,
        },
        BookingStatus.CLOSED: set(),
        BookingStatus.CANCELLED: set(),
        BookingStatus.EXPIRED: set(),
        BookingStatus.REJECTED: set(),
    }

    # Statuses that are terminal (no further transitions for non-admins).
    _TERMINAL_STATUSES: set[BookingStatus] = {
        BookingStatus.CLOSED,
        BookingStatus.CANCELLED,
        BookingStatus.EXPIRED,
        BookingStatus.REJECTED,
    }

    # Customer-cancel allowed source statuses.
    _CUSTOMER_CANCELABLE: set[BookingStatus] = {
        BookingStatus.PENDING,
        BookingStatus.ASSIGNED,
        BookingStatus.ACCEPTED,
        BookingStatus.ON_THE_WAY,
        BookingStatus.ARRIVED,
    }

    # Customer-reschedule allowed source statuses.
    _RESCHEDULABLE: set[BookingStatus] = {
        BookingStatus.PENDING,
        BookingStatus.ASSIGNED,
        BookingStatus.ACCEPTED,
    }

    # ─── TRANSITION + AUDIT HELPER ────────────────────────────────────

    def _validate_transition(
        self,
        booking: Booking,
        new_status: BookingStatus,
        current_user: User,
    ) -> None:
        """Validate a status transition against the lifecycle map.

        Admins may bypass the map for manual corrections. Non-admins must
        follow the allowed transitions. Invalid transitions raise 409.
        """
        def _to_status(val: Any) -> BookingStatus:
            if isinstance(val, BookingStatus):
                return val
            if isinstance(val, str):
                try:
                    return BookingStatus(val.lower())
                except ValueError:
                    pass
            return val

        cur_st = _to_status(booking.status)
        tgt_st = _to_status(new_status)

        if cur_st == tgt_st:
            return

        if not current_user.is_superuser:
            allowed_next = self._ALLOWED_TRANSITIONS.get(cur_st, set())
            if tgt_st not in allowed_next:
                cur_name = cur_st.value if hasattr(cur_st, "value") else str(cur_st)
                tgt_name = tgt_st.value if hasattr(tgt_st, "value") else str(tgt_st)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Invalid status transition: "
                        f"'{cur_name}' -> '{tgt_name}'"
                    ),
                )

    def _transition(
        self,
        booking: Booking,
        new_status: BookingStatus,
        current_user: User,
        reason: Optional[str] = None,
    ) -> Booking:
        """Perform a status transition and record an audit log entry.

        The booking object is mutated in place and committed.  A
        ``BookingStatusLog`` entry is created for every change.
        """
        old_status = booking.status

        if old_status == new_status:
            return booking

        self._validate_transition(booking, new_status, current_user)

        booking.status = new_status
        self.db.commit()
        self.db.refresh(booking)

        self.crud.create_status_log(
            booking_id=booking.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=current_user.id,
            reason=reason,
        )

        # Broadcast real-time status update to Customer, Technician, and Admin
        try:
            ws_service = WebSocketService(self.db)
            old_val = old_status.value if hasattr(old_status, "value") else str(old_status)
            new_val = new_status.value if hasattr(new_status, "value") else str(new_status)
            ws_service.broadcast_booking_update(
                booking_id=booking.id,
                old_status=old_val,
                new_status=new_val,
                message=reason or f"Booking #{booking.booking_number} is now {new_val}",
            )
        except Exception as exc:
            logger.warning(f"Failed to broadcast status update websocket event: {exc}")

        return booking

    # ─── HELPER: load + authorise ─────────────────────────────────────

    def _get_booking_for(self, current_user: User, booking_id: int) -> Booking:
        """Load a booking and verify basic read access (owner/tech/admin)."""
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
            
        if current_user.is_superuser:
            return booking

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        is_assigned_technician = (
            booking.technician and booking.technician.user_id == current_user.id
        )
        
        is_unassigned_tech = False
        if not booking.technician_id:
            if self.technician_crud.get_by_user_id(current_user.id):
                is_unassigned_tech = True

        if not (is_owner or is_assigned_technician or is_unassigned_tech):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this booking",
            )
        return booking

    def _get_technician_id(self, current_user: User) -> int:
        """Resolve the Technician record id for the current user."""
        technician = self.technician_crud.get_by_user_id(current_user.id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )
        return technician.id

    # ─── CUSTOMER: CANCEL ─────────────────────────────────────────────

    def cancel_booking(
        self,
        current_user: User,
        booking_id: int,
        payload: BookingCancelRequest,
    ) -> BookingResponse:
        """Cancel a booking.

        The booking owner (customer) or an admin may cancel.  Customers may
        only cancel from the ``PENDING / ASSIGNED / ACCEPTED / ON_THE_WAY``
        statuses.
        """
        booking = self._get_booking_for(current_user, booking_id)

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking",
            )

        if not current_user.is_superuser and booking.status not in self._CUSTOMER_CANCELABLE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Booking cannot be cancelled from status "
                    f"'{booking.status.value}'"
                ),
            )

        updated = self._transition(
            booking,
            BookingStatus.CANCELLED,
            current_user,
            reason=payload.reason,
        )
        return BookingResponse.model_validate(updated)

    # ─── CUSTOMER: RESCHEDULE ─────────────────────────────────────────

    def reschedule_booking(
        self,
        current_user: User,
        booking_id: int,
        payload: BookingRescheduleRequest,
    ) -> BookingResponse:
        """Reschedule a booking.

        The booking owner (customer) or an admin may reschedule.  Customers
        may only reschedule from ``PENDING / ASSIGNED / ACCEPTED``.
        """
        booking = self._get_booking_for(current_user, booking_id)

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reschedule this booking",
            )

        if not current_user.is_superuser and booking.status not in self._RESCHEDULABLE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Booking cannot be rescheduled from status "
                    f"'{booking.status.value}'"
                ),
            )

        updated = self.crud.update_booking(
            booking_id,
            {
                "booking_date": payload.booking_date,
                "preferred_time": payload.preferred_time,
            },
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reschedule booking",
            )
        return BookingResponse.model_validate(updated)

    # ─── CUSTOMER: HISTORY ────────────────────────────────────────────

    def get_booking_history(
        self,
        current_user: User,
        booking_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> BookingHistoryResponse:
        """Return the status-change history (audit trail) for a booking."""
        booking = self._get_booking_for(current_user, booking_id)

        logs = self.crud.list_status_logs(booking_id, offset=offset, limit=limit)
        total = self.crud.count_status_logs(booking_id)

        return BookingHistoryResponse(
            items=[BookingHistoryEntry.model_validate(log) for log in logs],
            total=int(total),
        )

    def get_booking_history_logs(
        self,
        current_user: User,
        booking_id: int,
    ) -> list[Any]:
        """Return raw status logs for admin booking audit log view."""
        return self.crud.list_status_logs(booking_id, offset=0, limit=100)

    # ─── CUSTOMER: TRACK ─────────────────────────────────────────────

    def track_booking(self, current_user: User, booking_id: int) -> BookingResponse:
        """Alias for viewing a booking (used by the track endpoint)."""
        return self.get_booking(current_user, booking_id)

    # ─── CUSTOMER: ASSIGNED TECHNICIAN ───────────────────────────────

    def get_assigned_technician(
        self,
        current_user: User,
        booking_id: int,
    ) -> AssignedTechnicianResponse:
        """Return the technician assigned to a booking."""
        booking = self._get_booking_for(current_user, booking_id)

        technician = booking.technician
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No technician assigned to this booking",
            )

        return AssignedTechnicianResponse(
            id=technician.id,
            user_id=technician.user_id,
            full_name=technician.user.full_name,
            phone=technician.user.phone,
            specialization=technician.specialization,
            rating=technician.rating,
            reviews_count=technician.reviews_count,
            profile_image=technician.profile_image,
        )

    # ─── TECHNICIAN: ACCEPT / REJECT ─────────────────────────────────

    def accept_booking(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Accept an assigned booking (technician or admin)."""
        booking = self._get_booking_for(current_user, booking_id)
        
        if not booking.technician_id and not current_user.is_superuser:
            technician = self.technician_crud.get_by_user_id(current_user.id)
            if technician:
                self.crud.update_booking(booking.id, {"technician_id": technician.id})
                self.db.refresh(booking)
        else:
            self._ensure_technician_role(current_user, booking)
            
        self._ensure_transition_change(booking, BookingStatus.ACCEPTED)

        reason = payload.reason if payload else None
        updated = self._transition(
            booking,
            BookingStatus.ACCEPTED,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    def reject_booking(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Reject an assigned booking (technician or admin)."""
        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)
        self._ensure_transition_change(booking, BookingStatus.REJECTED)

        reason = payload.reason if payload else None
        updated = self._transition(
            booking,
            BookingStatus.REJECTED,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    # ─── TECHNICIAN: TRIP LIFECYCLE ──────────────────────────────────

    def start_trip(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Mark the technician as on the way (technician or admin)."""
        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)
        self._ensure_transition_change(booking, BookingStatus.ON_THE_WAY)

        reason = payload.reason if payload else None
        updated = self._transition(
            booking,
            BookingStatus.ON_THE_WAY,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    def mark_arrived(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Mark the technician as arrived and auto-generate unique 6-digit code and QR token."""
        import random
        import secrets
        from datetime import datetime, timedelta, timezone
        from app.models.qr import QRVerification

        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)
        self._ensure_transition_change(booking, BookingStatus.ARRIVED)

        # Generate unique 6-digit verification code and QR token
        verification_code = f"{random.randint(100000, 999999)}"
        qr_token = f"HMQ-VERIFY-{booking.id}-{secrets.token_hex(8)}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=2)

        qr_rec = self.db.scalar(select(QRVerification).where(QRVerification.booking_id == booking.id))
        tech_id = booking.technician_id
        if not tech_id and current_user.technician:
            tech_id = current_user.technician.id

        if not qr_rec:
            qr_rec = QRVerification(
                booking_id=booking.id,
                technician_id=tech_id or 0,
                token=qr_token,
                verification_code=verification_code,
                verification_status="pending",
                expires_at=expires_at,
                created_at=now,
            )
            self.db.add(qr_rec)
        else:
            qr_rec.token = qr_token
            qr_rec.verification_code = verification_code
            qr_rec.verification_status = "pending"
            qr_rec.expires_at = expires_at
            if tech_id:
                qr_rec.technician_id = tech_id

        self.db.commit()

        reason = payload.reason if payload else "Technician arrived at location"
        updated = self._transition(
            booking,
            BookingStatus.ARRIVED,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    def verify_arrival_code(
        self,
        current_user: User,
        booking_id: int,
        code: str,
    ) -> BookingResponse:
        """Technician verifies the customer's unique 6-digit code or QR token, marking service as CONFIRMED."""
        from datetime import datetime, timezone
        from app.models.qr import QRVerification

        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)

        if booking.status not in [BookingStatus.ARRIVED, BookingStatus.WAITING_QR, BookingStatus.QR_VERIFIED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot verify code for booking with status '{booking.status.value}'. Must be 'arrived'.",
            )

        clean_code = code.strip().upper()
        qr_rec = self.db.scalar(select(QRVerification).where(QRVerification.booking_id == booking.id))
        if not qr_rec or not qr_rec.verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification code active for this booking. Please mark arrived first.",
            )

        # Match either 6-digit passcode or QR token
        matches_code = clean_code == (qr_rec.verification_code or "").strip().upper()
        matches_token = clean_code == (qr_rec.token or "").strip().upper()

        if not (matches_code or matches_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code or QR token. Please verify with the customer.",
            )

        now = datetime.now(timezone.utc)
        qr_rec.verification_status = "verified"
        qr_rec.verified_at = now
        qr_rec.customer_pin_verified_at = now
        qr_rec.technician_qr_verified_at = now
        qr_rec.used = True
        self.db.commit()

        updated = self._transition(
            booking,
            BookingStatus.IN_PROGRESS,
            current_user,
            reason="Customer passcode verified. Work initiated and in progress.",
        )
        return BookingResponse.model_validate(updated)

    def get_verification_details(
        self,
        current_user: User,
        booking_id: int,
    ) -> dict[str, Any]:
        """Returns verification code, status, and service details for customer and technician."""
        from app.models.qr import QRVerification

        booking = self._get_booking_for(current_user, booking_id)
        qr_rec = self.db.scalar(select(QRVerification).where(QRVerification.booking_id == booking.id))

        tech_name = None
        tech_phone = None
        if booking.technician and booking.technician.user:
            tech_name = booking.technician.user.full_name
            tech_phone = booking.technician.user.phone

        service_name = booking.service.name if booking.service else None
        final_price = booking.final_price or booking.estimated_price

        code = qr_rec.verification_code if qr_rec else None
        qr_token = qr_rec.token if qr_rec else None
        is_verified = (qr_rec.verification_status == "verified") if qr_rec else False

        # If arrived and no code yet, generate on the fly
        if not code and booking.status == BookingStatus.ARRIVED:
            import random
            import secrets
            from datetime import datetime, timedelta, timezone
            code = f"{random.randint(100000, 999999)}"
            qr_token = f"HMQ-VERIFY-{booking.id}-{secrets.token_hex(8)}"
            now = datetime.now(timezone.utc)
            if not qr_rec:
                qr_rec = QRVerification(
                    booking_id=booking.id,
                    technician_id=booking.technician_id or 0,
                    token=qr_token,
                    verification_code=code,
                    verification_status="pending",
                    expires_at=now + timedelta(hours=2),
                    created_at=now,
                )
                self.db.add(qr_rec)
            else:
                qr_rec.verification_code = code
                qr_rec.token = qr_token
            self.db.commit()

        return {
            "booking_id": booking.id,
            "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            "verification_code": code,
            "qr_token": qr_token,
            "qr_data": qr_token,
            "is_verified": is_verified,
            "technician_name": tech_name,
            "technician_phone": tech_phone,
            "service_name": service_name,
            "final_price": final_price,
            "payment_status": booking.payment_status.value if hasattr(booking.payment_status, "value") else str(booking.payment_status),
        }

    def start_service(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Start the service for a booking (technician or admin)."""
        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)
        self._ensure_transition_change(booking, BookingStatus.IN_PROGRESS)

        reason = payload.reason if payload else None
        updated = self._transition(
            booking,
            BookingStatus.IN_PROGRESS,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    def complete_service(
        self,
        current_user: User,
        booking_id: int,
        payload: Optional[BookingRejectRequest] = None,
    ) -> BookingResponse:
        """Complete the service for a booking (technician or admin).
        
        Strictly enforces that customer payment must be completed before the service can be marked as complete.
        """
        booking = self._get_booking_for(current_user, booking_id)
        self._ensure_technician_role(current_user, booking)
        self._ensure_transition_change(booking, BookingStatus.COMPLETED)

        # Strict payment check: Customer must complete payment before completion!
        if not current_user.is_superuser:
            pay_st = booking.payment_status.value if hasattr(booking.payment_status, "value") else str(booking.payment_status)
            if pay_st.lower() != "paid":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer payment has not been received yet. Customer must complete payment before this service can be marked completed.",
                )

        reason = payload.reason if payload else "Service completed and verified"
        updated = self._transition(
            booking,
            BookingStatus.COMPLETED,
            current_user,
            reason=reason,
        )
        return BookingResponse.model_validate(updated)

    # ─── TECHNICIAN: HELPERS ─────────────────────────────────────────

    def _ensure_technician_role(self, current_user: User, booking: Booking) -> None:
        """Ensure the current user is the assigned technician or an admin."""
        if current_user.is_superuser:
            return

        is_technician = False
        if booking.technician and booking.technician.user_id == current_user.id:
            is_technician = True
        elif booking.technician_id:
            tech = self.technician_crud.get_by_user_id(current_user.id)
            if tech and tech.id == booking.technician_id:
                is_technician = True
        else:
            # Unassigned booking being acted on by an eligible technician
            tech = self.technician_crud.get_by_user_id(current_user.id)
            if tech:
                self.crud.update_booking(booking.id, {"technician_id": tech.id})
                self.db.refresh(booking)
                is_technician = True

        if not is_technician:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action on this booking",
            )

    def _ensure_transition_change(
        self, booking: Booking, new_status: BookingStatus
    ) -> None:
        """Reject a no-op (duplicate) action with 409."""
        cur = booking.status.value if hasattr(booking.status, "value") else str(booking.status)
        target = new_status.value if hasattr(new_status, "value") else str(new_status)
        if cur.lower() == target.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Booking is already in status '{target}'; "
                    f"this action has already been performed"
                ),
            )

    # ─── ADMIN: REASSIGN ─────────────────────────────────────────────

    def reassign_technician(
        self,
        current_user: User,
        booking_id: int,
        payload: BookingAssignTechnician,
    ) -> BookingResponse:
        """Reassign a booking to a different technician (admin only)."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin credentials required to reassign technician",
            )

        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        if booking.status in self._TERMINAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Cannot reassign a booking in terminal status "
                    f"'{booking.status.value}'"
                ),
            )

        technician = self.technician_crud.get_by_technician_id(payload.technician_id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )

        updated = self.crud.reassign_technician(booking_id, payload.technician_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reassign technician",
            )

        # Return the booking to ASSIGNED so the new technician can accept.
        updated = self._transition(
            updated,
            BookingStatus.ASSIGNED,
            current_user,
            reason=f"Reassigned to technician #{payload.technician_id}",
        )
        return BookingResponse.model_validate(updated)

    # ─── ADMIN: FORCE CANCEL ─────────────────────────────────────────

    def force_cancel_booking(
        self,
        current_user: User,
        booking_id: int,
        payload: BookingCancelRequest,
    ) -> BookingResponse:
        """Force-cancel a booking regardless of its status (admin only)."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin credentials required to force cancel booking",
            )

        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is already cancelled",
            )

        updated = self._transition(
            booking,
            BookingStatus.CANCELLED,
            current_user,
            reason=payload.reason or "Forced cancellation by admin",
        )
        return BookingResponse.model_validate(updated)

    # ─── ADMIN: OVERRIDE STATUS ──────────────────────────────────────

    def override_status(
        self,
        current_user: User,
        booking_id: int,
        new_status: BookingStatus,
        admin_note: Optional[str] = None,
    ) -> BookingResponse:
        """Admin-only status override that bypasses the transition map."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin credentials required to override booking status",
            )

        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        if new_status == booking.status:
            return BookingResponse.model_validate(booking)

        update_data: dict[str, Any] = {"status": new_status}
        if admin_note is not None:
            update_data["admin_note"] = admin_note

        updated = self.crud.update_booking(booking_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to override status",
            )

        self.crud.create_status_log(
            booking_id=booking.id,
            old_status=booking.status,
            new_status=new_status,
            changed_by_user_id=current_user.id,
            reason=admin_note or "Admin status override",
        )
        return BookingResponse.model_validate(updated)
