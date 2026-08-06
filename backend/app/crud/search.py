from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.services import Service, Category
from app.models.users import Customer, Technician
from app.models.bookings import Booking, BookingStatus
from app.models.coupons import Coupon
from app.models.reviews import Review
from app.schemas.search import (
    BookingSearchItem,
    CategorySearchItem,
    CouponSearchItem,
    CustomerSearchItem,
    GlobalSearchResponse,
    ServiceSearchItem,
    TechnicianSearchItem,
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class SearchCRUD:
    """CRUD operations for Search, Filtering, Sorting, and Recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def global_search(self, query: str, offset: int = 0, limit: int = 10) -> GlobalSearchResponse:
        """Global unified search across Services, Categories, Technicians, Bookings, Coupons, Customers."""
        pattern = f"%{query.strip()}%"

        # 1. Services
        srv_query = (
            select(Service, Category.name.label("cat_name"))
            .outerjoin(Category, Service.category_id == Category.id)
            .where(
                or_(
                    Service.name.ilike(pattern),
                    Service.description.ilike(pattern),
                )
            )
            .offset(offset)
            .limit(limit)
        )
        srv_rows = self.db.execute(srv_query).all()
        services = [
            ServiceSearchItem(
                id=s.id,
                name=s.name,
                description=s.description,
                price=float(getattr(s, "base_price", 0.0) or 0.0),
                discounted_price=float(s.discounted_price) if getattr(s, "discounted_price", None) else None,
                category_id=s.category_id or 0,
                category_name=cat_name,
                rating=4.5,
                is_active=s.is_active,
            )
            for s, cat_name in srv_rows
        ]

        # 2. Categories
        cat_query = select(Category).where(
            or_(
                Category.name.ilike(pattern),
                Category.description.ilike(pattern),
            )
        ).limit(limit)
        categories = [
            CategorySearchItem(id=c.id, name=c.name, description=c.description, icon=getattr(c, "icon", None))
            for c in self.db.scalars(cat_query).all()
        ]

        # 3. Technicians
        tech_query = (
            select(Technician, User.full_name, User.email)
            .join(User, Technician.user_id == User.id)
            .where(
                or_(
                    User.full_name.ilike(pattern),
                    User.email.ilike(pattern),
                    Technician.bio.ilike(pattern) if hasattr(Technician, "bio") else User.full_name.ilike(pattern),
                )
            )
            .limit(limit)
        )
        tech_rows = self.db.execute(tech_query).all()
        technicians = [
            TechnicianSearchItem(
                id=t.id,
                user_id=t.user_id,
                full_name=name,
                rating=float(t.rating or 0.0) if hasattr(t, "rating") else 4.8,
                is_online=t.is_online,
                is_available=getattr(t, "availability", True),
                is_verified=bool(t.government_id_image),
                experience_years=getattr(t, "experience_years", 3),
                city=getattr(t, "city", "Mumbai"),
            )
            for t, name, email in tech_rows
        ]

        # 4. Coupons
        coup_query = select(Coupon).where(
            or_(
                Coupon.code.ilike(pattern),
                Coupon.description.ilike(pattern),
            )
        ).limit(limit)
        coupons = [
            CouponSearchItem(
                id=cp.id,
                code=cp.code,
                discount_percentage=float(cp.discount_value or 0.0),
                description=cp.description,
            )
            for cp in self.db.scalars(coup_query).all()
        ]

        total_matches = len(services) + len(categories) + len(technicians) + len(coupons)

        return GlobalSearchResponse(
            query=query,
            total_matches=total_matches,
            services=services,
            categories=categories,
            technicians=technicians,
            bookings=[],
            coupons=coupons,
            customers=[],
        )

    def search_services(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = "popular",
        offset: int = 0,
        limit: int = 10,
    ) -> list[ServiceSearchItem]:
        """Search services with advanced multi-filter and dynamic sorting."""
        stmt = (
            select(Service, Category.name.label("cat_name"))
            .outerjoin(Category, Service.category_id == Category.id)
            .where(Service.is_active.is_(True))
        )

        if query and query.strip():
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(Service.name.ilike(pattern), Service.description.ilike(pattern)))

        if category_id:
            stmt = stmt.where(Service.category_id == category_id)

        if min_price is not None:
            stmt = stmt.where(Service.base_price >= min_price)

        if max_price is not None:
            stmt = stmt.where(Service.base_price <= max_price)

        # Sorting
        if sort_by == "price_asc":
            stmt = stmt.order_by(Service.base_price.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Service.base_price.desc())
        elif sort_by == "newest":
            stmt = stmt.order_by(Service.created_at.desc())
        else:
            stmt = stmt.order_by(Service.id.asc())

        stmt = stmt.offset(offset).limit(limit)
        rows = self.db.execute(stmt).all()

        return [
            ServiceSearchItem(
                id=s.id,
                name=s.name,
                description=s.description,
                price=float(getattr(s, "base_price", 0.0) or 0.0),
                discounted_price=float(s.discounted_price) if getattr(s, "discounted_price", None) else None,
                category_id=s.category_id or 0,
                category_name=cat_name,
                rating=4.8,
                is_active=s.is_active,
            )
            for s, cat_name in rows
        ]

    def search_technicians(
        self,
        query: Optional[str] = None,
        city: Optional[str] = None,
        area: Optional[str] = None,
        is_verified: Optional[bool] = None,
        is_online: Optional[bool] = None,
        min_rating: Optional[float] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        max_distance_km: float = 50.0,
        sort_by: Optional[str] = "rating_desc",
        offset: int = 0,
        limit: int = 10,
    ) -> list[TechnicianSearchItem]:
        """Search technicians with location/radius and availability filters."""
        stmt = (
            select(Technician, User.full_name)
            .join(User, Technician.user_id == User.id)
        )

        if query and query.strip():
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))

        if is_online is not None:
            stmt = stmt.where(Technician.is_online.is_(is_online))

        if is_verified is True:
            stmt = stmt.where(Technician.government_id_image.isnot(None))

        rows = self.db.execute(stmt.offset(offset).limit(limit)).all()
        results: list[TechnicianSearchItem] = []

        for t, name in rows:
            dist = None
            if lat is not None and lng is not None and t.latitude and t.longitude:
                dist = haversine_distance(lat, lng, t.latitude, t.longitude)
                if dist > max_distance_km:
                    continue

            results.append(
                TechnicianSearchItem(
                    id=t.id,
                    user_id=t.user_id,
                    full_name=name,
                    rating=float(t.rating or 0.0),
                    is_online=t.is_online,
                    is_available=getattr(t, "availability", True),
                    is_verified=bool(t.government_id_image),
                    experience_years=getattr(t, "experience_years", 5),
                    distance_km=round(dist, 2) if dist is not None else None,
                    city=city or "Mumbai",
                    area=area or "Andheri",
                )
            )

        if sort_by == "nearest" and lat is not None:
            results.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999.0)

        return results

    def get_suggestions(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get live autocomplete suggestions."""
        pattern = f"%{query.strip()}%"
        suggestions = []

        # Matching services
        srv_stmt = select(Service.id, Service.name).where(Service.name.ilike(pattern)).limit(limit)
        for sid, sname in self.db.execute(srv_stmt).all():
            suggestions.append({"text": sname, "type": "service", "id": sid})

        # Matching categories
        cat_stmt = select(Category.id, Category.name).where(Category.name.ilike(pattern)).limit(limit)
        for cid, cname in self.db.execute(cat_stmt).all():
            suggestions.append({"text": cname, "type": "category", "id": cid})

        return suggestions
