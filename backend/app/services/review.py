from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.review import ReviewCRUD
from app.crud.customer import CustomerCRUD
from app.crud.technician import TechnicianCRUD
from app.crud.booking import BookingCRUD
from app.models.auth import User
from app.models.bookings import BookingStatus
from app.schemas.reviews import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)


class ReviewService:
    """Service layer for review operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = ReviewCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.technician_crud = TechnicianCRUD(db)
        self.booking_crud = BookingCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    # ── Create ─────────────────────────────────────────────────────────

    def create_review(self, current_user: User, payload: ReviewCreate) -> ReviewResponse:
        """Create a review for a completed booking."""
        customer_id = self._get_customer_id(current_user)

        # Verify booking exists and is completed
        booking = self.booking_crud.get_booking(payload.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        # Verify booking belongs to customer
        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This booking does not belong to you.",
            )

        # Verify booking is completed (post-completion pipeline)
        if booking.status not in [
            BookingStatus.COMPLETED,
            BookingStatus.WAITING_PAYMENT,
            BookingStatus.PAID,
            BookingStatus.REVIEW_PENDING,
            BookingStatus.CLOSED,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings.",
            )

        # Check for duplicate review
        existing = self.crud.get_by_booking(payload.booking_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this booking.",
            )

        # Verify technician exists
        technician = self.technician_crud.get_by_technician_id(payload.technician_id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found.",
            )

        data = payload.model_dump()
        data["customer_id"] = customer_id
        review = self.crud.create(data)

        # Update technician average rating
        avg_rating = self.crud.average_rating(payload.technician_id)
        review_count = self.crud.count_reviews(technician_id=payload.technician_id)
        self.technician_crud.update(
            payload.technician_id,
            {"rating": round(avg_rating, 2), "reviews_count": review_count},
        )

        return ReviewResponse.model_validate(review)

    # ── Get ────────────────────────────────────────────────────────────

    def get_review(self, review_id: int) -> ReviewResponse:
        """Get a review by ID."""
        review = self.crud.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found.",
            )
        return ReviewResponse.model_validate(review)

    # ── List ───────────────────────────────────────────────────────────

    def list_reviews(
        self,
        technician_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        min_rating: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> ReviewListResponse:
        """List reviews with optional filters."""
        reviews = self.crud.list_reviews(
            technician_id=technician_id,
            customer_id=customer_id,
            min_rating=min_rating,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_reviews(
            technician_id=technician_id,
            customer_id=customer_id,
        )
        return ReviewListResponse(
            items=[ReviewResponse.model_validate(r) for r in reviews],
            total=total,
        )

    # ── Update ─────────────────────────────────────────────────────────

    def update_review(
        self, current_user: User, review_id: int, payload: ReviewUpdate
    ) -> ReviewResponse:
        """Update a review. Only the review author can update."""
        review = self.crud.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found.",
            )

        customer_id = self._get_customer_id(current_user)
        if review.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews.",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )

        updated = self.crud.update(review_id, data)

        # Update technician average rating
        if "rating" in data:
            avg_rating = self.crud.average_rating(review.technician_id)
            self.technician_crud.update(
                review.technician_id,
                {"rating": round(avg_rating, 2)},
            )

        return ReviewResponse.model_validate(updated)

    # ── Delete ─────────────────────────────────────────────────────────

    def delete_review(self, current_user: User, review_id: int) -> dict[str, str]:
        """Delete a review. Only the review author or admin can delete."""
        review = self.crud.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found.",
            )

        customer_id = self._get_customer_id(current_user)
        if review.customer_id != customer_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews.",
            )

        deleted = self.crud.delete(review_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete review.",
            )

        # Update technician rating
        avg_rating = self.crud.average_rating(review.technician_id)
        review_count = self.crud.count_reviews(technician_id=review.technician_id)
        self.technician_crud.update(
            review.technician_id,
            {"rating": round(avg_rating, 2), "reviews_count": review_count},
        )

        return {"message": "Review deleted successfully."}

    # ── Technician Reviews ─────────────────────────────────────────────

    def get_technician_reviews(
        self,
        technician_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> ReviewListResponse:
        """Get all reviews for a specific technician."""
        return self.list_reviews(
            technician_id=technician_id,
            offset=offset,
            limit=limit,
        )

    def get_technician_rating_summary(self, technician_id: int):
        """Get rating summary and star distribution breakdown for a technician."""
        from app.schemas.reviews import TechnicianRatingSummaryResponse
        technician = self.technician_crud.get_by_technician_id(technician_id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found.",
            )
        summary = self.crud.get_technician_rating_summary(technician_id)
        return TechnicianRatingSummaryResponse.model_validate(summary)

    def patch_review(
        self, current_user: User, review_id: int, payload: Any
    ) -> ReviewResponse:
        """Patch rating or comment of an existing review."""
        update_payload = ReviewUpdate(**payload.model_dump(exclude_unset=True, exclude_none=True))
        return self.update_review(current_user, review_id, update_payload)


