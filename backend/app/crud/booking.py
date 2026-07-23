from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bookings import Booking


class BookingCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, data: Dict[str, Any]) -> Booking:
        booking = Booking(**data)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self.db.get(Booking, booking_id)

    def list_bookings(self, offset: int = 0, limit: int = 100) -> List[Booking]:
        stmt = select(Booking).order_by(Booking.created_at.desc()).offset(offset).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update_booking(self, booking_id: int, data: Dict[str, Any]) -> Optional[Booking]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        for key, value in data.items():
            setattr(booking, key, value)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def delete_booking(self, booking_id: int) -> bool:
        booking = self.get_booking(booking_id)
        if not booking:
            return False
        self.db.delete(booking)
        self.db.commit()
        return True

    def assign_technician(self, booking_id: int, technician_id: int) -> Optional[Booking]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        booking.technician_id = technician_id
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_status(self, booking_id: int, status: Any) -> Optional[Booking]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        booking.status = status
        self.db.commit()
        self.db.refresh(booking)
        return booking
