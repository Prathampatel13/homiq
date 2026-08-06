"""
Pydantic schemas for the Jobs module (job posts + applications).

Follows the same pattern as ``schemas/company.py`` and ``schemas/technician.py``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Job Posts
# ─────────────────────────────────────────────


class JobPostCompany(BaseModel):
    """Embedded company info returned in job post responses."""

    id: int
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None


class JobPostCreate(BaseModel):
    """Payload for creating a new job post."""

    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    requirements: Optional[str] = Field(None, max_length=5000)
    is_active: bool = Field(True)


class JobPostUpdate(BaseModel):
    """Payload for updating a job post (partial)."""

    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    requirements: Optional[str] = Field(None, max_length=5000)
    is_active: Optional[bool] = None


class JobPostResponse(BaseModel):
    """Full job post response."""

    id: int
    company_id: int
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    is_active: bool
    application_count: int = 0
    created_at: datetime
    company: Optional[JobPostCompany] = Field(None, alias="company_profile")

    model_config = {"from_attributes": True, "populate_by_name": True}


class JobPostListResponse(BaseModel):
    """Paginated list of job posts."""

    items: list[JobPostResponse]
    total: int


# ─────────────────────────────────────────────
# Job Applications
# ─────────────────────────────────────────────


class JobApplicationTechnician(BaseModel):
    """Embedded technician info returned in application responses."""

    id: int
    full_name: str
    specialization: Optional[str] = None
    experience_years: int = 0
    rating: float = 0.0


class JobApplicationJobPost(BaseModel):
    """Embedded job post info returned in application responses."""

    id: int
    title: str
    company_name: str = ""
    is_active: bool


class JobApplicationCreate(BaseModel):
    """Payload for applying to a job."""

    cover_letter: Optional[str] = Field(None, max_length=5000)


class JobApplicationStatusUpdate(BaseModel):
    """Payload for updating application status (company)."""

    status: str = Field(..., pattern=r"^(applied|shortlisted|accepted|rejected)$")


class JobApplicationResponse(BaseModel):
    """Full job application response."""

    id: int
    job_post_id: int
    technician_id: int
    cover_letter: Optional[str] = None
    status: str
    created_at: datetime
    job_post: Optional[JobApplicationJobPost] = None
    technician: Optional[JobApplicationTechnician] = Field(
        None, alias="technician_profile"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class JobApplicationListResponse(BaseModel):
    """Paginated list of job applications."""

    items: list[JobApplicationResponse]
    total: int

