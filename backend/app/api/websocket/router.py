"""
Real-Time WebSocket Router and Endpoints.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from app.core.websockets import authenticate_ws_token, manager
from app.database.session import SessionLocal, get_db
from app.models.auth import User
from app.models.bookings import Booking
from app.security.deps import get_current_user
from app.services.websocket import WebSocketService

logger = logging.getLogger("homiq.websockets.router")

router = APIRouter(tags=["Real-Time WebSockets"])


# ── 0. UNIFIED REAL-TIME WEBSOCKET ────────────────────────────────────────

@router.websocket("/ws/live")
async def ws_live_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Access Token"),
):
    """Unified Live Real-Time WebSocket for all roles (Customer, Technician, Admin)."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        from app.crud.customer import CustomerCRUD
        from app.crud.technician import TechnicianCRUD

        cust = CustomerCRUD(db).get_by_user_id(user.id)
        tech = TechnicianCRUD(db).get_by_user_id(user.id)

        role = "customer"
        identifier = cust.id if cust else user.id
        if user.is_superuser or (user.role and user.role.name.lower() == "admin"):
            role = "admin"
            identifier = None
        elif tech or (user.role and user.role.name.lower() == "technician"):
            role = "technician"
            identifier = tech.id if tech else user.id

        await manager.connect(websocket, role=role, identifier=identifier)
        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    pass
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    finally:
        db.close()


# ── 1. CUSTOMER WEBSOCKET ──────────────────────────────────────────────────

@router.websocket("/ws/customer/{customer_id}")
async def ws_customer_endpoint(
    websocket: WebSocket,
    customer_id: int,
    token: str = Query(..., description="JWT Access Token"),
):
    """Customer Real-Time WebSocket for booking updates and notifications."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Security check: User must be customer or superuser
        from app.crud.customer import CustomerCRUD
        cust = CustomerCRUD(db).get_by_user_id(user.id)
        if not user.is_superuser and (not cust or cust.id != customer_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket, role="customer", identifier=customer_id)
        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    pass
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    finally:
        db.close()


# ── 2. TECHNICIAN WEBSOCKET ────────────────────────────────────────────────

@router.websocket("/ws/technician/{technician_id}")
async def ws_technician_endpoint(
    websocket: WebSocket,
    technician_id: int,
    token: str = Query(..., description="JWT Access Token"),
):
    """Technician Real-Time WebSocket for job assignments and alerts."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        from app.crud.technician import TechnicianCRUD
        tech = TechnicianCRUD(db).get_by_user_id(user.id)
        if not user.is_superuser and (not tech or tech.id != technician_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket, role="technician", identifier=technician_id)
        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    pass
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    finally:
        db.close()


# ── 3. ADMIN WEBSOCKET ────────────────────────────────────────────────────

@router.websocket("/ws/admin")
async def ws_admin_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Access Token"),
):
    """Admin Real-Time Control Center WebSocket for platform-wide feeds."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user or not user.is_superuser:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket, role="admin")
        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    pass
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    finally:
        db.close()


# ── 4. LIVE CHAT WEBSOCKET ────────────────────────────────────────────────

@router.websocket("/ws/chat/{booking_id}")
async def ws_chat_endpoint(
    websocket: WebSocket,
    booking_id: int,
    token: str = Query(..., description="JWT Access Token"),
):
    """Customer ↔ Technician Live Chat WebSocket."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        booking = db.get(Booking, booking_id)
        if not booking:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Security check: User must be customer of booking, technician of booking, or admin
        from app.crud.customer import CustomerCRUD
        from app.crud.technician import TechnicianCRUD
        cust = CustomerCRUD(db).get_by_user_id(user.id)
        tech = TechnicianCRUD(db).get_by_user_id(user.id)

        is_owner_cust = cust and booking.customer_id == cust.id
        is_owner_tech = tech and booking.technician_id == tech.id

        if not (user.is_superuser or is_owner_cust or is_owner_tech):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        role = "admin" if user.is_superuser else ("customer" if is_owner_cust else "technician")
        room = f"chat_{booking_id}"

        await websocket.accept()
        await manager.join_room(room, websocket)

        ws_service = WebSocketService(db)

        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    msg_type = data.get("type")
                    if msg_type == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif msg_type == "chat_message":
                        content = data.get("content", "").strip()
                        if content:
                            await ws_service.publish_chat_message(
                                booking_id=booking_id,
                                sender_id=user.id,
                                sender_role=role,
                                content=content,
                            )
                    elif msg_type == "typing":
                        is_typing = bool(data.get("is_typing", False))
                        await ws_service.publish_typing_indicator(
                            booking_id=booking_id,
                            sender_id=user.id,
                            is_typing=is_typing,
                        )
                except Exception as exc:
                    logger.warning(f"Error handling chat message: {exc}")
        except WebSocketDisconnect:
            await manager.leave_room(room, websocket)
    finally:
        db.close()


# ── 5. LIVE GPS LOCATION WEBSOCKET ────────────────────────────────────────

@router.websocket("/ws/location/{booking_id}")
async def ws_location_endpoint(
    websocket: WebSocket,
    booking_id: int,
    token: str = Query(..., description="JWT Access Token"),
):
    """Live Technician GPS Location & ETA Streaming WebSocket."""
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        booking = db.get(Booking, booking_id)
        if not booking:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        room = f"location_{booking_id}"
        await websocket.accept()
        await manager.join_room(room, websocket)

        ws_service = WebSocketService(db)

        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif data.get("type") == "location_update":
                        lat = float(data.get("latitude", 0.0))
                        lng = float(data.get("longitude", 0.0))
                        speed = float(data.get("speed", 0.0))
                        heading = float(data.get("heading", 0.0))
                        eta = data.get("eta_minutes")
                        tech_id = booking.technician_id or 0
                        await ws_service.publish_location_update(
                            booking_id=booking_id,
                            technician_id=tech_id,
                            latitude=lat,
                            longitude=lng,
                            speed=speed,
                            heading=heading,
                            eta_minutes=eta,
                        )
                except Exception as exc:
                    logger.warning(f"Error handling location update: {exc}")
        except WebSocketDisconnect:
            await manager.leave_room(room, websocket)
    finally:
        db.close()


# ── REST HELPER: CHAT HISTORY ─────────────────────────────────────────────

@router.get(
    "/chat/{booking_id}/history",
    summary="Get Chat History",
    description="Returns conversation message history for a booking.",
)
def get_chat_history(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get chat history for a booking."""
    return WebSocketService(db).get_chat_history(booking_id)
