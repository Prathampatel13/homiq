from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.addresses import CustomerAddress
    from app.models.bookings import Booking
    from app.models.jobs import JobApplication, JobPost
    from app.models.payments import Payment
    from app.models.invoices import Invoice

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    profile_image: Mapped[object] = mapped_column(String(500), nullable=True)
    phone: Mapped[object] = mapped_column(String(20), nullable=True)
    address: Mapped[object] = mapped_column(Text, nullable=True)
    city: Mapped[object] = mapped_column(String(100), nullable=True)
    state: Mapped[object] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[object] = mapped_column(String(20), nullable=True)
    latitude: Mapped[object] = mapped_column(Float, nullable=True)
    longitude: Mapped[object] = mapped_column(Float, nullable=True)
    preferred_language: Mapped[object] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        back_populates="customer",
    )

    addresses: Mapped[list["CustomerAddress"]] = relationship(
        "CustomerAddress",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    specialization: Mapped[object] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skills: Mapped[object] = mapped_column(JSON, nullable=True)
    languages: Mapped[object] = mapped_column(JSON, nullable=True)
    working_hours: Mapped[object] = mapped_column(String(255), nullable=True)
    availability: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latitude: Mapped[object] = mapped_column(Float, nullable=True)
    longitude: Mapped[object] = mapped_column(Float, nullable=True)
    service_radius_km: Mapped[object] = mapped_column(Float, nullable=True)
    profile_image: Mapped[object] = mapped_column(String(500), nullable=True)
    government_id_image: Mapped[object] = mapped_column(String(500), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="technician")

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="technician",
    )

    job_applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="technician_profile",
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[object] = mapped_column(String(255), nullable=True)
    description: Mapped[object] = mapped_column(Text, nullable=True)
    website: Mapped[object] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="company")

    job_posts: Mapped[list["JobPost"]] = relationship(
        "JobPost",
        back_populates="company_profile",
        cascade="all, delete-orphan",
    )


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    department: Mapped[object] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="admin")
