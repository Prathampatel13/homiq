from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.bookings import Booking, BookingStatus, BookingStatusLog


class BookingCRUD:
    def __init__(self, db: Session):
        self.db = db

    # --------------------------------------------------
    # Create
    # --------------------------------------------------

    def create_booking(self, data: Dict[str, Any]) -> Booking:
        booking = Booking(**data)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    # --------------------------------------------------
    # Get
    # --------------------------------------------------

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer),
                joinedload(Booking.technician),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(Booking.id == booking_id)
        )

        return self.db.scalar(stmt)

    def get_by_booking_number(self, booking_number: str) -> Optional[Booking]:
        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer),
                joinedload(Booking.technician),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(Booking.booking_number == booking_number)
        )

        return self.db.scalar(stmt)

    # --------------------------------------------------
    # List
    # --------------------------------------------------

    def list_bookings(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer),
                joinedload(Booking.technician),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return self.db.execute(stmt).scalars().all()

    def list_customer_bookings(
        self,
        customer_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer),
                joinedload(Booking.technician),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return self.db.execute(stmt).scalars().all()

    def list_technician_bookings(
        self,
        technician_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer),
                joinedload(Booking.technician),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(Booking.technician_id == technician_id)
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return self.db.execute(stmt).scalars().all()

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    def count_bookings(self) -> int:
        return self.db.scalar(
            select(func.count(Booking.id))
        ) or 0

    def count_customer_bookings(
        self,
        customer_id: int,
    ) -> int:

        return self.db.scalar(
            select(func.count(Booking.id))
            .where(
                Booking.customer_id == customer_id
            )
        ) or 0

    def count_technician_bookings(
        self,
        technician_id: int,
    ) -> int:

        return self.db.scalar(
            select(func.count(Booking.id))
            .where(
                Booking.technician_id == technician_id
            )
        ) or 0

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update_booking(
        self,
        booking_id: int,
        data: Dict[str, Any],
    ) -> Optional[Booking]:

        booking = self.get_booking(booking_id)

        if not booking:
            return None

        for key, value in data.items():
            setattr(booking, key, value)

        self.db.commit()
        self.db.refresh(booking)

        return booking

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    def delete_booking(
        self,
        booking_id: int,
    ) -> bool:

        booking = self.get_booking(booking_id)

        if not booking:
            return False

        self.db.delete(booking)

        self.db.commit()

        return True

    # --------------------------------------------------
    # Technician
    # --------------------------------------------------

    def assign_technician(
        self,
        booking_id: int,
        technician_id: int,
    ) -> Optional[Booking]:

        booking = self.get_booking(booking_id)

        if not booking:
            return None

        booking.technician_id = technician_id

        self.db.commit()
        self.db.refresh(booking)

        return booking

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def update_status(
        self,
        booking_id: int,
        booking_status: Any,
    ) -> Optional[Booking]:

        booking = self.get_booking(booking_id)

        if not booking:
            return None

        booking.status = booking_status

        self.db.commit()
        self.db.refresh(booking)

        return booking

    # --------------------------------------------------
    # Reassign Technician
    # --------------------------------------------------


    def reassign_technician(
        self,
        booking_id: int,
        technician_id: int,
    ) -> Optional[Booking]:
        """Reassign a booking to a different technician.

        Unlike ``assign_technician`` this does not transition the status;
        the caller is responsible for deciding whether the status should
        move back to ``ASSIGNED`` after a reassignment.
        """

        booking = self.get_booking(booking_id)

        if not booking:
            return None

        booking.technician_id = technician_id

        self.db.commit()
        self.db.refresh(booking)

        return booking

    # --------------------------------------------------
    # Status Logs (audit trail)
    # --------------------------------------------------

    def create_status_log(
        self,
        booking_id: int,
        new_status: BookingStatus,
        old_status: Optional[BookingStatus] = None,
        changed_by_user_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> BookingStatusLog:
        """Record a booking status change in the audit trail."""

        log = BookingStatusLog(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user_id,
            reason=reason,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_status_log(
        self,
        log_id: int,
    ) -> Optional[BookingStatusLog]:
        """Retrieve a single status log entry."""

        return self.db.get(BookingStatusLog, log_id)

    def list_status_logs(
        self,
        booking_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[BookingStatusLog]:
        """List the status-change history for a booking, newest first."""

        stmt = (
            select(BookingStatusLog)
            .where(BookingStatusLog.booking_id == booking_id)
            .order_by(BookingStatusLog.created_at.desc(), BookingStatusLog.id.desc())
            .offset(offset)
            .limit(limit)
        )

        return self.db.execute(stmt).scalars().all()

    def count_status_logs(
        self,
        booking_id: int,
    ) -> int:
        """Count the status-change history entries for a booking."""

        return (
            self.db.scalar(
                select(func.count(BookingStatusLog.id)).where(
                    BookingStatusLog.booking_id == booking_id
                )
            )
            or 0
        )
