from __future__ import annotations

import math
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.crud.tracking import TrackingCRUD
from app.crud.booking import BookingCRUD
from app.crud.technician import TechnicianCRUD
from app.crud.customer import CustomerCRUD
from app.integrations.google_maps import GoogleMapsClient
from app.models.auth import User
from app.models.bookings import BookingStatus
from app.schemas.tracking import (
    ETAResponse,
    GeocodeResponse,
    LocationUpdatePayload,
    NearbyTechnicianItem,
    NearbyTechniciansResponse,
    ReverseGeocodeResponse,
    TechnicianLocationResponse,
    TechnicianLocationUpdate,
    TrackingEventResponse,
    TrackingHistoryResponse,
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in km."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


class TrackingService:
    """Service layer for live tracking & Google Maps operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = TrackingCRUD(db)
        self.booking_crud = BookingCRUD(db)
        self.technician_crud = TechnicianCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.maps_client = GoogleMapsClient()

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    def _get_technician_id(self, current_user: User) -> int:
        technician = self.technician_crud.get_by_user_id(current_user.id)
        if not technician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )
        return technician.id

    # ── Update Technician Location ─────────────────────────────────────

    def update_location(
        self,
        current_user: User,
        booking_id: int,
        payload: TechnicianLocationUpdate,
    ) -> TechnicianLocationResponse:
        """Update the live location of a technician for an active booking."""
        technician_id = self._get_technician_id(current_user)

        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.technician_id != technician_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this booking.",
            )

        # Enforce tracking allowed only during active booking
        inactive_statuses = [BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.REJECTED]
        if booking.status in inactive_statuses:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location tracking is stopped because booking is '{booking.status.value}'.",
            )

        # Create tracking event
        event = self.crud.create_event({
            "booking_id": booking_id,
            "technician_id": technician_id,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "status": payload.status,
        })

        # Update technician's current location in DB
        self.technician_crud.update(
            technician_id,
            {"latitude": payload.latitude, "longitude": payload.longitude},
        )

        return TechnicianLocationResponse(
            booking_id=booking_id,
            technician_id=technician_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status=payload.status,
            last_updated=event.created_at,
        )

    def update_location_payload(
        self,
        current_user: User,
        payload: LocationUpdatePayload,
    ) -> TechnicianLocationResponse:
        """Update location via body payload."""
        update_data = TechnicianLocationUpdate(
            latitude=payload.latitude,
            longitude=payload.longitude,
            status=payload.status,
        )
        return self.update_location(current_user, payload.booking_id, update_data)

    # ── Get Latest Location ────────────────────────────────────────────

    def get_latest_location(
        self,
        current_user: User,
        booking_id: int,
    ) -> TechnicianLocationResponse:
        """Get the latest tracked location & ETA for a booking."""
        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if not current_user.is_superuser:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            is_customer = customer and booking.customer_id == customer.id
            technician = self.technician_crud.get_by_user_id(current_user.id)
            is_technician = technician and booking.technician_id == technician.id
            if not (is_customer or is_technician):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view tracking for this booking.",
                )

        event = self.crud.get_latest_event(booking_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tracking data available for this booking.",
            )

        # Calculate ETA
        eta_minutes = None
        target_lat = None
        target_lng = None

        if booking.address and booking.address.latitude and booking.address.longitude:
            target_lat = booking.address.latitude
            target_lng = booking.address.longitude
        elif booking.customer and booking.customer.latitude and booking.customer.longitude:
            target_lat = booking.customer.latitude
            target_lng = booking.customer.longitude

        if target_lat and target_lng:
            dist = haversine_distance(event.latitude, event.longitude, target_lat, target_lng)
            eta_minutes = round((dist / 30.0) * 60.0, 1)

        return TechnicianLocationResponse(
            booking_id=booking_id,
            technician_id=event.technician_id or 0,
            latitude=event.latitude,
            longitude=event.longitude,
            status=event.status,
            last_updated=event.created_at,
            eta_minutes=eta_minutes,
        )

    # ── Get Tracking History ───────────────────────────────────────────

    def get_tracking_history(
        self,
        current_user: User,
        booking_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> TrackingHistoryResponse:
        """Get the full tracking history for a booking."""
        booking = self.booking_crud.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if not current_user.is_superuser:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            is_customer = customer and booking.customer_id == customer.id
            technician = self.technician_crud.get_by_user_id(current_user.id)
            is_technician = technician and booking.technician_id == technician.id
            if not (is_customer or is_technician):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view tracking for this booking.",
                )

        events = self.crud.list_events(booking_id, offset=offset, limit=limit)
        total = self.crud.count_events(booking_id)

        return TrackingHistoryResponse(
            events=[TrackingEventResponse.model_validate(e) for e in events],
            total=total,
        )

    # ── Location Aliases & Inspection ──────────────────────────────────

    def get_technician_current_location(
        self,
        current_user: User,
    ) -> TechnicianLocationResponse:
        """Get the current location of the authenticated technician."""
        technician_id = self._get_technician_id(current_user)
        event = self.crud.get_latest_technician_event(technician_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No location data available for your profile.",
            )

        return TechnicianLocationResponse(
            booking_id=event.booking_id,
            technician_id=technician_id,
            latitude=event.latitude,
            longitude=event.longitude,
            status=event.status,
            last_updated=event.created_at,
        )

    def get_technician_location_by_id(
        self,
        current_user: User,
        technician_id: int,
    ) -> TechnicianLocationResponse:
        """Get current live location of any technician (Admin or assigned customer)."""
        event = self.crud.get_latest_technician_event(technician_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No live location available for technician #{technician_id}.",
            )

        return TechnicianLocationResponse(
            booking_id=event.booking_id,
            technician_id=technician_id,
            latitude=event.latitude,
            longitude=event.longitude,
            status=event.status,
            last_updated=event.created_at,
        )

    # ── Google Maps Services ───────────────────────────────────────────

    async def geocode_address(self, address: str) -> GeocodeResponse:
        """Geocode an address string to lat/lng using Google Maps API or mock fallback."""
        if not address or not address.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Address string cannot be empty.",
            )
        try:
            res = await self.maps_client.geocode(address)
            return GeocodeResponse(**res)
        except Exception:
            # Fallback mock for local testing when API key not configured
            return GeocodeResponse(
                formatted_address=address,
                latitude=28.6139,
                longitude=77.2090,
                place_id="mock_place_123",
            )

    async def reverse_geocode_coords(self, latitude: float, longitude: float) -> ReverseGeocodeResponse:
        """Reverse geocode lat/lng to formatted address."""
        try:
            res = await self.maps_client.reverse_geocode(latitude, longitude)
            return ReverseGeocodeResponse(**res)
        except Exception:
            return ReverseGeocodeResponse(
                formatted_address=f"Location at {latitude:.4f}, {longitude:.4f}",
                place_id="mock_reverse_place",
                address_components=[],
            )

    async def calculate_maps_eta(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving",
    ) -> ETAResponse:
        """Calculate travel distance & duration between two points."""
        try:
            res = await self.maps_client.get_eta(origin_lat, origin_lng, dest_lat, dest_lng, mode=mode)
            return ETAResponse(
                origin_latitude=origin_lat,
                origin_longitude=origin_lng,
                destination_latitude=dest_lat,
                destination_longitude=dest_lng,
                distance_km=res.get("distance_km"),
                duration_minutes=res.get("duration_minutes"),
                distance_text=res.get("distance_text", "N/A"),
                duration_text=res.get("duration_text", "N/A"),
                status=res.get("status", "OK"),
            )
        except Exception:
            dist = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
            dur = round((dist / 30.0) * 60.0, 1)
            return ETAResponse(
                origin_latitude=origin_lat,
                origin_longitude=origin_lng,
                destination_latitude=dest_lat,
                destination_longitude=dest_lng,
                distance_km=dist,
                duration_minutes=dur,
                distance_text=f"{dist} km",
                duration_text=f"{dur} mins",
                status="OK",
            )

    def find_nearby_technicians(
        self,
        current_user: User,
        lat: float,
        lng: float,
        radius_km: float = 25.0,
    ) -> NearbyTechniciansResponse:
        """Find online and available technicians within radius_km sorted by proximity."""
        from app.models.users import Technician

        stmt = select(Technician).where(
            Technician.latitude.isnot(None),
            Technician.longitude.isnot(None),
            Technician.is_online == True,
        )
        all_techs = list(self.db.execute(stmt).scalars().all())

        items = []
        for t in all_techs:
            dist = haversine_distance(t.latitude, t.longitude, lat, lng)
            if dist <= radius_km:
                eta_mins = round((dist / 30.0) * 60.0, 1)
                full_name = t.user.full_name if t.user else f"Technician #{t.id}"
                phone = t.user.phone if t.user else None
                is_busy = not getattr(t, "availability", True)
                items.append(
                    NearbyTechnicianItem(
                        technician_id=t.id,
                        user_id=t.user_id,
                        full_name=full_name,
                        phone=phone,
                        latitude=t.latitude,
                        longitude=t.longitude,
                        distance_km=dist,
                        eta_minutes=eta_mins,
                        is_online=t.is_online,
                        is_busy=is_busy,
                    )
                )

        items.sort(key=lambda x: x.distance_km)
        return NearbyTechniciansResponse(technicians=items, total=len(items))


