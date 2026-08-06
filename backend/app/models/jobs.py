from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.users import Company, Technician


class JobPost(Base):
    __tablename__ = "job_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    company_profile: Mapped["Company"] = relationship(
        "Company",
        back_populates="job_posts",
    )

    job_applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="job_post",
        cascade="all, delete-orphan",
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_post_id: Mapped[int] = mapped_column(ForeignKey("job_posts.id"), nullable=False)
    technician_id: Mapped[int] = mapped_column(ForeignKey("technicians.id"), nullable=False)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="applied", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    job_post: Mapped["JobPost"] = relationship(
        "JobPost",
        back_populates="job_applications",
    )

    technician_profile: Mapped["Technician"] = relationship(
        "Technician",
        back_populates="job_applications",
    )
