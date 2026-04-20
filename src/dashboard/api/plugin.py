"""Browser Plugin WebSocket Server Integration.

Listens for events from the CCS Browser Plugin (APT Fingerprint Detector).
Receives SIEM events, stores them, and sends prompts for Claude analysis.
"""
import json
import logging
from typing import Optional
from dataclasses import dataclass, asdict

from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


@dataclass
class PluginEvent:
    """Event from browser plugin."""
    event_type: str
    severity: str
    details: dict
    domain: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[int] = None


class PluginWebSocketManager:
    """Manages WebSocket connections from browser plugin."""
    
    def __init__(self):
        self.clients = set()
        self.recent_events = []
        self.max_events = 500
    
    async def register(self, websocket):
        """Register a new plugin client."""
        self.clients.add(websocket)
        logger.info(f"[Plugin] Client connected. Total clients: {len(self.clients)}")
    
    async def unregister(self, websocket):
        """Unregister a plugin client."""
        self.clients.discard(websocket)
        logger.info(f"[Plugin] Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected plugin clients."""
        if not self.clients:
            return
        
        msg_str = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send_text(msg_str)
            except Exception as e:
                logger.warning(f"[Plugin] Failed to send to client: {e}")
                disconnected.add(client)
        
        for client in disconnected:
            await self.unregister(client)
    
    def store_event(self, event: dict):
        """Store event in history."""
        event_obj = PluginEvent(
            event_type=event.get("event_type", "unknown"),
            severity=event.get("severity", "low"),
            details=event.get("details", {}),
            domain=event.get("domain"),
            url=event.get("url"),
            timestamp=event.get("timestamp")
        )
        
        self.recent_events.insert(0, event_obj)
        if len(self.recent_events) > self.max_events:
            self.recent_events.pop()
        
        return event_obj
    
    def get_recent_events(self, limit: int = 50):
        """Get recent events."""
        return [asdict(e) for e in self.recent_events[:limit]]
    
    def get_events_by_severity(self, severity: str):
        """Filter events by severity."""
        return [asdict(e) for e in self.recent_events if e.severity == severity]
    
    def get_events_by_type(self, event_type: str):
        """Filter events by type."""
        return [asdict(e) for e in self.recent_events if e.event_type == event_type]


# Global plugin manager
plugin_manager = PluginWebSocketManager()


class PluginWebSocketEndpoint(WebSocketEndpoint):
    """WebSocket endpoint for browser plugin communication."""
    
    encoding = "text"
    
    async def on_connect(self, websocket):
        await websocket.accept()
        await plugin_manager.register(websocket)
        
        logger.info("[Plugin WS] New connection accepted")
        
        # Send greeting
        await websocket.send_json({
            "type": "connected",
            "version": "1.0",
            "message": "Connected to CyberSecSuite Plugin Server"
        })
    
    async def on_receive(self, websocket, data):
        """Handle incoming message from plugin."""
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            logger.warning("[Plugin WS] Invalid JSON received")
            return
        
        msg_type = message.get("type")
        
        # ── SIEM Event ──
        if msg_type == "siem_event":
            event = message.get("event", {})
            plugin_manager.store_event(event)
            
            severity = event.get("severity", "low")
            event_type = event.get("event_type", "unknown")
            domain = event.get("domain", "unknown")
            
            logger.info(
                f"[Plugin] {severity.upper()} | {event_type} | {domain}"
            )
            
            # TODO: Send to SIEM, database, or analysis pipeline
        
        # ── Ping ──
        elif msg_type == "ping":
            await websocket.send_json({"type": "pong", "ts": message.get("ts")})
        
        # ── Unknown ──
        else:
            logger.warning(f"[Plugin WS] Unknown message type: {msg_type}")
    
    async def on_disconnect(self, websocket, close_code):
        await plugin_manager.unregister(websocket)
        logger.info(f"[Plugin WS] Connection closed ({close_code})")


# HTTP API Endpoints for plugin management

async def api_plugin_status(request):
    """GET /api/plugin/status - Plugin server status."""
    return JSONResponse({
        "status": "running",
        "connected_clients": len(plugin_manager.clients),
        "total_events": len(plugin_manager.recent_events),
        "max_events_stored": plugin_manager.max_events
    })


async def api_plugin_events(request):
    """GET /api/plugin/events - Get recent events."""
    limit = int(request.query_params.get("limit", 50))
    severity = request.query_params.get("severity")
    event_type = request.query_params.get("type")
    
    if severity:
        events = plugin_manager.get_events_by_severity(severity)
    elif event_type:
        events = plugin_manager.get_events_by_type(event_type)
    else:
        events = plugin_manager.get_recent_events(limit)
    
    return JSONResponse({
        "count": len(events),
        "events": events
    })


async def api_plugin_broadcast(request):
    """POST /api/plugin/broadcast - Send message to all connected plugins."""
    data = await request.json()
    
    await plugin_manager.broadcast({
        "type": data.get("type", "message"),
        "prompt": data.get("prompt"),
        "command": data.get("command")
    })
    
    return JSONResponse({
        "status": "broadcasted",
        "clients_count": len(plugin_manager.clients)
    })


async def api_plugin_clear_events(request):
    """POST /api/plugin/events/clear - Clear event history."""
    count = len(plugin_manager.recent_events)
    plugin_manager.recent_events.clear()
    
    return JSONResponse({
        "status": "cleared",
        "events_cleared": count
    })

