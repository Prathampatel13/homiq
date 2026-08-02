"""
Google Maps integration for geolocation services.

Provides:
- Geocoding (address -> lat/lng)
- Reverse geocoding (lat/lng -> address)
- Distance Matrix API (distance & ETA between points)
- Directions (route/polyline for live tracking)
"""

from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class GoogleMapsClient:
    """Client wrapper for Google Maps Platform APIs."""

    _instance: Optional["GoogleMapsClient"] = None
    BASE_URL = "https://maps.googleapis.com/maps/api"

    def __new__(cls) -> "GoogleMapsClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    def _validate_api_key(self) -> None:
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Maps API key is not configured.",
            )

    async def geocode(self, address: str) -> dict[str, Any]:
        """
        Convert an address to geographic coordinates.

        Args:
            address: Full address string.

        Returns:
            dict: Geocoding result with formatted_address, lat, lng, etc.
        """
        self._validate_api_key()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/geocode/json",
                params={"address": address, "key": self.api_key},
            )
            data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geocoding failed for address: {address}",
            )

        result = data["results"][0]
        location = result["geometry"]["location"]
        return {
            "formatted_address": result.get("formatted_address", ""),
            "latitude": location["lat"],
            "longitude": location["lng"],
            "place_id": result.get("place_id", ""),
        }

    async def reverse_geocode(self, latitude: float, longitude: float) -> dict[str, Any]:
        """
        Convert coordinates to a human-readable address.

        Args:
            latitude: Latitude value.
            longitude: Longitude value.

        Returns:
            dict: Address components and formatted address.
        """
        self._validate_api_key()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/geocode/json",
                params={
                    "latlng": f"{latitude},{longitude}",
                    "key": self.api_key,
                },
            )
            data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reverse geocoding failed.",
            )

        result = data["results"][0]
        return {
            "formatted_address": result.get("formatted_address", ""),
            "place_id": result.get("place_id", ""),
            "address_components": result.get("address_components", []),
        }

    async def get_distance_matrix(
        self,
        origins: list[str],
        destinations: list[str],
        mode: str = "driving",
    ) -> dict[str, Any]:
        """
        Calculate distance and travel time between origins and destinations.

        Args:
            origins: List of origin addresses or "lat,lng" strings.
            destinations: List of destination addresses or "lat,lng" strings.
            mode: Travel mode (driving, walking, bicycling, transit).

        Returns:
            dict: Distance matrix with distance and duration for each pair.
        """
        self._validate_api_key()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/distancematrix/json",
                params={
                    "origins": "|".join(origins),
                    "destinations": "|".join(destinations),
                    "mode": mode,
                    "key": self.api_key,
                },
            )
            data = response.json()

        if data.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Distance Matrix API request failed.",
            )

        return data

    async def get_eta(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving",
    ) -> dict[str, Any]:
        """
        Get ETA and distance between two points.

        Args:
            origin_lat: Origin latitude.
            origin_lng: Origin longitude.
            dest_lat: Destination latitude.
            dest_lng: Destination longitude.
            mode: Travel mode (default: driving).

        Returns:
            dict: Distance (km) and duration (minutes) with formatted strings.
        """
        origin = f"{origin_lat},{origin_lng}"
        dest = f"{dest_lat},{dest_lng}"

        data = await self.get_distance_matrix(
            origins=[origin],
            destinations=[dest],
            mode=mode,
        )

        try:
            element = data["rows"][0]["elements"][0]
            if element["status"] != "OK":
                return {
                    "distance_km": None,
                    "duration_minutes": None,
                    "distance_text": "N/A",
                    "duration_text": "N/A",
                    "status": element["status"],
                }

            return {
                "distance_km": element["distance"]["value"] / 1000.0,
                "duration_minutes": element["duration"]["value"] / 60.0,
                "distance_text": element["distance"]["text"],
                "duration_text": element["duration"]["text"],
                "status": "OK",
            }
        except (IndexError, KeyError):
            return {
                "distance_km": None,
                "duration_minutes": None,
                "distance_text": "N/A",
                "duration_text": "N/A",
                "status": "ERROR",
            }

    async def get_directions(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: Optional[list[dict[str, float]]] = None,
        mode: str = "driving",
    ) -> dict[str, Any]:
        """
        Get turn-by-turn directions with polyline for live tracking.

        Args:
            origin_lat: Origin latitude.
            origin_lng: Origin longitude.
            dest_lat: Destination latitude.
            dest_lng: Destination longitude.
            waypoints: Optional intermediate waypoints [{"lat": ..., "lng": ...}].
            mode: Travel mode (default: driving).

        Returns:
            dict: Directions with polyline, steps, distance, duration.
        """
        self._validate_api_key()
        params: dict[str, Any] = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": mode,
            "key": self.api_key,
        }

        if waypoints:
            waypoint_str = "|".join(
                f"{w['lat']},{w['lng']}" for w in waypoints
            )
            params["waypoints"] = waypoint_str

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/directions/json",
                params=params,
            )
            data = response.json()

        if data.get("status") != "OK" or not data.get("routes"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Directions request failed.",
            )

        route = data["routes"][0]
        leg = route["legs"][0]

        return {
            "polyline": route["overview_polyline"]["points"],
            "distance_km": leg["distance"]["value"] / 1000.0,
            "duration_minutes": leg["duration"]["value"] / 60.0,
            "distance_text": leg["distance"]["text"],
            "duration_text": leg["duration"]["text"],
            "start_address": leg.get("start_address", ""),
            "end_address": leg.get("end_address", ""),
            "steps": [
                {
                    "instruction": step["html_instructions"],
                    "distance": step["distance"]["text"],
                    "duration": step["duration"]["text"],
                    "start_location": step["start_location"],
                    "end_location": step["end_location"],
                }
                for step in leg.get("steps", [])
            ],
        }

    async def autocomplete(self, input: str, session_token: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get place predictions for an autocomplete input.

        Args:
            input: Partial address/place input.
            session_token: Optional session token for billing.

        Returns:
            list[dict]: List of place predictions.
        """
        self._validate_api_key()
        params: dict[str, Any] = {
            "input": input,
            "key": self.api_key,
        }
        if session_token:
            params["sessiontoken"] = session_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/place/autocomplete/json",
                params=params,
            )
            data = response.json()

        if data.get("status") != "OK":
            return []

        return [
            {
                "place_id": p["place_id"],
                "description": p["description"],
                "structured_formatting": p.get("structured_formatting", {}),
            }
            for p in data.get("predictions", [])
        ]

