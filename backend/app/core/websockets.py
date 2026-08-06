from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.auth import User
from app.security.tokens import decode_token

logger = logging.getLogger("homiq.websockets")


def authenticate_ws_token(token: str, db: Session) -> Optional[User]:
    """Validate JWT token for WebSocket connection."""
    try:
        payload: dict[str, Any] = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.get(User, int(user_id))
        if not user or not user.is_active:
            return None
        return user
    except Exception as exc:
        logger.warning(f"WebSocket authentication failed: {exc}")
        return None


class ConnectionManager:
    """Manager for active WebSockets, rooms, roles, and broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.customer_connections: Dict[int, Set[WebSocket]] = {}
        self.technician_connections: Dict[int, Set[WebSocket]] = {}
        self.admin_connections: Set[WebSocket] = set()
        self.room_connections: Dict[str, Set[WebSocket]] = {}
        self.last_heartbeat: Dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket, role: str, identifier: Optional[Any] = None):
        """Accept WebSocket connection and register in role/room maps."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.last_heartbeat[websocket] = datetime.now(timezone.utc)

        if role == "admin":
            self.admin_connections.add(websocket)
        elif role == "customer" and identifier:
            cid = int(identifier)
            if cid not in self.customer_connections:
                self.customer_connections[cid] = set()
            self.customer_connections[cid].add(websocket)
        elif role == "technician" and identifier:
            tid = int(identifier)
            if tid not in self.technician_connections:
                self.technician_connections[tid] = set()
            self.technician_connections[tid].add(websocket)

        logger.info(f"WebSocket connected. Role: {role}, ID: {identifier}. Total active: {len(self.active_connections)}")

    async def join_room(self, room: str, websocket: WebSocket):
        """Add WebSocket to a specific room (e.g. chat_12, location_12)."""
        if room not in self.room_connections:
            self.room_connections[room] = set()
        self.room_connections[room].add(websocket)

    async def leave_room(self, room: str, websocket: WebSocket):
        """Remove WebSocket from a specific room."""
        if room in self.room_connections and websocket in self.room_connections[room]:
            self.room_connections[room].remove(websocket)
            if not self.room_connections[room]:
                del self.room_connections[room]

    def disconnect(self, websocket: WebSocket):
        """Unregister and remove WebSocket connection from all maps."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

        if websocket in self.last_heartbeat:
            del self.last_heartbeat[websocket]

        # Remove from customer maps
        for cid, sockets in list(self.customer_connections.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.customer_connections[cid]

        # Remove from technician maps
        for tid, sockets in list(self.technician_connections.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.technician_connections[tid]

        # Remove from rooms
        for room, sockets in list(self.room_connections.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.room_connections[room]

        logger.info("WebSocket disconnected.")

    def update_heartbeat(self, websocket: WebSocket):
        """Update last active ping timestamp."""
        self.last_heartbeat[websocket] = datetime.now(timezone.utc)

    async def send_json(self, websocket: WebSocket, data: dict[str, Any]):
        """Send JSON payload to a single WebSocket safely."""
        try:
            await websocket.send_text(json.dumps(data))
            self.update_heartbeat(websocket)
        except Exception as exc:
            logger.warning(f"Error sending message to WebSocket: {exc}")
            self.disconnect(websocket)

    async def broadcast_to_customer(self, customer_id: int, data: dict[str, Any]):
        """Broadcast payload to all active sockets of a customer."""
        sockets = self.customer_connections.get(customer_id, set()).copy()
        for ws in sockets:
            await self.send_json(ws, data)

    async def broadcast_to_technician(self, technician_id: int, data: dict[str, Any]):
        """Broadcast payload to all active sockets of a technician."""
        sockets = self.technician_connections.get(technician_id, set()).copy()
        for ws in sockets:
            await self.send_json(ws, data)

    async def broadcast_to_admin(self, data: dict[str, Any]):
        """Broadcast platform-wide updates to all connected admins."""
        sockets = self.admin_connections.copy()
        for ws in sockets:
            await self.send_json(ws, data)

    async def broadcast_to_room(self, room: str, data: dict[str, Any]):
        """Broadcast payload to all sockets in a specific room."""
        sockets = self.room_connections.get(room, set()).copy()
        for ws in sockets:
            await self.send_json(ws, data)


manager = ConnectionManager()
