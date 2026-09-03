import os
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, settings
from app.crud.technician import TechnicianCRUD
from app.models.auth import User
from app.models.bookings import Booking, BookingStatus, PaymentStatus as BookingPayStatus
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.schemas.technician import (
    GovernmentIdImageResponse,
    ProfileImageResponse,
    TechnicianAvailabilityResponse,
    TechnicianAvailabilityUpdate,
    TechnicianCreate,
    TechnicianEarningsResponse,
    TechnicianJobAddress,
    TechnicianJobCustomer,
    TechnicianJobListResponse,
    TechnicianJobResponse,
    TechnicianJobService,
    TechnicianResponse,
    TechnicianUpdate,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


class TechnicianService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = TechnicianCRUD(db)

    def _get_technician_or_404(self, user_id: int):
        technician = self.crud.get_by_user_id(user_id)
        if not technician:
            technician = self.crud.create(user_id)
        return technician

    def get_profile(self, current_user: User) -> TechnicianResponse:
        technician = self._get_technician_or_404(current_user.id)
        return self._build_response(current_user, technician)

    def update_profile(
        self, current_user: User, payload: TechnicianUpdate
    ) -> TechnicianResponse:
        technician = self._get_technician_or_404(current_user.id)
        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        full_name = update_data.pop("full_name", None)

        if update_data:
            self.crud.update(technician.id, update_data)
            self.db.refresh(technician)

        if full_name:
            self.crud.update_user_name(current_user.id, full_name)
            self.db.refresh(technician)

        return self._build_response(current_user, technician)

    async def upload_profile_image(
        self, current_user: User, file: UploadFile
    ) -> ProfileImageResponse:
        technician = self._get_technician_or_404(current_user.id)
        relative_path = await self._store_image(file, current_user.id, "technician_profile")
        self.crud.update(technician.id, {"profile_image": relative_path})
        return ProfileImageResponse(profile_image=relative_path)

    async def upload_government_id(
        self, current_user: User, file: UploadFile
    ) -> GovernmentIdImageResponse:
        technician = self._get_technician_or_404(current_user.id)
        relative_path = await self._store_image(file, current_user.id, "technician_gov_id")
        self.crud.update(technician.id, {"government_id_image": relative_path})
        return GovernmentIdImageResponse(government_id_image=relative_path)

    def list_technicians(
        self,
        specialization: str | None = None,
        availability: bool | None = None,
        online: bool | None = None,
    ) -> list[TechnicianResponse]:
        technicians = self.crud.list_technicians(
            specialization=specialization,
            availability=availability,
            online=online,
        )
        return [self._build_response(t.user, t) for t in technicians]

    # ── Availability / Online status ──────────────────────────────────

    def update_availability(
        self, current_user: User, payload: TechnicianAvailabilityUpdate
    ) -> TechnicianAvailabilityResponse:
        """Update the technician's availability and/or online status."""
        technician = self._get_technician_or_404(current_user.id)
        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            self.crud.update(technician.id, update_data)
            self.db.refresh(technician)
        return TechnicianAvailabilityResponse(
            availability=technician.availability,
            is_online=technician.is_online,
        )

    def set_online(self, current_user: User) -> TechnicianAvailabilityResponse:
        """Set technician online status to True and availability to True."""
        technician = self._get_technician_or_404(current_user.id)
        self.crud.update(technician.id, {"is_online": True, "availability": True})
        self.db.refresh(technician)
        return TechnicianAvailabilityResponse(
            availability=technician.availability,
            is_online=technician.is_online,
        )

    def set_offline(self, current_user: User) -> TechnicianAvailabilityResponse:
        """Set technician online status to False and availability to False."""
        technician = self._get_technician_or_404(current_user.id)
        self.crud.update(technician.id, {"is_online": False, "availability": False})
        self.db.refresh(technician)
        return TechnicianAvailabilityResponse(
            availability=technician.availability,
            is_online=technician.is_online,
        )

    # ── Jobs & History ────────────────────────────────────────────────

    def get_my_jobs(
        self,
        current_user: User,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> TechnicianJobListResponse:
        """Return jobs (bookings) assigned to the authenticated technician."""
        technician = self._get_technician_or_404(current_user.id)
        bookings = self.crud.get_technician_jobs(
            technician_id=technician.id,
            status=status,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_technician_jobs(
            technician_id=technician.id,
            status=status,
        )
        return TechnicianJobListResponse(
            items=[self._build_job_response(b) for b in bookings],
            total=int(total),
        )

    def get_active_bookings(
        self,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ) -> TechnicianJobListResponse:
        """Return active jobs (bookings) assigned to the authenticated technician."""
        technician = self._get_technician_or_404(current_user.id)
        bookings = self.crud.get_active_bookings(
            technician_id=technician.id,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_active_bookings(technician_id=technician.id)
        return TechnicianJobListResponse(
            items=[self._build_job_response(b) for b in bookings],
            total=int(total),
        )

    def get_booking_history(
        self,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ) -> TechnicianJobListResponse:
        """Return historical completed/terminal jobs assigned to the authenticated technician."""
        technician = self._get_technician_or_404(current_user.id)
        bookings = self.crud.get_booking_history(
            technician_id=technician.id,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_booking_history(technician_id=technician.id)
        return TechnicianJobListResponse(
            items=[self._build_job_response(b) for b in bookings],
            total=int(total),
        )

    def get_customer_history(
        self,
        current_user: User,
        customer_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> TechnicianJobListResponse:
        """Return past/completed booking history of a specific customer."""
        technician = self._get_technician_or_404(current_user.id)
        
        # Verify if technician has ever served this customer (or is an admin)
        has_interaction = self.db.scalar(
            select(Booking).where(
                Booking.technician_id == technician.id,
                Booking.customer_id == customer_id
            ).limit(1)
        )
        if not has_interaction and current_user.role.name.lower() != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view this customer's history.")
            
        stmt = select(Booking).where(Booking.customer_id == customer_id).order_by(Booking.created_at.desc()).offset(offset).limit(limit)
        bookings = self.db.scalars(stmt).all()
        
        count_stmt = select(func.count(Booking.id)).where(Booking.customer_id == customer_id)
        total = self.db.scalar(count_stmt) or 0
        
        return TechnicianJobListResponse(
            items=[self._build_job_response(b) for b in bookings],
            total=int(total)
        )

    # ── Technician Workflow Actions ───────────────────────────────────

    def accept_booking(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Accept an assigned booking with busy guard validation."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        technician = self._get_technician_or_404(current_user.id)
        if self.crud.has_active_booking(technician.id, exclude_booking_id=booking_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Technician already has an active booking in progress",
            )

        booking_service = BookingService(self.db)
        booking_service.accept_booking(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    def reject_booking(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Reject an assigned booking."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        self._get_technician_or_404(current_user.id)
        booking_service = BookingService(self.db)
        booking_service.reject_booking(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    def start_trip(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Start navigation to the job site (mark on_the_way)."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        self._get_technician_or_404(current_user.id)
        booking_service = BookingService(self.db)
        booking_service.start_trip(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    def mark_arrived(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Mark technician arrived at the customer location."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        self._get_technician_or_404(current_user.id)
        booking_service = BookingService(self.db)
        booking_service.mark_arrived(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    def start_service(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Start work on the service (mark in_progress)."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        self._get_technician_or_404(current_user.id)
        booking_service = BookingService(self.db)
        booking_service.start_service(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    def complete_service(
        self, current_user: User, booking_id: int, reason: str | None = None
    ) -> TechnicianJobResponse:
        """Complete work on the service (mark completed)."""
        from app.schemas.bookings import BookingRejectRequest
        from app.services.booking import BookingService

        self._get_technician_or_404(current_user.id)
        booking_service = BookingService(self.db)
        booking_service.complete_service(
            current_user, booking_id, BookingRejectRequest(reason=reason)
        )
        booking = booking_service.crud.get_booking(booking_id)
        return self._build_job_response(booking)

    # ── Earnings ──────────────────────────────────────────────────────

    def get_my_earnings(self, current_user: User) -> TechnicianEarningsResponse:
        """Return the technician's earnings summary."""
        technician = self._get_technician_or_404(current_user.id)
        technician_id = technician.id

        total_earnings = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0))
                .join(Booking, Payment.booking_id == Booking.id)
                .where(
                    Booking.technician_id == technician_id,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0.0
        )

        pending_earnings = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Booking.final_price), 0))
                .where(
                    Booking.technician_id == technician_id,
                    Booking.status.in_([
                        BookingStatus.COMPLETED,
                        BookingStatus.WAITING_PAYMENT,
                    ]),
                    Booking.payment_status == BookingPayStatus.PENDING,
                )
            ) or 0.0
        )

        completed_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([
                    BookingStatus.COMPLETED,
                    BookingStatus.WAITING_PAYMENT,
                    BookingStatus.PAID,
                    BookingStatus.REVIEW_PENDING,
                    BookingStatus.CLOSED,
                ]),
            )
        ) or 0

        paid_jobs = self.db.scalar(
            select(func.count(Booking.id))
            .join(Payment, Payment.booking_id == Booking.id)
            .where(
                Booking.technician_id == technician_id,
                Payment.status == PayStatus.PAID,
            )
        ) or 0

        pending_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                ]),
            )
        ) or 0

        return TechnicianEarningsResponse(
            total_earnings=round(total_earnings, 2),
            pending_earnings=round(pending_earnings, 2),
            completed_jobs=int(completed_jobs),
            paid_jobs=int(paid_jobs),
            pending_jobs=int(pending_jobs),
        )

    # ── Response builders ─────────────────────────────────────────────

    def _build_job_response(self, booking: Any) -> TechnicianJobResponse:
        customer = booking.customer
        service = booking.service
        address = booking.address

        customer_data = None
        if customer and customer.user:
            customer_data = TechnicianJobCustomer(
                id=customer.id,
                full_name=customer.user.full_name,
                phone=customer.user.phone,
            )

        service_data = None
        if service:
            service_data = TechnicianJobService(id=service.id, name=service.name)

        address_data = None
        if address:
            address_data = TechnicianJobAddress(
                house_no=address.house_no,
                building=address.building,
                area=address.area,
                city=address.city,
                state=address.state,
                pincode=address.pincode,
                latitude=address.latitude,
                longitude=address.longitude,
            )

        return TechnicianJobResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
            payment_status=booking.payment_status.value if hasattr(booking.payment_status, 'value') else str(booking.payment_status),
            booking_date=booking.booking_date,
            preferred_time=booking.preferred_time,
            estimated_price=booking.estimated_price,
            final_price=booking.final_price,
            customer_note=booking.customer_note,
            admin_note=booking.admin_note,
            created_at=booking.created_at,
            customer=customer_data,
            service=service_data,
            address=address_data,
        )

    async def _store_image(self, file: UploadFile, user_id: int, prefix: str) -> str:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        contents = await file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image too large. Maximum size is 5 MB.",
            )
        await file.seek(0)

        upload_dir = Path(BASE_DIR) / settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.split(".")[-1] if file.filename else "jpg"
        filename = f"{prefix}_{user_id}_{uuid4().hex}.{ext}"
        file_path = upload_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return f"{settings.UPLOAD_DIR}/{filename}".replace("\\", "/")

    def _build_response(self, user: User, technician: Any) -> TechnicianResponse:
        return TechnicianResponse(
            id=technician.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            specialization=technician.specialization,
            experience_years=technician.experience_years,
            skills=technician.skills or [],
            languages=technician.languages or [],
            working_hours=technician.working_hours,
            availability=technician.availability,
            latitude=technician.latitude,
            longitude=technician.longitude,
            service_radius_km=technician.service_radius_km,
            is_online=technician.is_online,
            is_verified=getattr(user, "is_verified", False),
            rating=technician.rating,
            reviews_count=technician.reviews_count,
            profile_image=technician.profile_image,
            government_id_image=technician.government_id_image,
            created_at=technician.created_at,
            updated_at=technician.updated_at,
        )

