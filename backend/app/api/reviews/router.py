"""
Review management endpoints.

Customers: Create, update, delete their own reviews.
General: View reviews for technicians.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.reviews import (
    ReviewCreate,
    ReviewListResponse,
    ReviewPatch,
    ReviewResponse,
    ReviewUpdate,
    TechnicianRatingSummaryResponse,
)
from app.services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a review",
    description="Creates a review for a completed booking. Only the booking owner can review. One review per booking.",
)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a review for a completed booking."""
    return ReviewService(db).create_review(current_user, payload)


@router.get(
    "/",
    response_model=ReviewListResponse,
    summary="List reviews",
    description="Returns a paginated list of reviews with optional filters for technician, customer, or minimum rating.",
)
def list_reviews(
    technician_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    min_rating: Optional[int] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """List reviews with optional filters."""
    return ReviewService(db).list_reviews(
        technician_id=technician_id,
        customer_id=customer_id,
        min_rating=min_rating,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Get review by ID",
    description="Returns the details of a specific review by its ID.",
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Get a review by its ID."""
    return ReviewService(db).get_review(review_id)


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Patch a review",
    description="Partially update the rating or comment of a review. Only the review author can update.",
)
def patch_review(
    review_id: int,
    payload: ReviewPatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Patch a review. Only the review author can update."""
    return ReviewService(db).patch_review(current_user, review_id, payload)


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update a review",
    description="Update the rating or comment of a review. Only the review author can update.",
)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update a review. Only the review author can update."""
    return ReviewService(db).update_review(current_user, review_id, payload)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a review",
    description="Delete a review by its ID. Only the review author or an admin can delete.",
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a review. Only the author or admin can delete."""
    return ReviewService(db).delete_review(current_user, review_id)


@router.get(
    "/technician/{technician_id}",
    response_model=ReviewListResponse,
    summary="Get technician reviews",
    description="Returns all reviews for a specific technician.",
)
def get_technician_reviews(
    technician_id: int,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """Get all reviews for a technician."""
    return ReviewService(db).get_technician_reviews(
        technician_id=technician_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/technician/{technician_id}/summary",
    response_model=TechnicianRatingSummaryResponse,
    summary="Get technician rating summary",
    description="Returns rating breakdown (5 to 1 stars), total review count, and average rating for a technician.",
)
def get_technician_rating_summary(
    technician_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Get rating summary and star distribution breakdown for a technician."""
    return ReviewService(db).get_technician_rating_summary(technician_id)


# ─── REVIEW MEDIA ENDPOINTS (Review Photos) ──────────────────────────────

from fastapi import File, UploadFile
from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/{review_id}/images",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload review photo",
    description="Uploads a photo attached to a completed booking review (Review author only).",
)
def upload_review_photo(
    review_id: int,
    file: UploadFile = File(..., description="Review photo (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload review photo."""
    return MediaService(db).upload_review_image(current_user, review_id, file)


@router.get(
    "/{review_id}/images",
    response_model=list[MediaAssetResponse],
    summary="List review photos",
    description="Returns all photos attached to a review.",
)
def list_review_photos(
    review_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """List review photos."""
    return MediaService(db).list_review_images(review_id)


@router.delete(
    "/{review_id}/images/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete review photo",
    description="Deletes a photo from a review (Review author or Admin only).",
)
def delete_review_photo(
    review_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete review photo."""
    return MediaService(db).delete_review_image(current_user, review_id, asset_id)



