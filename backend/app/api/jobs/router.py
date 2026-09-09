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
    description="**User required.** Creates a new job post under the authenticated user's profile.",
)
def create_job_post(
    payload: JobPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a job post as a user."""
    return JobService(db).create_job_post(current_user, payload)


@router.get(
    "/",
    response_model=JobPostListResponse,
    summary="List job posts",
    description="Lists active job posts. Open for public discovery and search.",
)
def list_job_posts(
    search: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """List active job posts."""
    return JobService(db).list_job_posts(search=search, offset=offset, limit=limit)


@router.get(
    "/my",
    response_model=JobPostListResponse,
    summary="List my job posts",
    description="**User required.** Lists job posts created by the authenticated user.",
)
@router.get(
    "/company/my",
    response_model=JobPostListResponse,
    summary="List my job posts alias",
    description="**User required.** Lists job posts created by the authenticated user.",
)
def list_my_job_posts(
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List the authenticated user's job posts."""
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
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a job post by ID."""
    return JobService(db).get_job_post(job_post_id)


@router.put(
    "/{job_post_id}",
    response_model=JobPostResponse,
    summary="Update job post",
    description="**User required.** Updates one or more fields of a job post owned by the authenticated user.",
)
def update_job_post(
    job_post_id: int,
    payload: JobPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update a job post (partial update)."""
    return JobService(db).update_job_post(current_user, job_post_id, payload)


@router.delete(
    "/{job_post_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete job post",
    description="**User required.** Deletes a job post owned by the authenticated user.",
)
def delete_job_post(
    job_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a job post (owner only)."""
    return JobService(db).delete_job_post(current_user, job_post_id)


# ════════════════════════════════════════════════════════════
# Job Applications — User manages, User applies
# ════════════════════════════════════════════════════════════


@router.get(
    "/{job_post_id}/applications",
    response_model=JobApplicationListResponse,
    summary="List job applications",
    description="**User required.** Lists applications received for a job post owned by the authenticated user.",
)
def list_job_applications(
    job_post_id: int,
    application_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List applications for a user-owned job post."""
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
    description="**User required.** Submits an application for an active job post. Duplicate applications are rejected.",
)
def apply_to_job(
    job_post_id: int,
    payload: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Apply to a job post as a user."""
    return JobService(db).apply_to_job(current_user, job_post_id, payload)


@router.get(
    "/applications/my",
    response_model=JobApplicationListResponse,
    summary="List my job applications",
    description="**User required.** Lists applications submitted by the authenticated user.",
)
def list_my_applications(
    application_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List the authenticated user's applications."""
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
    description="**User required.** Withdraws an application. Not allowed once accepted or rejected.",
)
def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Withdraw an application as a user."""
    return JobService(db).withdraw_application(current_user, application_id)


# ─── JOB MEDIA ENDPOINTS (Resumes & Documents) ───────────────────────────

from fastapi import File, UploadFile
from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/{job_id}/resumes",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload job application resume",
    description="Uploads an applicant resume (PDF) for a job post.",
)
def upload_job_resume(
    job_id: int,
    file: UploadFile = File(..., description="Resume file (PDF)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload resume document."""
    return MediaService(db).upload_job_resume(current_user, job_id, file)


@router.post(
    "/{job_id}/documents",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload job post document",
    description="Uploads a job description, specification, or legal document for a job post.",
)
def upload_job_document(
    job_id: int,
    file: UploadFile = File(..., description="Job document (PDF or Image)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload job document."""
    return MediaService(db).upload_job_document(current_user, job_id, file)


@router.get(
    "/{job_id}/documents",
    response_model=list[MediaAssetResponse],
    summary="List job documents",
    description="Returns all documents and resumes uploaded for a job post.",
)
def list_job_documents(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List job documents."""
    return MediaService(db).list_job_documents(current_user, job_id)

