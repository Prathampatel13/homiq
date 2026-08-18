from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.search import SearchCRUD
from app.models.auth import User
from app.models.bookings import Booking
from app.schemas.search import (
    AutocompleteResponse,
    AutocompleteSuggestion,
    BookingSearchItem,
    GlobalSearchResponse,
    RecentSearchResponse,
    RecommendationServicesResponse,
    RecommendationTechniciansResponse,
    ServiceSearchItem,
    TechnicianSearchItem,
    UnifiedRecommendationResponse,
)

# Global in-memory recent search store (Redis fallback)
RECENT_SEARCH_STORE: dict[int, list[str]] = {}


class SearchService:
    """Service layer for Search, Autocomplete & Recommendations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = SearchCRUD(db)

    def global_search(self, query: str, offset: int = 0, limit: int = 10, user_id: Optional[int] = None) -> GlobalSearchResponse:
        """Global search across platform entities."""
        if user_id and query.strip():
            self.record_recent_search(user_id, query.strip())
        return self.crud.global_search(query=query, offset=offset, limit=limit)

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
        user_id: Optional[int] = None,
    ) -> list[ServiceSearchItem]:
        """Search services with filtering & sorting."""
        if user_id and query and query.strip():
            self.record_recent_search(user_id, query.strip())

        return self.crud.search_services(
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            sort_by=sort_by,
            offset=offset,
            limit=limit,
        )

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
        """Search technicians with location/availability filters."""
        return self.crud.search_technicians(
            query=query,
            city=city,
            area=area,
            is_verified=is_verified,
            is_online=is_online,
            min_rating=min_rating,
            lat=lat,
            lng=lng,
            max_distance_km=max_distance_km,
            sort_by=sort_by,
            offset=offset,
            limit=limit,
        )

    def search_bookings(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        current_user: Optional[User] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[BookingSearchItem]:
        """Search bookings for admin/customer/technician."""
        stmt = select(Booking)
        if current_user and not current_user.is_superuser:
            # Scope to customer if customer
            from app.crud.customer import CustomerCRUD
            cust = CustomerCRUD(self.db).get_by_user_id(current_user.id)
            if cust:
                stmt = stmt.where(Booking.customer_id == cust.id)

        if status:
            stmt = stmt.where(Booking.status == status)

        stmt = stmt.offset(offset).limit(limit)
        bookings = self.db.scalars(stmt).all()

        return [
            BookingSearchItem(
                id=b.id,
                booking_number=b.booking_number,
                status=b.status.value if hasattr(b.status, 'value') else str(b.status),
                total_amount=float(getattr(b, "final_price", None) or getattr(b, "estimated_price", None) or 0.0),
                service_id=b.service_id,
                customer_id=b.customer_id,
                created_at=b.created_at.isoformat() if b.created_at else "",
            )
            for b in bookings
        ]

    def get_suggestions(self, query: str, limit: int = 5) -> AutocompleteResponse:
        """Get live autocomplete suggestions and trending search keywords."""
        sug_items = self.crud.get_suggestions(query=query, limit=limit)
        suggestions = [
            AutocompleteSuggestion(
                text=item["text"],
                type=item["type"],
                id=item["id"],
            )
            for item in sug_items
        ]
        trending = ["AC Repair", "Home Cleaning", "Plumbing", "Deep Clean", "Electrical Inspection"]

        return AutocompleteResponse(
            query=query,
            suggestions=suggestions,
            trending_searches=trending,
        )

    def record_recent_search(self, user_id: int, query: str):
        """Record user's recent search string."""
        if user_id not in RECENT_SEARCH_STORE:
            RECENT_SEARCH_STORE[user_id] = []
        lst = RECENT_SEARCH_STORE[user_id]
        if query in lst:
            lst.remove(query)
        lst.insert(0, query)
        RECENT_SEARCH_STORE[user_id] = lst[:10]

    def get_recent_searches(self, user_id: int) -> RecentSearchResponse:
        """Retrieve recent searches for authenticated user."""
        queries = RECENT_SEARCH_STORE.get(user_id, ["AC Repair", "Plumbing"])
        return RecentSearchResponse(user_id=user_id, recent_queries=queries)

    def get_recommendations_services(self, user_id: Optional[int] = None) -> RecommendationServicesResponse:
        """Get recommended services (Popular, Nearby, Frequently Booked, Trending, Recently Viewed)."""
        services = self.crud.search_services(limit=5)
        return RecommendationServicesResponse(
            popular_services=services,
            nearby_services=services,
            frequently_booked=services,
            trending_services=services,
            recently_viewed=services[:2],
        )

    def get_recommendations_technicians(self, user_id: Optional[int] = None) -> RecommendationTechniciansResponse:
        """Get recommended technicians (Top Rated, Nearby, Fast Response)."""
        techs = self.crud.search_technicians(limit=5)
        return RecommendationTechniciansResponse(
            recommended_technicians=techs,
            top_rated=techs,
            nearby=techs,
        )

    def get_unified_recommendations(self, user_id: Optional[int] = None) -> UnifiedRecommendationResponse:
        """Get complete recommendations for dashboard."""
        return UnifiedRecommendationResponse(
            services=self.get_recommendations_services(user_id),
            technicians=self.get_recommendations_technicians(user_id),
        )
