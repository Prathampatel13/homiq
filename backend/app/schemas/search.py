from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SortByEnum(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING_DESC = "rating_desc"
    NEAREST = "nearest"
    NEWEST = "newest"
    POPULAR = "popular"
    FASTEST_ARRIVAL = "fastest_arrival"


class ServiceSearchItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    discounted_price: Optional[float] = None
    category_id: int
    category_name: Optional[str] = None
    rating: float = 0.0
    duration_minutes: Optional[int] = 60
    is_active: bool = True

    model_config = {"from_attributes": True}


class TechnicianSearchItem(BaseModel):
    id: int
    user_id: int
    full_name: str
    rating: float = 0.0
    total_reviews: int = 0
    is_online: bool = False
    is_available: bool = True
    is_verified: bool = False
    experience_years: int = 0
    distance_km: Optional[float] = None
    city: Optional[str] = None
    area: Optional[str] = None

    model_config = {"from_attributes": True}


class CategorySearchItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

    model_config = {"from_attributes": True}


class CouponSearchItem(BaseModel):
    id: int
    code: str
    discount_percentage: float
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class BookingSearchItem(BaseModel):
    id: int
    booking_number: str
    status: str
    total_amount: float
    service_id: int
    customer_id: int
    created_at: str

    model_config = {"from_attributes": True}


class CustomerSearchItem(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None

    model_config = {"from_attributes": True}


class GlobalSearchResponse(BaseModel):
    query: str
    total_matches: int
    services: list[ServiceSearchItem] = []
    categories: list[CategorySearchItem] = []
    technicians: list[TechnicianSearchItem] = []
    bookings: list[BookingSearchItem] = []
    coupons: list[CouponSearchItem] = []
    customers: list[CustomerSearchItem] = []

    model_config = {"from_attributes": True}


class AutocompleteSuggestion(BaseModel):
    text: str
    type: str  # "service", "category", "keyword"
    id: Optional[int] = None


class AutocompleteResponse(BaseModel):
    query: str
    suggestions: list[AutocompleteSuggestion] = []
    trending_searches: list[str] = []

    model_config = {"from_attributes": True}


class RecentSearchResponse(BaseModel):
    user_id: int
    recent_queries: list[str] = []

    model_config = {"from_attributes": True}


class RecommendationServicesResponse(BaseModel):
    popular_services: list[ServiceSearchItem] = []
    nearby_services: list[ServiceSearchItem] = []
    frequently_booked: list[ServiceSearchItem] = []
    trending_services: list[ServiceSearchItem] = []
    recently_viewed: list[ServiceSearchItem] = []

    model_config = {"from_attributes": True}


class RecommendationTechniciansResponse(BaseModel):
    recommended_technicians: list[TechnicianSearchItem] = []
    top_rated: list[TechnicianSearchItem] = []
    nearby: list[TechnicianSearchItem] = []

    model_config = {"from_attributes": True}


class UnifiedRecommendationResponse(BaseModel):
    services: RecommendationServicesResponse
    technicians: RecommendationTechniciansResponse

    model_config = {"from_attributes": True}
