"""
Search, Autocomplete & Recommendation Engine API Endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user, get_current_user_optional
from app.schemas.search import (
    AutocompleteResponse,
    BookingSearchItem,
    GlobalSearchResponse,
    RecentSearchResponse,
    RecommendationServicesResponse,
    RecommendationTechniciansResponse,
    ServiceSearchItem,
    TechnicianSearchItem,
    UnifiedRecommendationResponse,
)
from app.services.search import SearchService

router = APIRouter(tags=["Search & Recommendations"])


@router.get(
    "/search",
    response_model=GlobalSearchResponse,
    summary="Global Unified Search",
    description="Searches across Services, Categories, Technicians, Bookings, Coupons, and Customers in a single request.",
)
def global_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Any:
    """Global search across platform."""
    user_id = current_user.id if current_user else None
    return SearchService(db).global_search(query=q, offset=offset, limit=limit, user_id=user_id)


@router.get(
    "/search/services",
    response_model=list[ServiceSearchItem],
    summary="Search Services",
    description="Filtered and sorted service search (category, price range, min rating, sorting).",
)
def search_services(
    q: Optional[str] = Query(None, description="Keyword search query"),
    category_id: Optional[int] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5.0),
    sort_by: Optional[str] = Query("popular", description="Sort by: price_asc, price_desc, rating_desc, newest, popular"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Any:
    """Search services with filters and sorting."""
    user_id = current_user.id if current_user else None
    return SearchService(db).search_services(
        query=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        offset=offset,
        limit=limit,
        user_id=user_id,
    )


@router.get(
    "/search/technicians",
    response_model=list[TechnicianSearchItem],
    summary="Search Technicians",
    description="Filtered technician search (city, area, online status, verified status, Haversine GPS radius).",
)
def search_technicians(
    q: Optional[str] = Query(None, description="Technician name search"),
    city: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    is_verified: Optional[bool] = Query(None),
    is_online: Optional[bool] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5.0),
    lat: Optional[float] = Query(None, description="Latitude for distance calculation"),
    lng: Optional[float] = Query(None, description="Longitude for distance calculation"),
    max_distance_km: float = Query(50.0, ge=1.0, le=500.0),
    sort_by: Optional[str] = Query("rating_desc", description="Sort by: rating_desc, nearest, experience_desc"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> Any:
    """Search technicians with location/availability filters."""
    return SearchService(db).search_technicians(
        query=q,
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


@router.get(
    "/search/bookings",
    response_model=list[BookingSearchItem],
    summary="Search Bookings",
    description="Search user or platform bookings by status or query string.",
)
def search_bookings(
    q: Optional[str] = Query(None, description="Booking reference search"),
    status: Optional[str] = Query(None, description="Booking status filter"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Search bookings."""
    return SearchService(db).search_bookings(
        query=q,
        status=status,
        current_user=current_user,
        offset=offset,
        limit=limit,
    )


# ─── AUTOCOMPLETE & SUGGESTIONS ─────────────────────────────────────────────


@router.get(
    "/search/suggestions",
    response_model=AutocompleteResponse,
    summary="Live Search Autocomplete",
    description="Returns live matching service & category suggestions along with trending search terms.",
)
def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Live prefix/query text"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> Any:
    """Get live search suggestions."""
    return SearchService(db).get_suggestions(query=q, limit=limit)


@router.get(
    "/search/recent",
    response_model=RecentSearchResponse,
    summary="Get Recent Searches",
    description="Returns recent search history for the authenticated user.",
)
def get_recent_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get authenticated user's recent searches."""
    return SearchService(db).get_recent_searches(user_id=current_user.id)


# ─── RECOMMENDATION ENGINE ──────────────────────────────────────────────────


@router.get(
    "/recommendations",
    response_model=UnifiedRecommendationResponse,
    summary="Get Unified Recommendations",
    description="Returns complete recommendation suite for dashboard (Popular, Nearby, Trending, Top Technicians).",
)
def get_unified_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Any:
    """Get unified recommendations."""
    user_id = current_user.id if current_user else None
    return SearchService(db).get_unified_recommendations(user_id=user_id)


@router.get(
    "/recommendations/services",
    response_model=RecommendationServicesResponse,
    summary="Get Service Recommendations",
    description="Returns popular, nearby, trending, and frequently booked services.",
)
def get_service_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Any:
    """Get service recommendations."""
    user_id = current_user.id if current_user else None
    return SearchService(db).get_recommendations_services(user_id=user_id)


@router.get(
    "/recommendations/technicians",
    response_model=RecommendationTechniciansResponse,
    summary="Get Technician Recommendations",
    description="Returns top rated, recommended, and nearby technicians.",
)
def get_technician_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Any:
    """Get technician recommendations."""
    user_id = current_user.id if current_user else None
    return SearchService(db).get_recommendations_technicians(user_id=user_id)
