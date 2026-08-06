"""
Repository-style CRUD operations for job posts and job applications.

Follows the same pattern as ``CompanyCRUD`` and ``TechnicianCRUD``.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.jobs import JobApplication, JobPost
from app.models.users import Company, Technician


class JobCRUD:
    """CRUD operations for job posts and job applications."""

    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────
    # Job Posts
    # ─────────────────────────────────────────────

    def create_job_post(self, data: dict[str, Any]) -> JobPost:
        job_post = JobPost(**data)
        self.db.add(job_post)
        self.db.commit()
        self.db.refresh(job_post)
        return job_post

    def get_job_post(self, job_post_id: int) -> Optional[JobPost]:
        """Fetch a single job post with its company relationship loaded."""
        stmt = (
            select(JobPost)
            .options(joinedload(JobPost.company_profile))
            .where(JobPost.id == job_post_id)
        )
        return self.db.scalar(stmt)

    def list_job_posts(
        self,
        company_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[JobPost]:
        """List job posts with optional filters, newest first."""
        stmt = (
            select(JobPost)
            .options(joinedload(JobPost.company_profile))
            .order_by(JobPost.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if company_id is not None:
            stmt = stmt.where(JobPost.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(JobPost.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                JobPost.title.ilike(pattern)
                | JobPost.description.ilike(pattern)
                | JobPost.requirements.ilike(pattern)
            )
        return list(self.db.execute(stmt).scalars().all())

    def count_job_posts(
        self,
        company_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(JobPost.id))
        if company_id is not None:
            stmt = stmt.where(JobPost.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(JobPost.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                JobPost.title.ilike(pattern)
                | JobPost.description.ilike(pattern)
                | JobPost.requirements.ilike(pattern)
            )
        return self.db.scalar(stmt) or 0

    def update_job_post(
        self, job_post_id: int, data: dict[str, Any]
    ) -> Optional[JobPost]:
        if not data:
            return self.get_job_post(job_post_id)

        stmt = (
            update(JobPost)
            .where(JobPost.id == job_post_id)
            .values(**data)
            .returning(JobPost)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def delete_job_post(self, job_post_id: int) -> bool:
        job_post = self.get_job_post(job_post_id)
        if not job_post:
            return False
        self.db.delete(job_post)
        self.db.commit()
        return True

    # ─────────────────────────────────────────────
    # Job Applications
    # ─────────────────────────────────────────────

    def create_application(self, data: dict[str, Any]) -> JobApplication:
        application = JobApplication(**data)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """Fetch a single application with job post and technician loaded."""
        stmt = (
            select(JobApplication)
            .options(
                joinedload(JobApplication.job_post),
                joinedload(JobApplication.technician_profile),
            )
            .where(JobApplication.id == application_id)
        )
        return self.db.scalar(stmt)

    def get_application_by_job_and_technician(
        self, job_post_id: int, technician_id: int
    ) -> Optional[JobApplication]:
        """Check if a technician has already applied to a job."""
        return self.db.scalar(
            select(JobApplication).where(
                JobApplication.job_post_id == job_post_id,
                JobApplication.technician_id == technician_id,
            )
        )

    def list_applications(
        self,
        job_post_id: Optional[int] = None,
        technician_id: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        """List applications with optional filters, newest first."""
        stmt = (
            select(JobApplication)
            .options(
                joinedload(JobApplication.job_post).joinedload(
                    JobPost.company_profile
                ),
                joinedload(JobApplication.technician_profile).joinedload(
                    Technician.user
                ),
            )
            .order_by(JobApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if job_post_id is not None:
            stmt = stmt.where(JobApplication.job_post_id == job_post_id)
        if technician_id is not None:
            stmt = stmt.where(JobApplication.technician_id == technician_id)
        if status:
            stmt = stmt.where(JobApplication.status == status)
        return list(self.db.execute(stmt).scalars().all())

    def count_applications(
        self,
        job_post_id: Optional[int] = None,
        technician_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(JobApplication.id))
        if job_post_id is not None:
            stmt = stmt.where(JobApplication.job_post_id == job_post_id)
        if technician_id is not None:
            stmt = stmt.where(JobApplication.technician_id == technician_id)
        if status:
            stmt = stmt.where(JobApplication.status == status)
        return self.db.scalar(stmt) or 0

    def update_application_status(
        self, application_id: int, status: str
    ) -> Optional[JobApplication]:
        result = self.db.execute(
            update(JobApplication)
            .where(JobApplication.id == application_id)
            .values(status=status)
            .returning(JobApplication)
        )
        self.db.commit()
        return result.scalar_one_or_none()

    def delete_application(self, application_id: int) -> bool:
        application = self.get_application(application_id)
        if not application:
            return False
        self.db.delete(application)
        self.db.commit()
        return True

