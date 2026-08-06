from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.tracking import (
    ETAResponse,
    GeocodeResponse,
    LocationUpdatePayload,
    NearbyTechniciansResponse,
    ReverseGeocodeResponse,
    TechnicianLocationResponse,
    TechnicianLocationUpdate,
    TrackingHistoryResponse,
)
from app.services.tracking import TrackingService

router = APIRouter(tags=["Location & Maps System"])


# ─── LOCATION SYSTEM ENDPOINTS ──────────────────────────────────────────


@router.post(
    "/location/update",
    response_model=TechnicianLocationResponse,
    summary="Update live location",
    description="**Technician only.** Updates live GPS coordinates for an active booking.",
)
def update_location_post(
    payload: LocationUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update live location via body payload."""
    return TrackingService(db).update_location_payload(current_user, payload)


@router.get(
    "/location/current",
    response_model=TechnicianLocationResponse,
    summary="Get current location",
    description="Returns current tracked location of authenticated user or technician.",
)
def get_current_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get current location of the authenticated user/technician."""
    return TrackingService(db).get_technician_current_location(current_user)


@router.get(
    "/location/technician/{technician_id}",
    response_model=TechnicianLocationResponse,
    summary="Get technician location by ID",
    description="Returns live tracked location of a specific technician.",
)
def get_technician_location_by_id(
    technician_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get live location for a technician by ID."""
    return TrackingService(db).get_technician_location_by_id(current_user, technician_id)


@router.get(
    "/location/booking/{booking_id}",
    response_model=TechnicianLocationResponse,
    summary="Get booking technician location & ETA",
    description="Returns live technician location and driving ETA for a booking.",
)
def get_booking_location(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get latest location & ETA for a booking."""
    return TrackingService(db).get_latest_location(current_user, booking_id)


# ─── GOOGLE MAPS PLATFORM ENDPOINTS ─────────────────────────────────────


@router.get(
    "/maps/geocode",
    response_model=GeocodeResponse,
    summary="Geocode address",
    description="Converts a human-readable address into latitude & longitude coordinates using Google Maps.",
)
async def geocode_address(
    address: str = Query(..., min_length=1, description="Address string to geocode"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Geocode address string to coordinates."""
    return await TrackingService(db).geocode_address(address)


@router.get(
    "/maps/reverse-geocode",
    response_model=ReverseGeocodeResponse,
    summary="Reverse geocode coordinates",
    description="Converts latitude & longitude coordinates into a human-readable address.",
)
async def reverse_geocode(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Reverse geocode coordinates to formatted address."""
    return await TrackingService(db).reverse_geocode_coords(latitude, longitude)


@router.get(
    "/maps/eta",
    response_model=ETAResponse,
    summary="Calculate distance & ETA",
    description="Calculates travel distance (km) and driving duration (minutes) between origin and destination.",
)
async def get_maps_eta(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lng: float = Query(..., ge=-180, le=180),
    dest_lat: float = Query(..., ge=-90, le=90),
    dest_lng: float = Query(..., ge=-180, le=180),
    mode: str = Query("driving", description="Travel mode (driving, walking, bicycling)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Calculate distance & ETA via Google Maps Distance Matrix."""
    return await TrackingService(db).calculate_maps_eta(origin_lat, origin_lng, dest_lat, dest_lng, mode=mode)


@router.get(
    "/maps/nearby-technicians",
    response_model=NearbyTechniciansResponse,
    summary="Search nearby technicians",
    description="Returns online and available technicians within radius_km, sorted by distance & ETA.",
)
def find_nearby_technicians(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(25.0, gt=0, le=500.0, description="Search radius in kilometers"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Find nearby available technicians sorted by distance."""
    return TrackingService(db).find_nearby_technicians(current_user, latitude, longitude, radius_km=radius_km)


# ─── BACKWARD COMPATIBILITY TRACKING ENDPOINTS ──────────────────────────


@router.put(
    "/tracking/{booking_id}/location",
    response_model=TechnicianLocationResponse,
    summary="Update technician location (legacy)",
    description="**Technician only.** Updates live location for a booking.",
)
def update_location(
    booking_id: int,
    payload: TechnicianLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update live location for a booking."""
    return TrackingService(db).update_location(current_user, booking_id, payload)


@router.get(
    "/tracking/{booking_id}/location",
    response_model=TechnicianLocationResponse,
    summary="Get technician location (legacy)",
    description="Returns latest location & ETA for a booking.",
)
def get_latest_location(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get latest location for a booking."""
    return TrackingService(db).get_latest_location(current_user, booking_id)


@router.get(
    "/tracking/{booking_id}/history",
    response_model=TrackingHistoryResponse,
    summary="Get tracking history (legacy)",
    description="Returns full tracking history for a booking.",
)
def get_tracking_history(
    booking_id: int,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get tracking history for a booking."""
    return TrackingService(db).get_tracking_history(
        current_user, booking_id, offset=offset, limit=limit
    )


@router.get(
    "/tracking/me/location",
    response_model=TechnicianLocationResponse,
    summary="Get my current location (legacy)",
    description="Returns current location of authenticated technician.",
)
def get_my_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get current location of authenticated technician."""
    return TrackingService(db).get_technician_current_location(current_user)


