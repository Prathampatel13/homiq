"""
Job posting and application management endpoints.

Company flows (JWT, company role required):
- POST /jobs                 create a job post
- GET  /jobs/my              list my job posts
- GET  /jobs/{job_id}/applications       list applicants
- PUT  /jobs/applications/{app_id}/status  update application status
- PUT  /jobs/{job_id}        update a job post
- DELETE /jobs/{job_id}      delete a job post

Technician flows (JWT, technician role required):
- GET  /jobs                 list active job posts
- POST /jobs/{job_id}/apply  apply to a job
- GET  /jobs/applications/my list my applications
- DELETE /jobs/applications/{app_id}  withdraw an application
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_company, get_current_technician, get_current_user
from app.schemas.jobs import (
    JobApplicationCreate,
    JobApplicationListResponse,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobPostCreate,
    JobPostListResponse,
    JobPostResponse,
    JobPostUpdate,
)
from app.services.jobs import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ════════════════════════════════════════════════════════════
# Job Posts
# ════════════════════════════════════════════════════════════


@router.post(
    "/",
    response_model=JobPostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job post",
    description="**Company required.** Creates a new job post under the authenticated company's profile.",
)
def create_job_post(
    payload: JobPostCreate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Create a job post as a company."""
    return JobService(db).create_job_post(current_user, payload)


@router.get(
    "/",
    response_model=JobPostListResponse,
    summary="List job posts",
    description="Lists active job posts. Technicians use this to discover open jobs. Optionally filter by search text.",
)
def list_job_posts(
    search: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List active job posts (any authenticated user)."""
    return JobService(db).list_job_posts(search=search, offset=offset, limit=limit)


@router.get(
    "/my",
    response_model=JobPostListResponse,
    summary="List my job posts",
    description="**Company required.** Lists job posts created by the authenticated company.",
)
def list_my_job_posts(
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """List the authenticated company's job posts."""
    return JobService(db).list_my_job_posts(
        current_user, is_active=is_active, offset=offset, limit=limit
    )


@router.get(
    "/{job_post_id}",
    response_model=JobPostResponse,
    summary="Get job post by ID",
    description="Returns the full details of a job post, including application count.",
)
def get_job_post(
    job_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a job post by ID."""
    return JobService(db).get_job_post(job_post_id)


@router.put(
    "/{job_post_id}",
    response_model=JobPostResponse,
    summary="Update job post",
    description="**Company required.** Updates one or more fields of a job post owned by the authenticated company.",
)
def update_job_post(
    job_post_id: int,
    payload: JobPostUpdate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Update a job post (partial update)."""
    return JobService(db).update_job_post(current_user, job_post_id, payload)


@router.delete(
    "/{job_post_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete job post",
    description="**Company required.** Deletes a job post owned by the authenticated company.",
)
def delete_job_post(
    job_post_id: int,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a job post (company owner only)."""
    return JobService(db).delete_job_post(current_user, job_post_id)


# ════════════════════════════════════════════════════════════
# Job Applications — Company manages, Technician applies
# ════════════════════════════════════════════════════════════


@router.get(
    "/{job_post_id}/applications",
    response_model=JobApplicationListResponse,
    summary="List job applications",
    description="**Company required.** Lists applications received for a job post owned by the authenticated company.",
)
def list_job_applications(
    job_post_id: int,
    application_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """List applications for a company-owned job post."""
    return JobService(db).list_job_applications(
        current_user,
        job_post_id,
        status=application_status,
        offset=offset,
        limit=limit,
    )


@router.post(
    "/{job_post_id}/apply",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to a job",
    description="**Technician required.** Submits an application for an active job post. Duplicate applications are rejected.",
)
def apply_to_job(
    job_post_id: int,
    payload: JobApplicationCreate,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Apply to a job post as a technician."""
    return JobService(db).apply_to_job(current_user, job_post_id, payload)


@router.get(
    "/applications/my",
    response_model=JobApplicationListResponse,
    summary="List my job applications",
    description="**Technician required.** Lists applications submitted by the authenticated technician.",
)
def list_my_applications(
    application_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """List the authenticated technician's applications."""
    return JobService(db).list_my_applications(
        current_user,
        status=application_status,
        offset=offset,
        limit=limit,
    )


@router.put(
    "/applications/{application_id}/status",
    response_model=JobApplicationResponse,
    summary="Update application status",
    description="**Company required.** Updates the status of an application (applied → shortlisted/accepted/rejected).",
)
def update_application_status(
    application_id: int,
    payload: JobApplicationStatusUpdate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Update an application's status (company owner of the job post only)."""
    return JobService(db).update_application_status(
        current_user, application_id, payload
    )


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_200_OK,
    summary="Withdraw application",
    description="**Technician required.** Withdraws an application. Not allowed once accepted or rejected.",
)
def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Withdraw an application as a technician."""
    return JobService(db).withdraw_application(current_user, application_id)
