import logging
import json
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("nexus.websocket")

class WebSocketHub:
    """
    Central real-time event distribution hub.
    Broadcasts live incidents, agent updates, telemetry pulses, and approvals to frontend.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast a structured event payload to all subscribed clients."""
        if not self.active_connections:
            return

        message = json.dumps({"event": event_type, "payload": data})
        stale_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client: {e}")
                stale_connections.append(connection)

        for stale in stale_connections:
            self.disconnect(stale)

ws_hub = WebSocketHub()
