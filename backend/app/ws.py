"""WebSocket endpoint for streaming agent actions to the frontend.

Streams: screenshots (base64), action events, task completion scores.
"""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Active WebSocket connections
_connections: list[WebSocket] = []


async def broadcast(event: dict):
    """Send an event to all connected WebSocket clients."""
    message = json.dumps(event, default=str)
    disconnected = []
    for ws in _connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        _connections.remove(ws)


async def agent_event_callback(event: dict):
    """Callback passed to the agent — broadcasts events to all connected clients."""
    await broadcast(event)


@router.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket):
    """WebSocket endpoint for live agent event streaming.

    Clients connect here to receive real-time agent screenshots and action logs.
    """
    await websocket.accept()
    _connections.append(websocket)

    try:
        # Keep connection alive, listen for client messages (e.g., cancel)
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=300)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_text(json.dumps({"type": "keepalive"}))
            except WebSocketDisconnect:
                break
    finally:
        if websocket in _connections:
            _connections.remove(websocket)
