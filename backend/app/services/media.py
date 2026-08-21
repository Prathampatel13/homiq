"""
Media & Document Management Service Layer.

Binds Cloudinary integration, strict validation, transactional rollback safety,
database persistence (MediaAsset), and role-based permissions for:
- User avatars (with safe replacement)
- Technician media (avatar, portfolio, certificates, verification docs)
- Company media (logo, gallery, docs)
- Service media (featured image, gallery)
- Booking media (before, after, attachments)
- Complaint evidence attachments
- Review photos
- Job recruitment resumes & documents
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.customer import CustomerCRUD
from app.crud.media import MediaCRUD
from app.crud.technician import TechnicianCRUD
from app.crud.user import UserCRUD
from app.models.auth import User
from app.models.bookings import Booking
from app.models.media import MediaAsset, MediaAssetType
from app.models.reviews import Review
from app.models.services import Service
from app.models.users import Company, Customer, Technician
from app.schemas.media import (
    DocumentApprovalPayload,
    DocumentStatusEnum,
    DocumentTypeEnum,
    MediaAssetListResponse,
    MediaAssetResponse,
    MediaOptimizedUrlRequest,
    MediaOptimizedUrlResponse,
    MediaResponse,
    StandardMediaResponse,
    TechnicianDocumentResponse,
)
from app.services.cloudinary_service import cloudinary_service

logger = logging.getLogger("homiq.media_service")

# In-memory document verification registry for technician documents if needed
DOCUMENT_STORE: dict[str, dict[str, Any]] = {}


class MediaService:
    """Enterprise service layer coordinating Cloudinary operations and database state."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = MediaCRUD(db)
        self.user_crud = UserCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.technician_crud = TechnicianCRUD(db)
        self.cloudinary = cloudinary_service

    # ── 1. Generic Upload & Safe Persistence ─────────────────────────────────

    def upload_asset(
        self,
        current_user: User,
        file: UploadFile,
        asset_type: MediaAssetType = MediaAssetType.PROFILE_AVATAR,
        owner_id: Optional[int] = None,
        owner_type: Optional[str] = None,
    ) -> MediaAssetResponse:
        """Uploads a media asset with strict validation, stores in Cloudinary, and persists DB record."""
        resolved_owner_id = owner_id if owner_id is not None else current_user.id
        resolved_owner_type = owner_type or ("technician" if current_user.role_id == 2 else "user")

        upload_res = self.cloudinary.upload_file(
            file=file,
            owner_id=resolved_owner_id,
            owner_type=resolved_owner_type,
            asset_type=asset_type,
        )

        public_id = upload_res["cloudinary_public_id"]
        secure_url = upload_res["secure_url"]

        try:
            db_asset = self.crud.create_media_asset(
                owner_id=resolved_owner_id,
                owner_type=resolved_owner_type,
                asset_type=asset_type,
                cloudinary_public_id=public_id,
                cloudinary_asset_id=upload_res.get("cloudinary_asset_id"),
                secure_url=secure_url,
                resource_type=upload_res.get("resource_type", "image"),
                format=upload_res.get("format", "png"),
                width=upload_res.get("width"),
                height=upload_res.get("height"),
                file_size=upload_res.get("file_size", 0),
            )
        except Exception as exc:
            logger.error("DB persistence failed after upload; rolling back Cloudinary asset %s: %s", public_id, exc)
            self.cloudinary.delete_asset(public_id, resource_type=upload_res.get("resource_type", "image"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while registering uploaded asset. Upload safely rolled back.",
            )

        thumbnail_url = self.cloudinary.get_thumbnail_url(public_id) if db_asset.resource_type == "image" else None

        return MediaAssetResponse(
            id=db_asset.id,
            owner_id=db_asset.owner_id,
            owner_type=db_asset.owner_type,
            asset_type=db_asset.asset_type,
            cloudinary_asset_id=db_asset.cloudinary_asset_id,
            cloudinary_public_id=db_asset.cloudinary_public_id,
            secure_url=db_asset.secure_url,
            thumbnail_url=thumbnail_url,
            resource_type=db_asset.resource_type,
            format=db_asset.format,
            width=db_asset.width,
            height=db_asset.height,
            file_size=db_asset.file_size,
            created_at=db_asset.created_at,
            updated_at=db_asset.updated_at,
        )

    # ── 2. User Profile Avatar with Transactional Rollback Safety ────────────

    def update_user_avatar(self, current_user: User, file: UploadFile) -> StandardMediaResponse:
        """
        Upload new avatar with atomic safety:
        1. Upload new image to Cloudinary first.
        2. Update DB. If DB update fails, delete new Cloudinary asset (rollback).
        3. Delete old Cloudinary asset only after DB success. If old deletion fails, keep new active.
        """
        # Find existing avatar if any
        old_assets = self.crud.get_assets_by_owner(
            owner_id=current_user.id,
            owner_type="user",
            asset_type=MediaAssetType.PROFILE_AVATAR,
        )
        old_public_id = old_assets[0].cloudinary_public_id if old_assets else None

        # 1. Upload new image
        upload_res = self.cloudinary.upload_file(
            file=file,
            owner_id=current_user.id,
            owner_type="user",
            asset_type=MediaAssetType.PROFILE_AVATAR,
        )
        new_public_id = upload_res["cloudinary_public_id"]
        new_secure_url = upload_res["secure_url"]

        # 2. Update DB
        try:
            db_asset = self.crud.create_media_asset(
                owner_id=current_user.id,
                owner_type="user",
                asset_type=MediaAssetType.PROFILE_AVATAR,
                cloudinary_public_id=new_public_id,
                cloudinary_asset_id=upload_res.get("cloudinary_asset_id"),
                secure_url=new_secure_url,
                resource_type="image",
                format=upload_res.get("format", "png"),
                width=upload_res.get("width"),
                height=upload_res.get("height"),
                file_size=upload_res.get("file_size", 0),
            )
            self.user_crud.update_avatar_url(current_user.id, new_secure_url)

            # Sync with role profiles
            if current_user.role and current_user.role.name.lower() == "customer":
                cust = self.customer_crud.get_by_user_id(current_user.id)
                if cust:
                    self.crud.update_customer_profile_image(cust.id, new_secure_url)
            elif current_user.role and current_user.role.name.lower() == "technician":
                tech = self.technician_crud.get_by_user_id(current_user.id)
                if tech:
                    self.crud.update_technician_profile_image(tech.id, new_secure_url)
        except Exception as exc:
            logger.error("DB update failed during avatar replacement; cleaning up new asset %s: %s", new_public_id, exc)
            self.cloudinary.delete_asset(new_public_id, resource_type="image")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during avatar update. Upload safely rolled back.",
            )

        # 3. Clean up old asset
        if old_public_id and old_public_id != new_public_id:
            try:
                self.cloudinary.delete_asset(old_public_id, resource_type="image")
                self.crud.delete_media_asset(old_public_id)
            except Exception as del_exc:
                logger.warning("Failed to delete old avatar asset %s: %s (new avatar remains active)", old_public_id, del_exc)

        thumbnail_url = self.cloudinary.get_thumbnail_url(new_public_id)

        return StandardMediaResponse(
            success=True,
            message="Profile avatar updated successfully.",
            data={
                "id": db_asset.id,
                "url": new_secure_url,
                "secure_url": new_secure_url,
                "thumbnail_url": thumbnail_url,
                "public_id": new_public_id,
                "asset_type": MediaAssetType.PROFILE_AVATAR.value,
            },
        )

    def delete_user_avatar(self, current_user: User) -> StandardMediaResponse:
        """Deletes the authenticated user's avatar from Cloudinary and DB."""
        assets = self.crud.get_assets_by_owner(
            owner_id=current_user.id,
            owner_type="user",
            asset_type=MediaAssetType.PROFILE_AVATAR,
        )
        for asset in assets:
            try:
                self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type="image")
            except Exception:
                pass
            self.crud.delete_media_asset(asset.cloudinary_public_id)

        self.user_crud.update_avatar_url(current_user.id, None)
        if current_user.role and current_user.role.name.lower() == "customer":
            cust = self.customer_crud.get_by_user_id(current_user.id)
            if cust:
                self.crud.delete_customer_profile_image(cust.id)
        elif current_user.role and current_user.role.name.lower() == "technician":
            tech = self.technician_crud.get_by_user_id(current_user.id)
            if tech:
                self.crud.delete_technician_profile_image(tech.id)

        return StandardMediaResponse(
            success=True,
            message="Profile avatar removed successfully.",
            data=None,
        )

    # ── 3. Technician Portfolio & Certificates ───────────────────────────────

    def upload_technician_portfolio(self, current_user: User, file: UploadFile) -> StandardMediaResponse:
        """Upload a portfolio work sample for the authenticated technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician profile not found.")

        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.TECHNICIAN_PORTFOLIO,
            owner_id=tech.id,
            owner_type="technician",
        )
        return StandardMediaResponse(
            success=True,
            message="Portfolio work image uploaded successfully.",
            data=res.model_dump(),
        )

    def list_technician_portfolio(self, current_user: User) -> list[MediaAssetResponse]:
        """List portfolio images for the authenticated technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician profile not found.")

        res = self.list_owner_assets(owner_id=tech.id, owner_type="technician", asset_type=MediaAssetType.TECHNICIAN_PORTFOLIO)
        return res.items

    def delete_technician_portfolio(self, current_user: User, asset_id: int) -> StandardMediaResponse:
        """Delete a portfolio image owned by the technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "technician" or (tech and asset.owner_id != tech.id and not current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Portfolio item deleted successfully.")

    def upload_technician_certificate(self, current_user: User, file: UploadFile) -> StandardMediaResponse:
        """Upload a professional certificate (Image/PDF) for the authenticated technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician profile not found.")

        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.TECHNICIAN_CERTIFICATE,
            owner_id=tech.id,
            owner_type="technician",
        )
        return StandardMediaResponse(
            success=True,
            message="Certificate document uploaded successfully.",
            data=res.model_dump(),
        )

    def list_technician_certificates(self, current_user: User) -> list[MediaAssetResponse]:
        """List certificates for the authenticated technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician profile not found.")

        res = self.list_owner_assets(owner_id=tech.id, owner_type="technician", asset_type=MediaAssetType.TECHNICIAN_CERTIFICATE)
        return res.items

    def delete_technician_certificate(self, current_user: User, asset_id: int) -> StandardMediaResponse:
        """Delete a certificate owned by the technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "technician" or (tech and asset.owner_id != tech.id and not current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Certificate removed successfully.")

    # ── 4. Company Media (Logo & Gallery) ───────────────────────────────────

    def upload_company_logo(self, current_user: User, file: UploadFile) -> StandardMediaResponse:
        """Upload brand logo for authenticated company."""
        stmt = select(Company).where(Company.user_id == current_user.id)
        company = self.db.scalars(stmt).first()
        if not company and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")

        company_id = company.id if company else current_user.id
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.COMPANY_LOGO,
            owner_id=company_id,
            owner_type="company",
        )
        return StandardMediaResponse(
            success=True,
            message="Company logo uploaded successfully.",
            data=res.model_dump(),
        )

    def upload_company_gallery(self, current_user: User, file: UploadFile) -> StandardMediaResponse:
        """Upload gallery photo for authenticated company."""
        stmt = select(Company).where(Company.user_id == current_user.id)
        company = self.db.scalars(stmt).first()
        if not company and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")

        company_id = company.id if company else current_user.id
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.SERVICE_GALLERY,
            owner_id=company_id,
            owner_type="company",
        )
        return StandardMediaResponse(
            success=True,
            message="Company gallery photo uploaded successfully.",
            data=res.model_dump(),
        )

    def list_company_gallery(self, company_id: int) -> list[MediaAssetResponse]:
        """Public listing of company gallery photos."""
        res = self.list_owner_assets(owner_id=company_id, owner_type="company")
        return res.items

    def delete_company_gallery(self, current_user: User, asset_id: int) -> StandardMediaResponse:
        """Delete company gallery photo."""
        stmt = select(Company).where(Company.user_id == current_user.id)
        company = self.db.scalars(stmt).first()
        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "company" or (company and asset.owner_id != company.id and not current_user.is_superuser):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company media asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Company media asset deleted successfully.")

    # ── 5. Service Media (Thumbnail & Gallery) ───────────────────────────────

    def upload_service_gallery(self, current_user: User, service_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload image to service gallery (Admin or Company)."""
        service = self.db.get(Service, service_id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.SERVICE_GALLERY,
            owner_id=service_id,
            owner_type="service",
        )
        return StandardMediaResponse(
            success=True,
            message="Service gallery image uploaded successfully.",
            data=res.model_dump(),
        )

    def list_service_gallery(self, service_id: int) -> list[MediaAssetResponse]:
        """List gallery images for a service."""
        service = self.db.get(Service, service_id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

        res = self.list_owner_assets(owner_id=service_id, owner_type="service")
        return res.items

    def delete_service_gallery(self, current_user: User, service_id: int, asset_id: int) -> StandardMediaResponse:
        """Delete service gallery image (Admin only)."""
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required.")

        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "service" or asset.owner_id != service_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service media asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Service gallery item deleted successfully.")

    # ── 6. Booking Media (Before, After, Attachments) ────────────────────────

    def _verify_booking_participant(self, current_user: User, booking_id: int) -> Booking:
        """Ensures user is the customer owner, assigned technician, or admin."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        if current_user.is_superuser:
            return booking

        is_customer = booking.customer and booking.customer.user_id == current_user.id
        is_tech = booking.technician and booking.technician.user_id == current_user.id

        if not is_customer and not is_tech:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access media for this booking.",
            )
        return booking

    def upload_booking_before_image(self, current_user: User, booking_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload before-work photo for a booking."""
        self._verify_booking_participant(current_user, booking_id)
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.BOOKING_BEFORE,
            owner_id=booking_id,
            owner_type="booking",
        )
        return StandardMediaResponse(
            success=True,
            message="Before-service image uploaded successfully.",
            data=res.model_dump(),
        )

    def upload_booking_after_image(self, current_user: User, booking_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload after-work photo for a booking."""
        self._verify_booking_participant(current_user, booking_id)
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.BOOKING_AFTER,
            owner_id=booking_id,
            owner_type="booking",
        )
        return StandardMediaResponse(
            success=True,
            message="After-service image uploaded successfully.",
            data=res.model_dump(),
        )

    def upload_booking_attachment(self, current_user: User, booking_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload document/attachment for a booking."""
        self._verify_booking_participant(current_user, booking_id)
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.BOOKING_ATTACHMENT,
            owner_id=booking_id,
            owner_type="booking",
        )
        return StandardMediaResponse(
            success=True,
            message="Booking attachment uploaded successfully.",
            data=res.model_dump(),
        )

    def list_booking_media(self, current_user: User, booking_id: int) -> list[MediaAssetResponse]:
        """List all before, after, and attachment media for a booking."""
        self._verify_booking_participant(current_user, booking_id)
        res = self.list_owner_assets(owner_id=booking_id, owner_type="booking")
        return res.items

    def delete_booking_media(self, current_user: User, booking_id: int, asset_id: int) -> StandardMediaResponse:
        """Delete a media asset from a booking."""
        self._verify_booking_participant(current_user, booking_id)
        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "booking" or asset.owner_id != booking_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking media asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Booking media asset deleted successfully.")

    # ── 7. Complaint Evidence & Attachments ─────────────────────────────────

    def upload_complaint_attachment(self, current_user: User, complaint_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload evidence image/document for a customer complaint."""
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.COMPLAINT_ATTACHMENT,
            owner_id=complaint_id,
            owner_type="complaint",
        )
        return StandardMediaResponse(
            success=True,
            message="Complaint evidence attachment uploaded successfully.",
            data=res.model_dump(),
        )

    def list_complaint_attachments(self, current_user: User, complaint_id: int) -> list[MediaAssetResponse]:
        """List all evidence attachments for a complaint."""
        res = self.list_owner_assets(owner_id=complaint_id, owner_type="complaint")
        return res.items

    # ── 8. Review Photos ────────────────────────────────────────────────────

    def upload_review_image(self, current_user: User, review_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload review photo (Review author only)."""
        review = self.db.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        cust = self.customer_crud.get_by_user_id(current_user.id)
        if (not cust or review.customer_id != cust.id) and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only add photos to your own reviews.")

        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.REVIEW_IMAGE,
            owner_id=review_id,
            owner_type="review",
        )
        return StandardMediaResponse(
            success=True,
            message="Review image uploaded successfully.",
            data=res.model_dump(),
        )

    def list_review_images(self, review_id: int) -> list[MediaAssetResponse]:
        """List all photos attached to a review."""
        res = self.list_owner_assets(owner_id=review_id, owner_type="review")
        return res.items

    def delete_review_image(self, current_user: User, review_id: int, asset_id: int) -> StandardMediaResponse:
        """Delete a photo attached to a review."""
        review = self.db.get(Review, review_id)
        cust = self.customer_crud.get_by_user_id(current_user.id)
        if review and (not cust or review.customer_id != cust.id) and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete photos from your own reviews.")

        asset = self.crud.get_by_id(asset_id)
        if not asset or asset.owner_type != "review" or asset.owner_id != review_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review image asset not found.")

        self.cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
        self.crud.delete_media_asset(asset.cloudinary_public_id)
        return StandardMediaResponse(success=True, message="Review image deleted successfully.")

    # ── 9. Job Resumes & Recruitment Documents ──────────────────────────────

    def upload_job_resume(self, current_user: User, job_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload applicant resume (PDF) for a job."""
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.JOB_RESUME,
            owner_id=job_id,
            owner_type="job",
        )
        return StandardMediaResponse(
            success=True,
            message="Resume document uploaded successfully.",
            data=res.model_dump(),
        )

    def upload_job_document(self, current_user: User, job_id: int, file: UploadFile) -> StandardMediaResponse:
        """Upload job description or specification document."""
        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=MediaAssetType.JOB_DOCUMENT,
            owner_id=job_id,
            owner_type="job",
        )
        return StandardMediaResponse(
            success=True,
            message="Job document uploaded successfully.",
            data=res.model_dump(),
        )

    def list_job_documents(self, current_user: User, job_id: int) -> list[MediaAssetResponse]:
        """List documents and resumes associated with a job post."""
        res = self.list_owner_assets(owner_id=job_id, owner_type="job")
        return res.items

    # ── 10. Retrieval, Listing & URL Optimization ───────────────────────────

    def get_media_details(self, public_id: str) -> MediaAssetResponse:
        """Fetch media asset details from DB and generate optimized thumbnail."""
        asset = self.crud.get_by_public_id(public_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Media asset with public ID '{public_id}' not found.",
            )

        thumbnail_url = self.cloudinary.get_thumbnail_url(public_id) if asset.resource_type == "image" else None

        return MediaAssetResponse(
            id=asset.id,
            owner_id=asset.owner_id,
            owner_type=asset.owner_type,
            asset_type=asset.asset_type,
            cloudinary_asset_id=asset.cloudinary_asset_id,
            cloudinary_public_id=asset.cloudinary_public_id,
            secure_url=asset.secure_url,
            thumbnail_url=thumbnail_url,
            resource_type=asset.resource_type,
            format=asset.format,
            width=asset.width,
            height=asset.height,
            file_size=asset.file_size,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )

    def list_owner_assets(
        self,
        owner_id: int,
        owner_type: str,
        asset_type: Optional[MediaAssetType] = None,
    ) -> MediaAssetListResponse:
        """List all media assets belonging to an owner."""
        assets = self.crud.get_assets_by_owner(owner_id=owner_id, owner_type=owner_type, asset_type=asset_type)
        items = []
        for asset in assets:
            thumb = self.cloudinary.get_thumbnail_url(asset.cloudinary_public_id) if asset.resource_type == "image" else None
            items.append(
                MediaAssetResponse(
                    id=asset.id,
                    owner_id=asset.owner_id,
                    owner_type=asset.owner_type,
                    asset_type=asset.asset_type,
                    cloudinary_asset_id=asset.cloudinary_asset_id,
                    cloudinary_public_id=asset.cloudinary_public_id,
                    secure_url=asset.secure_url,
                    thumbnail_url=thumb,
                    resource_type=asset.resource_type,
                    format=asset.format,
                    width=asset.width,
                    height=asset.height,
                    file_size=asset.file_size,
                    created_at=asset.created_at,
                    updated_at=asset.updated_at,
                )
            )
        return MediaAssetListResponse(total=len(items), items=items)

    def get_optimized_url(self, public_id: str, payload: MediaOptimizedUrlRequest) -> MediaOptimizedUrlResponse:
        """Generate optimized / transformed Cloudinary URL."""
        opt_url = self.cloudinary.get_optimized_url(
            public_id=public_id,
            width=payload.width,
            height=payload.height,
            crop=payload.crop,
            quality=payload.quality,
            fetch_format=payload.fetch_format,
            gravity=payload.gravity,
        )
        thumb_url = self.cloudinary.get_thumbnail_url(public_id)
        return MediaOptimizedUrlResponse(
            public_id=public_id,
            optimized_url=opt_url,
            thumbnail_url=thumb_url,
        )

    def delete_media(self, current_user: User, public_id: str) -> dict[str, str]:
        """Delete media asset from Cloudinary and database."""
        asset = self.crud.get_by_public_id(public_id)
        if asset:
            if not current_user.is_superuser and asset.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to delete this media asset.",
                )
            self.cloudinary.delete_asset(public_id, resource_type=asset.resource_type)
            self.crud.delete_media_asset(public_id)
        else:
            self.cloudinary.delete_asset(public_id)

        return {"message": "Media asset deleted successfully."}

    def replace_media(
        self,
        current_user: User,
        public_id: str,
        file: UploadFile,
        asset_type: Optional[MediaAssetType] = None,
    ) -> MediaAssetResponse:
        """Replace existing Cloudinary asset with new file."""
        asset = self.crud.get_by_public_id(public_id)
        target_asset_type = asset_type or (asset.asset_type if asset else MediaAssetType.PROFILE_AVATAR)
        owner_id = asset.owner_id if asset else current_user.id
        owner_type = asset.owner_type if asset else "user"

        if asset:
            self.cloudinary.delete_asset(public_id, resource_type=asset.resource_type)
            self.crud.delete_media_asset(public_id)

        return self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=target_asset_type,
            owner_id=owner_id,
            owner_type=owner_type,
        )

    # ── 11. Legacy Upload Adapter (Backwards Compatibility) ──────────────────

    def upload_file(
        self,
        current_user: User,
        file: UploadFile,
        folder: str = "homiq",
    ) -> MediaResponse:
        """Legacy upload adapter returning MediaResponse."""
        asset_type = MediaAssetType.PROFILE_AVATAR if "profile" in folder else MediaAssetType.SERVICE_IMAGE
        res = self.upload_asset(current_user, file=file, asset_type=asset_type)
        return MediaResponse(
            public_id=res.cloudinary_public_id,
            url=res.secure_url,
            secure_url=res.secure_url,
            thumbnail_url=res.thumbnail_url or res.secure_url,
            format=res.format,
            width=res.width or 0,
            height=res.height or 0,
            bytes=res.file_size,
            folder=folder,
            uploaded_at=res.created_at,
        )

    # ── 12. Technician Verification Documents ───────────────────────────────

    def upload_technician_document(
        self,
        current_user: User,
        doc_type: DocumentTypeEnum,
        file: UploadFile,
    ) -> TechnicianDocumentResponse:
        """Upload and persist technician verification document (Aadhaar, PAN, License, Certificate)."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )

        asset_type = (
            MediaAssetType.TECHNICIAN_CERTIFICATE
            if doc_type == DocumentTypeEnum.CERTIFICATE
            else MediaAssetType.IDENTITY_DOCUMENT
        )

        res = self.upload_asset(
            current_user=current_user,
            file=file,
            asset_type=asset_type,
            owner_id=tech.id,
            owner_type="technician",
        )

        doc_id = f"doc_{uuid4().hex[:8]}"
        doc_record = {
            "id": doc_id,
            "technician_id": tech.id,
            "doc_type": doc_type,
            "url": res.secure_url,
            "public_id": res.cloudinary_public_id,
            "status": DocumentStatusEnum.PENDING,
            "rejection_reason": None,
            "uploaded_at": datetime.now(timezone.utc),
        }
        DOCUMENT_STORE[doc_id] = doc_record

        self.crud.update_technician_government_id(tech.id, res.secure_url)
        return TechnicianDocumentResponse.model_validate(doc_record)

    def get_technician_documents(self, current_user: User) -> list[TechnicianDocumentResponse]:
        """List uploaded verification documents for current technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )

        tech_id = tech.id if tech else None
        return [
            TechnicianDocumentResponse.model_validate(doc)
            for doc in DOCUMENT_STORE.values()
            if tech_id is None or doc["technician_id"] == tech_id
        ]

    def approve_technician_document(self, current_user: User, doc_id: str) -> TechnicianDocumentResponse:
        """Admin approve technician verification document."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can approve documents.",
            )

        doc = DOCUMENT_STORE.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        doc["status"] = DocumentStatusEnum.APPROVED
        doc["rejection_reason"] = None
        return TechnicianDocumentResponse.model_validate(doc)

    def reject_technician_document(
        self,
        current_user: User,
        doc_id: str,
        reason: Optional[str] = "Document illegible or invalid.",
    ) -> TechnicianDocumentResponse:
        """Admin reject technician verification document."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can reject documents.",
            )

        doc = DOCUMENT_STORE.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        doc["status"] = DocumentStatusEnum.REJECTED
        doc["rejection_reason"] = reason
        return TechnicianDocumentResponse.model_validate(doc)
