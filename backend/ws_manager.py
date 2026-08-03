"""
WebSocket Manager for Real-Time Compass Updates

Handles WebSocket connections, broadcasting, and room management.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
from datetime import datetime
import json
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with support for:
    - Multiple concurrent clients
    - Room/channel subscriptions
    - Broadcast to all or specific rooms
    - Connection lifecycle management
    - Heartbeat/keepalive
    """

    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Room subscriptions: {room_name: {client_id, ...}}
        self.rooms: Dict[str, Set[str]] = {}

        # Client metadata: {client_id: {metadata}}
        self.client_metadata: Dict[str, dict] = {}

        # Message queue for rate limiting: {client_id: [messages]}
        self.message_queues: Dict[str, List[dict]] = {}

        # Connection timestamps
        self.connection_times: Dict[str, datetime] = {}

        logger.info("WebSocket ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            client_id: Unique identifier for the client

        Returns:
            bool: True if connection successful
        """
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_times[client_id] = datetime.utcnow()
            self.message_queues[client_id] = []

            logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

            # Send welcome message
            await self.send_personal_message({
                "event": "connection.established",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Compass WebSocket"
            }, client_id)

            return True

        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {e}")
            return False

    def disconnect(self, client_id: str):
        """
        Remove a client connection and clean up resources.

        Args:
            client_id: Client identifier to disconnect
        """
        # Remove from all rooms
        for room_name in list(self.rooms.keys()):
            self.leave_room(client_id, room_name)

        # Remove connection
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Clean up metadata
        if client_id in self.client_metadata:
            del self.client_metadata[client_id]

        if client_id in self.message_queues:
            del self.message_queues[client_id]

        if client_id in self.connection_times:
            del self.connection_times[client_id]

        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    def join_room(self, client_id: str, room_name: str):
        """
        Subscribe a client to a room/channel.

        Args:
            client_id: Client identifier
            room_name: Room to join (e.g., "feedback", "clusters", "roadmap")
        """
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        self.rooms[room_name].add(client_id)
        logger.info(f"Client {client_id} joined room '{room_name}'. Room size: {len(self.rooms[room_name])}")

    def leave_room(self, client_id: str, room_name: str):
        """
        Unsubscribe a client from a room.

        Args:
            client_id: Client identifier
            room_name: Room to leave
        """
        if room_name in self.rooms and client_id in self.rooms[room_name]:
            self.rooms[room_name].remove(client_id)

            # Clean up empty rooms
            if len(self.rooms[room_name]) == 0:
                del self.rooms[room_name]

            logger.info(f"Client {client_id} left room '{room_name}'")

    async def send_personal_message(self, message: dict, client_id: str):
        """
        Send a message to a specific client.

        Args:
            message: Message dict to send
            client_id: Target client identifier
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, room_name: Optional[str] = None):
        """
        Broadcast a message to all clients or clients in a specific room.

        Args:
            message: Message dict to broadcast
            room_name: Optional room to broadcast to. If None, broadcasts to all.
        """
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        # Determine target clients
        if room_name and room_name in self.rooms:
            target_clients = self.rooms[room_name]
            logger.debug(f"Broadcasting to room '{room_name}': {len(target_clients)} clients")
        else:
            target_clients = self.active_connections.keys()
            logger.debug(f"Broadcasting to all clients: {len(target_clients)}")

        # Send to all target clients
        disconnected_clients = []
        for client_id in target_clients:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def broadcast_with_rate_limit(self, message: dict, room_name: Optional[str] = None, rate_limit: int = 10):
        """
        Broadcast with rate limiting per connection.

        Args:
            message: Message to broadcast
            room_name: Optional room name
            rate_limit: Maximum messages per client queue
        """
        # Determine target clients
        if room_name and room_name in self.rooms:
            target_clients = self.rooms[room_name]
        else:
            target_clients = self.active_connections.keys()

        # Queue or send messages
        for client_id in target_clients:
            if client_id in self.message_queues:
                queue = self.message_queues[client_id]

                # Rate limiting: drop old messages if queue is full
                if len(queue) >= rate_limit:
                    queue.pop(0)

                queue.append(message)

    async def process_message_queues(self):
        """
        Background task to process queued messages.
        Should be run as an async task.
        """
        while True:
            for client_id, queue in list(self.message_queues.items()):
                if len(queue) > 0 and client_id in self.active_connections:
                    message = queue.pop(0)
                    await self.send_personal_message(message, client_id)

            await asyncio.sleep(0.1)  # Process every 100ms

    async def heartbeat(self, client_id: str, websocket: WebSocket):
        """
        Send periodic heartbeat pings to keep connection alive.

        Args:
            client_id: Client identifier
            websocket: WebSocket connection
        """
        try:
            while client_id in self.active_connections:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds

                if client_id in self.active_connections:
                    await websocket.send_json({
                        "event": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            logger.warning(f"Heartbeat failed for {client_id}: {e}")
            self.disconnect(client_id)

    def get_stats(self) -> dict:
        """
        Get current connection statistics.

        Returns:
            dict: Statistics about connections and rooms
        """
        return {
            "total_connections": len(self.active_connections),
            "active_rooms": len(self.rooms),
            "room_details": {
                room_name: len(clients)
                for room_name, clients in self.rooms.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global connection manager instance
manager = ConnectionManager()


async def handle_client_message(client_id: str, message: dict):
    """
    Handle incoming messages from clients.

    Supports commands like:
    - {"action": "join", "room": "feedback"}
    - {"action": "leave", "room": "feedback"}
    - {"action": "subscribe", "rooms": ["feedback", "clusters"]}

    Args:
        client_id: Client identifier
        message: Parsed message dict
    """
    action = message.get("action")

    if action == "join":
        room = message.get("room")
        if room:
            manager.join_room(client_id, room)
            await manager.send_personal_message({
                "event": "room.joined",
                "room": room,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)

    elif action == "leave":
        room = message.get("room")
        if room:
            manager.leave_room(client_id, room)
            await manager.send_personal_message({
                "event": "room.left",
                "room": room,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)

    elif action == "subscribe":
        rooms = message.get("rooms", [])
        for room in rooms:
            manager.join_room(client_id, room)

        await manager.send_personal_message({
            "event": "rooms.subscribed",
            "rooms": rooms,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)

    elif action == "stats":
        stats = manager.get_stats()
        await manager.send_personal_message({
            "event": "stats.response",
            "data": stats
        }, client_id)

    elif action == "ping":
        await manager.send_personal_message({
            "event": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)

    else:
        await manager.send_personal_message({
            "event": "error",
            "message": f"Unknown action: {action}",
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
