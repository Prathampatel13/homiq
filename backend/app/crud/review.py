from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.reviews import Review


class ReviewCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Create ─────────────────────────────────────────────────────────

    def create(self, data: dict) -> Review:
        review = Review(**data)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    # ── Get ────────────────────────────────────────────────────────────

    def get(self, review_id: int) -> Optional[Review]:
        return self.db.get(Review, review_id)

    def get_by_booking(self, booking_id: int) -> Optional[Review]:
        stmt = select(Review).where(Review.booking_id == booking_id)
        return self.db.scalar(stmt)

    # ── List ───────────────────────────────────────────────────────────

    def list_reviews(
        self,
        technician_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        min_rating: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Review]:
        stmt = select(Review).order_by(Review.created_at.desc())
        if technician_id is not None:
            stmt = stmt.where(Review.technician_id == technician_id)
        if customer_id is not None:
            stmt = stmt.where(Review.customer_id == customer_id)
        if min_rating is not None:
            stmt = stmt.where(Review.rating >= min_rating)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_reviews(
        self,
        technician_id: Optional[int] = None,
        customer_id: Optional[int] = None,
    ) -> int:
        stmt = select(func.count(Review.id))
        if technician_id is not None:
            stmt = stmt.where(Review.technician_id == technician_id)
        if customer_id is not None:
            stmt = stmt.where(Review.customer_id == customer_id)
        return self.db.scalar(stmt) or 0

    # ── Update ─────────────────────────────────────────────────────────

    def update(self, review_id: int, data: dict) -> Optional[Review]:
        review = self.get(review_id)
        if not review:
            return None
        for key, value in data.items():
            setattr(review, key, value)
        self.db.commit()
        self.db.refresh(review)
        return review

    # ── Delete ─────────────────────────────────────────────────────────

    def delete(self, review_id: int) -> bool:
        review = self.get(review_id)
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True

    # ── Aggregations ───────────────────────────────────────────────────

    def average_rating(self, technician_id: int) -> float:
        stmt = select(func.coalesce(func.avg(Review.rating), 0)).where(
            Review.technician_id == technician_id
        )
        return float(self.db.scalar(stmt) or 0.0)

    def rating_distribution(self, technician_id: int) -> dict[int, int]:
        """Returns a dict of rating -> count for a technician."""
        from sqlalchemy import Integer

        stmt = (
            select(
                Review.rating,
                func.count(Review.id).label("count"),
            )
            .where(Review.technician_id == technician_id)
            .group_by(Review.rating)
            .order_by(Review.rating)
        )
        results = self.db.execute(stmt).all()
        distribution = {i: 0 for i in range(1, 6)}
        for row in results:
            distribution[int(row[0])] = row[1]
        return distribution

