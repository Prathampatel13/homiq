from typing import Any, Optional

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.auth import User
from app.models.users import Customer, Technician
from app.models.bookings import Booking, BookingStatus


class TechnicianCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Technician]:
        return self.db.scalar(select(Technician).where(Technician.user_id == user_id))

    def get_by_technician_id(self, technician_id: int) -> Optional[Technician]:
        return self.db.get(Technician, technician_id)

    def create(self, user_id: int) -> Technician:
        technician = Technician(user_id=user_id)
        self.db.add(technician)
        self.db.commit()
        self.db.refresh(technician)
        return technician

    def update(self, technician_id: int, data: dict[str, Any]) -> Optional[Technician]:
        if not data:
            return self.get_by_technician_id(technician_id)

        stmt = (
            update(Technician)
            .where(Technician.id == technician_id)
            .values(**data)
            .returning(Technician)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def delete(self, technician_id: int) -> bool:
        technician = self.get_by_technician_id(technician_id)
        if not technician:
            return False
        self.db.delete(technician)
        self.db.commit()
        return True

    def list_technicians(
        self,
        specialization: Optional[str] = None,
        availability: Optional[bool] = None,
        online: Optional[bool] = None,
    ) -> list[Technician]:
        stmt = select(Technician)
        if specialization:
            stmt = stmt.where(Technician.specialization.ilike(f"%{specialization}%"))
        if availability is not None:
            stmt = stmt.where(Technician.availability == availability)
        if online is not None:
            stmt = stmt.where(Technician.is_online == online)

        result = self.db.execute(
            stmt.order_by(Technician.rating.desc(), Technician.reviews_count.desc())
        )
        return list(result.scalars().all())

    def update_user_name(self, user_id: int, full_name: str) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.full_name = full_name
            self.db.commit()

    # ── Technician Jobs ────────────────────────────────────────────────

    def get_technician_jobs(
        self,
        technician_id: int,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """Return bookings assigned to a technician, optionally filtered by status."""
        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer).joinedload(Customer.user),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(Booking.technician_id == technician_id)
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if status:
            stmt = stmt.where(Booking.status == status)
        return list(self.db.execute(stmt).scalars().all())

    def count_technician_jobs(
        self,
        technician_id: int,
        status: Optional[str] = None,
    ) -> int:
        """Count bookings assigned to a technician, optionally filtered by status."""
        stmt = select(func.count(Booking.id)).where(
            Booking.technician_id == technician_id
        )
        if status:
            stmt = stmt.where(Booking.status == status)
        return self.db.scalar(stmt) or 0

    def get_active_bookings(
        self,
        technician_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """Return active (in-flight/pending execution) bookings assigned to a technician."""
        active_statuses = [
            BookingStatus.ASSIGNED,
            BookingStatus.ACCEPTED,
            BookingStatus.ON_THE_WAY,
            BookingStatus.ARRIVED,
            BookingStatus.WAITING_QR,
            BookingStatus.QR_VERIFIED,
            BookingStatus.IN_PROGRESS,
        ]
        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer).joinedload(Customer.user),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(
                Booking.technician_id == technician_id,
                Booking.status.in_(active_statuses),
            )
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_active_bookings(self, technician_id: int) -> int:
        """Count active bookings assigned to a technician."""
        active_statuses = [
            BookingStatus.ASSIGNED,
            BookingStatus.ACCEPTED,
            BookingStatus.ON_THE_WAY,
            BookingStatus.ARRIVED,
            BookingStatus.WAITING_QR,
            BookingStatus.QR_VERIFIED,
            BookingStatus.IN_PROGRESS,
        ]
        stmt = select(func.count(Booking.id)).where(
            Booking.technician_id == technician_id,
            Booking.status.in_(active_statuses),
        )
        return self.db.scalar(stmt) or 0

    def get_booking_history(
        self,
        technician_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """Return historical (completed/terminal) bookings assigned to a technician."""
        history_statuses = [
            BookingStatus.COMPLETED,
            BookingStatus.WAITING_PAYMENT,
            BookingStatus.PAID,
            BookingStatus.REVIEW_PENDING,
            BookingStatus.CLOSED,
            BookingStatus.CANCELLED,
            BookingStatus.EXPIRED,
            BookingStatus.REJECTED,
        ]
        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.customer).joinedload(Customer.user),
                joinedload(Booking.service),
                joinedload(Booking.address),
            )
            .where(
                Booking.technician_id == technician_id,
                Booking.status.in_(history_statuses),
            )
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_booking_history(self, technician_id: int) -> int:
        """Count historical bookings assigned to a technician."""
        history_statuses = [
            BookingStatus.COMPLETED,
            BookingStatus.WAITING_PAYMENT,
            BookingStatus.PAID,
            BookingStatus.REVIEW_PENDING,
            BookingStatus.CLOSED,
            BookingStatus.CANCELLED,
            BookingStatus.EXPIRED,
            BookingStatus.REJECTED,
        ]
        stmt = select(func.count(Booking.id)).where(
            Booking.technician_id == technician_id,
            Booking.status.in_(history_statuses),
        )
        return self.db.scalar(stmt) or 0

    def has_active_booking(self, technician_id: int, exclude_booking_id: Optional[int] = None) -> bool:
        """Check if technician has another booking currently in progress (ACCEPTED through IN_PROGRESS)."""
        busy_statuses = [
            BookingStatus.ACCEPTED,
            BookingStatus.ON_THE_WAY,
            BookingStatus.ARRIVED,
            BookingStatus.WAITING_QR,
            BookingStatus.QR_VERIFIED,
            BookingStatus.IN_PROGRESS,
        ]
        stmt = select(func.count(Booking.id)).where(
            Booking.technician_id == technician_id,
            Booking.status.in_(busy_statuses),
        )
        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)
        count = self.db.scalar(stmt) or 0
        return count > 0

