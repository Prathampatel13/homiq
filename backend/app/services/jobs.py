"""
Business logic for the Jobs module (job posts + applications).

Company flows:
- Create / update / delete job posts
- List own job posts
- List applicants for a job
- Update application status (applied -> shortlisted/accepted/rejected)

Technician flows:
- List active job posts
- Apply to a job (duplicate check)
- List my applications
- Withdraw application
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.company import CompanyCRUD
from app.crud.jobs import JobCRUD
from app.crud.technician import TechnicianCRUD
from app.models.auth import User
from app.models.jobs import JobApplication, JobPost
from app.schemas.jobs import (
    JobApplicationCreate,
    JobApplicationJobPost,
    JobApplicationListResponse,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationTechnician,
    JobPostCompany,
    JobPostCreate,
    JobPostListResponse,
    JobPostResponse,
    JobPostUpdate,
)

VALID_APPLICATION_STATUSES = {"applied", "shortlisted", "accepted", "rejected"}


class JobService:
    """Service layer for job posts and applications."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = JobCRUD(db)
        self.company_crud = CompanyCRUD(db)
        self.technician_crud = TechnicianCRUD(db)

    # ─────────────────────────────────────────────
    # Company — Job Post management
    # ─────────────────────────────────────────────

    def _get_user_job_or_404(self, user: User, job_post_id: int) -> JobPost:
        job_post = self.crud.get_job_post(job_post_id)
        if not job_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job post not found.",
            )
        if job_post.creator_id != user.id and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage this job post.",
            )
        return job_post

    def create_job_post(
        self, current_user: User, payload: JobPostCreate
    ) -> JobPostResponse:
        data = payload.model_dump(exclude_unset=True)
        data["creator_id"] = current_user.id
        job_post = self.crud.create_job_post(data)
        return self._build_job_post_response(job_post)

    def list_my_job_posts(
        self,
        current_user: User,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> JobPostListResponse:
        job_posts = self.crud.list_job_posts(
            creator_id=current_user.id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_job_posts(
            creator_id=current_user.id,
            is_active=is_active,
        )
        return JobPostListResponse(
            items=[self._build_job_post_response(jp) for jp in job_posts],
            total=int(total),
        )

    def list_job_posts(
        self,
        search: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> JobPostListResponse:
        """Public listing of active job posts."""
        job_posts = self.crud.list_job_posts(
            is_active=True,
            search=search,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_job_posts(
            is_active=True,
            search=search,
        )
        return JobPostListResponse(
            items=[self._build_job_post_response(jp) for jp in job_posts],
            total=int(total),
        )

    def get_job_post(self, job_post_id: int) -> JobPostResponse:
        job_post = self.crud.get_job_post(job_post_id)
        if not job_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job post not found.",
            )
        return self._build_job_post_response(job_post, include_inactive=True)

    def update_job_post(
        self,
        current_user: User,
        job_post_id: int,
        payload: JobPostUpdate,
    ) -> JobPostResponse:
        job_post = self._get_user_job_or_404(current_user, job_post_id)

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            return self._build_job_post_response(job_post)

        updated = self.crud.update_job_post(job_post_id, data)
        return self._build_job_post_response(updated)

    def delete_job_post(
        self, current_user: User, job_post_id: int
    ) -> dict[str, str]:
        self._get_user_job_or_404(current_user, job_post_id)

        deleted = self.crud.delete_job_post(job_post_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete job post.",
            )
        return {"message": "Job post deleted successfully"}

    # ─────────────────────────────────────────────
    # Company — Application management
    # ─────────────────────────────────────────────

    def list_job_applications(
        self,
        current_user: User,
        job_post_id: int,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> JobApplicationListResponse:
        self._get_user_job_or_404(current_user, job_post_id)

        applications = self.crud.list_applications(
            job_post_id=job_post_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_applications(
            job_post_id=job_post_id,
            status=status,
        )
        return JobApplicationListResponse(
            items=[self._build_application_response(app) for app in applications],
            total=int(total),
        )

    def update_application_status(
        self,
        current_user: User,
        application_id: int,
        payload: JobApplicationStatusUpdate,
    ) -> JobApplicationResponse:
        application = self.crud.get_application(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found.",
            )
        if application.job_post.creator_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage this application.",
            )

        updated = self.crud.update_application_status(
            application_id, payload.status
        )
        return self._build_application_response(updated)

    # ─────────────────────────────────────────────
    # Technician — Application flows
    # ─────────────────────────────────────────────

    def _get_technician_or_404(self, user_id: int) -> Any:
        technician = self.technician_crud.get_by_user_id(user_id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )
        return technician

    def apply_to_job(
        self,
        current_user: User,
        job_post_id: int,
        payload: JobApplicationCreate,
    ) -> JobApplicationResponse:
        job_post = self.crud.get_job_post(job_post_id)
        if not job_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job post not found.",
            )
        if not job_post.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This job post is no longer accepting applications.",
            )

        existing = self.crud.get_application_by_job_and_user(
            job_post_id, current_user.id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this job.",
            )

        data = {
            "job_post_id": job_post_id,
            "user_id": current_user.id,
            "cover_letter": payload.cover_letter,
            "status": "applied",
        }
        application = self.crud.create_application(data)
        return self._build_application_response(application)

    def list_my_applications(
        self,
        current_user: User,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> JobApplicationListResponse:
        applications = self.crud.list_applications(
            user_id=current_user.id,
            status=status,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_applications(
            user_id=current_user.id,
            status=status,
        )
        return JobApplicationListResponse(
            items=[self._build_application_response(app) for app in applications],
            total=int(total),
        )

    def withdraw_application(
        self, current_user: User, application_id: int
    ) -> dict[str, str]:
        application = self.crud.get_application(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found.",
            )
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to withdraw this application.",
            )
        if application.status in ("accepted", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot withdraw an application with status '{application.status}'.",
            )

        deleted = self.crud.delete_application(application_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to withdraw application.",
            )
        return {"message": "Application withdrawn successfully"}

    # ─────────────────────────────────────────────
    # Response builders
    # ─────────────────────────────────────────────

    def _build_job_post_response(
        self, job_post: JobPost, include_inactive: bool = False
    ) -> JobPostResponse:
        company = job_post.company_profile
        company_data = None
        if company:
            company_data = JobPostCompany(
                id=company.id,
                company_name=company.company_name,
                industry=company.industry,
                description=company.description,
            )

        application_count = self.crud.count_applications(
            job_post_id=job_post.id
        )

        return JobPostResponse(
            id=job_post.id,
            company_id=job_post.company_id,
            title=job_post.title,
            description=job_post.description,
            requirements=job_post.requirements,
            is_active=job_post.is_active,
            application_count=int(application_count),
            created_at=job_post.created_at,
            company=company_data,
        )

    def _build_application_response(
        self, application: JobApplication
    ) -> JobApplicationResponse:
        from app.schemas.jobs import JobApplicationUser
        job_post = application.job_post
        user = application.user

        job_post_data = None
        if job_post:
            company_name = (
                job_post.company_profile.company_name
                if job_post.company_profile
                else ""
            )
            job_post_data = JobApplicationJobPost(
                id=job_post.id,
                title=job_post.title,
                company_name=company_name,
                is_active=job_post.is_active,
            )

        user_data = None
        if user:
            user_data = JobApplicationUser(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                avatar_url=user.avatar_url,
            )

        return JobApplicationResponse(
            id=application.id,
            job_post_id=application.job_post_id,
            user_id=application.user_id,
            cover_letter=application.cover_letter,
            status=application.status,
            created_at=application.created_at,
            job_post=job_post_data,
            applicant=user_data,
        )
