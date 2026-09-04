from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.websockets import manager
from app.models.bookings import Booking
from app.schemas.websocket import (
    ChatMessagePayload,
    LocationPayload,
    StatusUpdatePayload,
    SystemAlertPayload,
    TypingPayload,
    WSEventTypeEnum,
    WSMessage,
)

# In-memory Chat History Store
CHAT_HISTORY_STORE: dict[int, list[dict[str, Any]]] = {}


class WebSocketService:
    """Service layer for Real-Time WebSocket events and chat persistence."""

    def __init__(self, db: Session):
        self.db = db

    async def publish_booking_status_update(
        self,
        booking_id: int,
        old_status: str,
        new_status: str,
        message: Optional[str] = None,
    ):
        """Broadcast booking status change to Customer, Technician, and Admin."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            return

        payload = StatusUpdatePayload(
            booking_id=booking.id,
            booking_number=booking.booking_number,
            old_status=old_status,
            new_status=new_status,
            message=message or f"Booking #{booking.booking_number} updated to {new_status}.",
        )

        msg = WSMessage(
            event_type=WSEventTypeEnum.STATUS_UPDATE,
            payload=payload.model_dump(),
        )

        data = msg.model_dump()

        # Broadcast to Customer
        if booking.customer_id:
            await manager.broadcast_to_customer(booking.customer_id, data)

        # Broadcast to Assigned Technician
        if booking.technician_id:
            await manager.broadcast_to_technician(booking.technician_id, data)

        # If unassigned or status affects dispatch availability, notify ALL technicians
        if not booking.technician_id or new_status in ["pending", "accepted", "cancelled", "rejected"]:
            await manager.broadcast_to_all_technicians(data)

        # Broadcast to Admin
        await manager.broadcast_to_admin(data)

        # Broadcast to Location & Chat rooms
        await manager.broadcast_to_room(f"location_{booking_id}", data)
        await manager.broadcast_to_room(f"chat_{booking_id}", data)

    def broadcast_booking_update(
        self,
        booking_id: int,
        old_status: str,
        new_status: str,
        message: Optional[str] = None,
    ):
        """Synchronous thread-safe trigger for booking status broadcast."""
        manager.broadcast_sync(
            self.publish_booking_status_update(
                booking_id=booking_id,
                old_status=old_status,
                new_status=new_status,
                message=message,
            )
        )

    async def publish_chat_message(
        self,
        booking_id: int,
        sender_id: int,
        sender_role: str,
        content: str,
    ) -> ChatMessagePayload:
        """Persist & broadcast chat message to booking chat room."""
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        payload = ChatMessagePayload(
            message_id=message_id,
            booking_id=booking_id,
            sender_id=sender_id,
            sender_role=sender_role,
            content=content,
            status="delivered",
        )

        # Persist in Chat History Store
        if booking_id not in CHAT_HISTORY_STORE:
            CHAT_HISTORY_STORE[booking_id] = []
        CHAT_HISTORY_STORE[booking_id].append(payload.model_dump())

        msg = WSMessage(
            event_type=WSEventTypeEnum.CHAT_MESSAGE,
            payload=payload.model_dump(),
        )

        await manager.broadcast_to_room(f"chat_{booking_id}", msg.model_dump())
        return payload

    async def publish_typing_indicator(self, booking_id: int, sender_id: int, is_typing: bool):
        """Broadcast typing indicator to chat room."""
        payload = TypingPayload(
            booking_id=booking_id,
            sender_id=sender_id,
            is_typing=is_typing,
        )

        msg = WSMessage(
            event_type=WSEventTypeEnum.TYPING,
            payload=payload.model_dump(),
        )

        await manager.broadcast_to_room(f"chat_{booking_id}", msg.model_dump())

    async def broadcast_system_alert(self, title: str, message: str, severity: str = "info"):
        """Broadcast platform-wide system alert to all connected Admins."""
        payload = SystemAlertPayload(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            severity=severity,
            title=title,
            message=message,
        )

        msg = WSMessage(
            event_type=WSEventTypeEnum.ADMIN_ALERT,
            payload=payload.model_dump(),
        )

        await manager.broadcast_to_admin(msg.model_dump())

    def get_chat_history(self, booking_id: int) -> list[dict[str, Any]]:
        """Retrieve chat history for a booking."""
        return CHAT_HISTORY_STORE.get(booking_id, [])
