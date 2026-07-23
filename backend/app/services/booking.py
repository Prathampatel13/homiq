from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.booking import BookingCRUD
from app.crud.customer import CustomerCRUD
from app.crud.address import AddressCRUD
from app.crud.services import ServicesCRUD
from app.models.bookings import Booking, BookingStatus
from app.models.auth import User
from app.schemas.bookings import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    BookingUpdate,
)


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = BookingCRUD(db)
        self.service_crud = ServicesCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.address_crud = AddressCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            customer = self.customer_crud.create(current_user.id)
        return customer.id

    def _generate_booking_number(self, booking_date: date) -> str:
        # Count existing bookings for the date and make a daily sequence
        count = self.db.scalar(select(func.count(Booking.id)).where(Booking.booking_date == booking_date)) or 0
        seq = int(count) + 1
        return f"HMQ-{booking_date.strftime('%Y%m%d')}-{seq:06d}"

    def create_booking(self, current_user: User, payload: BookingCreate) -> BookingResponse:
        customer_id = self._get_customer_id(current_user)

        # booking_date validation (defensive)
        if payload.booking_date < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="booking_date cannot be in the past")

        # ensure service exists and is active
        service = self.service_crud.get_service(payload.service_id)
        if not service or getattr(service, "is_active", True) is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

        # ensure address belongs to customer
        address = self.address_crud.get_address(customer_id, payload.address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found for customer")

        data: dict[str, Any] = payload.model_dump()
        data["customer_id"] = customer_id
        data.setdefault("estimated_price", service.base_price)
        data["booking_number"] = self._generate_booking_number(payload.booking_date)

        booking = self.crud.create_booking(data)
        return BookingResponse.model_validate(booking)

    def get_booking(self, current_user: User, booking_id: int) -> BookingResponse:
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        # allow if owner customer, assigned technician, or admin
        is_owner = booking.customer and booking.customer.user_id == current_user.id
        is_technician = booking.technician and booking.technician.user_id == current_user.id
        if not (is_owner or is_technician or current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this booking")

        return BookingResponse.model_validate(booking)

    def list_bookings(self, current_user: User, offset: int = 0, limit: int = 100) -> BookingListResponse:
        # Admins see all, customers see their own, technicians see assigned bookings
        if current_user.is_superuser:
            bookings = self.crud.list_bookings(offset=offset, limit=limit)
            total = self.db.scalar(select(func.count(Booking.id))) or 0
        else:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            if customer:
                stmt = select(Booking).where(Booking.customer_id == customer.id).order_by(Booking.created_at.desc()).offset(offset).limit(limit)
                result = self.db.execute(stmt)
                bookings = result.scalars().all()
                total = self.db.scalar(select(func.count(Booking.id)).where(Booking.customer_id == customer.id)) or 0
            else:
                # If user has no customer record, return empty list
                bookings = []
                total = 0

        return BookingListResponse(items=[BookingResponse.model_validate(b) for b in bookings], total=int(total))

    def update_booking(self, current_user: User, booking_id: int, payload: BookingUpdate) -> BookingResponse:
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        # Only owner or admin can update booking details
        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this booking")

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

        # Customers cannot change technician
        if (not current_user.is_superuser) and "technician_id" in data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers cannot change technician")

        # Validate booking_date
        if "booking_date" in data and data["booking_date"] < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="booking_date cannot be in the past")

        # If address is provided, ensure it belongs to customer
        if "address_id" in data:
            customer_id = self._get_customer_id(current_user)
            addr = self.address_crud.get_address(customer_id, int(data["address_id"]))
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found for customer")

        # If service provided, ensure it exists
        if "service_id" in data:
            svc = self.service_crud.get_service(int(data["service_id"]))
            if not svc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

        updated = self.crud.update_booking(booking_id, data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update booking")
        return BookingResponse.model_validate(updated)

    def delete_booking(self, current_user: User, booking_id: int) -> dict[str, str]:
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        is_owner = booking.customer and booking.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this booking")

        deleted = self.crud.delete_booking(booking_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete booking")
        return {"message": "Booking deleted successfully"}

    def assign_technician(self, current_user: User, booking_id: int, technician_id: int) -> BookingResponse:
        # only admin can assign
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin credentials required to assign technician")

        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        updated = self.crud.assign_technician(booking_id, technician_id)
        if not updated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign technician")
        # set status to assigned
        updated = self.crud.update_status(booking_id, BookingStatus.ASSIGNED)
        return BookingResponse.model_validate(updated)

    def update_status(self, current_user: User, booking_id: int, new_status: BookingStatus) -> BookingResponse:
        booking = self.crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        # Only assigned technician or admin can update status
        is_technician = booking.technician and booking.technician.user_id == current_user.id
        if not (is_technician or current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update status")

        # validate transitions
        allowed = {
            BookingStatus.PENDING: {BookingStatus.ACCEPTED, BookingStatus.CANCELLED, BookingStatus.REJECTED},
            BookingStatus.ACCEPTED: {BookingStatus.ASSIGNED, BookingStatus.CANCELLED},
            BookingStatus.ASSIGNED: {BookingStatus.IN_PROGRESS, BookingStatus.CANCELLED},
            BookingStatus.IN_PROGRESS: {BookingStatus.COMPLETED, BookingStatus.CANCELLED},
            BookingStatus.COMPLETED: set(),
            BookingStatus.CANCELLED: set(),
            BookingStatus.REJECTED: set(),
        }

        if new_status == booking.status:
            return BookingResponse.model_validate(booking)

        allowed_next = allowed.get(booking.status, set())
        if new_status not in allowed_next:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status transition: {booking.status} -> {new_status}")

        updated = self.crud.update_status(booking_id, new_status)
        if not updated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update status")
        return BookingResponse.model_validate(updated)
