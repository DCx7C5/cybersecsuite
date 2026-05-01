"""Unix socket IPC receiver — receives JSON lines from TypeScript hooks."""

import asyncio
import json
from pathlib import Path

from legacy.logger import getLogger

logger = getLogger(__name__)

SOCKET_PATH = "/tmp/cybersecsuite-hooks.sock"
_server: asyncio.Server | None = None


async def start_ipc_server() -> None:
    """Start the Unix socket IPC server."""
    global _server

    if _server is not None:
        return

    socket_path = Path(SOCKET_PATH)
    if socket_path.exists():
        try:
            socket_path.unlink()
        except Exception:
            pass

    loop = asyncio.get_event_loop()
    _server = await loop.create_unix_server(
        _handle_client,
        path=SOCKET_PATH,
    )

    logger.info(f"IPC server listening on {SOCKET_PATH}")


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Handle a client connection."""
    buffer = b""
    try:
        while True:
            chunk = await reader.read(1024)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if line.strip():
                    try:
                        data = json.loads(line.decode("utf-8"))
                        await _dispatch_event(data)
                    except json.JSONDecodeError:
                        logger.warning(f"IPC: non-JSON line: {line[:100]}")
    except Exception as e:
        logger.error(f"IPC client error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def _dispatch_event(data: dict) -> None:
    """Dispatch received event."""
    event_type = data.get("event", "unknown")
    _payload = data.get("payload", {})
    ts = data.get("ts", "")

    logger.info(f"IPC event: {event_type} at {ts}")

    # TODO: dispatch to SSE /sse/hooks + DB audit


async def stop_ipc_server() -> None:
    """Stop the IPC server."""
    global _server
    if _server:
        _server.close()
        await _server.wait_closed()
        _server = None
        socket_path = Path(SOCKET_PATH)
        if socket_path.exists():
            try:
                socket_path.unlink()
            except Exception:
                pass


_ipc_server_started = False


async def ensure_ipc_server() -> None:
    """Ensure IPC server is started (non-fatal)."""
    global _ipc_server_started
    if _ipc_server_started:
        return
    try:
        await start_ipc_server()
        _ipc_server_started = True
    except Exception as exc:
        logger.warning(f"IPC server failed to start: {exc}")