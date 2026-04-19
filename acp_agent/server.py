"""
CyberSecSuite ACP Agent Server

JSON-RPC 2.0 over stdio with Content-Length framing (LSP-style).
Implements the Agent Client Protocol (ACP) so JetBrains AI Assistant
can delegate to the CyberSecSuite AI proxy.

Supported methods:
  initialize       — negotiate protocol version + capabilities
  session/new      — create a new chat session
  session/prompt   — process a user turn (streams session/update notifications)
  session/status   — return session metadata (optional, silently ignored if absent)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any

import httpx

# --------------------------------------------------------------------------- #
# Logging — stderr only (stdout is the JSON-RPC channel)
# --------------------------------------------------------------------------- #
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [acp] %(levelname)s %(message)s",
)
log = logging.getLogger("acp_agent")

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
PROTOCOL_VERSION = 1
AGENT_NAME = "CyberSecSuite"
AGENT_VERSION = "1.0.0"

PROXY_URL = os.environ.get("CYBERSEC_PROXY_URL", "http://localhost:8000/v1")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "sk-placeholder")
MODEL = os.environ.get("CYBERSEC_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = (
    "You are CyberSecSuite — an elite cybersecurity forensics AI assistant.\n"
    "You have deep expertise in: threat hunting, incident response, MITRE ATT&CK, "
    "CVE/CWE analysis, network forensics, malware reverse engineering, OSINT, "
    "cryptography, digital forensics, and security architecture review.\n\n"
    "Answer questions clearly and concisely. When analysing artefacts or logs, "
    "structure findings with: Observation → MITRE technique → Severity → Remediation.\n"
    "Always cite CVE/CWE IDs and MITRE technique IDs when relevant.\n"
    "The project root is /home/daen/Projects/cybersecsuite."
)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
_sessions: dict[str, list[dict]] = {}   # sessionId → list of {role, content} messages


# --------------------------------------------------------------------------- #
# JSON-RPC framing helpers
# --------------------------------------------------------------------------- #

def _encode(message: dict) -> bytes:
    body = json.dumps(message, ensure_ascii=False).encode()
    return f"Content-Length: {len(body)}\r\n\r\n".encode() + body


async def _read_one(reader: asyncio.StreamReader) -> dict | None:
    """Read one Content-Length framed JSON-RPC message from *reader*."""
    headers: dict[str, str] = {}
    while True:
        try:
            raw = await reader.readline()
        except (asyncio.IncompleteReadError, ConnectionResetError):
            return None
        if not raw:
            return None
        line = raw.decode(errors="replace").strip()
        if not line:
            break
        if ":" in line:
            k, _, v = line.partition(":")
            headers[k.strip().lower()] = v.strip()

    length = int(headers.get("content-length", 0))
    if length == 0:
        return None
    try:
        body = await reader.readexactly(length)
    except asyncio.IncompleteReadError:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        log.warning("JSON parse error: %s", exc)
        return None


def _send(writer: asyncio.StreamWriter, message: dict) -> None:
    writer.write(_encode(message))


async def _flush(writer: asyncio.StreamWriter) -> None:
    await writer.drain()


# --------------------------------------------------------------------------- #
# ACP method handlers
# --------------------------------------------------------------------------- #

def _ok(msg_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _err(msg_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


async def handle_initialize(params: dict, msg_id: Any, writer: asyncio.StreamWriter) -> dict:
    return _ok(msg_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "agentCapabilities": {
            "sessions": {"new": True, "load": False},
        },
        "meta": {"name": AGENT_NAME, "version": AGENT_VERSION},
        "authenticationMethods": [],
    })


async def handle_session_new(params: dict, msg_id: Any, writer: asyncio.StreamWriter) -> dict:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = []
    log.info("New session: %s", session_id)
    return _ok(msg_id, {"sessionId": session_id})


async def handle_session_prompt(
    params: dict, msg_id: Any, writer: asyncio.StreamWriter
) -> dict:
    session_id = params.get("sessionId", "")
    if not session_id or session_id not in _sessions:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = []

    history = _sessions[session_id]

    # Extract user text from either `prompt.content` (ACP spec) or `messages`
    user_text = _extract_user_text(params)
    if not user_text:
        return _err(msg_id, -32602, "No user text in prompt params")

    history.append({"role": "user", "content": user_text})

    full_text = await _call_ai_proxy(session_id, history, writer)
    history.append({"role": "assistant", "content": full_text})

    return _ok(msg_id, {
        "sessionId": session_id,
        "content": [{"type": "text", "text": full_text}],
    })


def _extract_user_text(params: dict) -> str:
    """Pull user text from various ACP prompt param shapes."""
    # ACP standard: params.prompt.content = [{type: text, text: ...}]
    prompt = params.get("prompt", {})
    if isinstance(prompt, dict):
        content = prompt.get("content", [])
        if isinstance(content, list):
            return "".join(
                b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
            )
        if isinstance(content, str):
            return content

    # Fallback: params.messages (OpenAI-style)
    messages = params.get("messages", [])
    if isinstance(messages, list):
        parts = []
        for m in messages:
            if isinstance(m, dict) and m.get("role") == "user":
                c = m.get("content", "")
                if isinstance(c, str):
                    parts.append(c)
                elif isinstance(c, list):
                    parts.extend(b.get("text", "") for b in c if isinstance(b, dict))
        return " ".join(parts)

    return ""


async def _call_ai_proxy(
    session_id: str,
    history: list[dict],
    writer: asyncio.StreamWriter,
) -> str:
    """Stream a completion from the AI proxy and emit session/update notifications."""
    full_text = ""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST",
                f"{PROXY_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                json={
                    "model": MODEL,
                    "stream": True,
                    "system": SYSTEM_PROMPT,
                    "messages": history,
                    "max_tokens": 4096,
                },
            ) as resp:
                if resp.status_code >= 400:
                    body = await resp.aread()
                    log.error("API error %d: %s", resp.status_code, body[:300])
                    return f"[API error {resp.status_code}]"

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    # OpenAI-compatible SSE delta
                    delta = (
                        chunk.get("choices", [{}])[0].get("delta", {})
                        if "choices" in chunk
                        else chunk.get("delta", {})   # Anthropic direct
                    )
                    text = delta.get("content", "") or delta.get("text", "")
                    if not text:
                        continue

                    full_text += text
                    _send(writer, {
                        "jsonrpc": "2.0",
                        "method": "session/update",
                        "params": {
                            "sessionId": session_id,
                            "update": {
                                "kind": "message",
                                "role": "assistant",
                                "content": [{"type": "text", "text": text}],
                            },
                        },
                    })
                    await _flush(writer)

    except httpx.ConnectError:
        log.warning("AI proxy unavailable at %s — returning offline message", PROXY_URL)
        full_text = (
            "⚠️ CyberSecSuite AI proxy is offline. "
            f"Start it with `docker-compose up -d` at the project root "
            f"(/home/daen/Projects/cybersecsuite)."
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("Unexpected error calling AI proxy")
        full_text = f"[Error: {exc}]"

    return full_text


# --------------------------------------------------------------------------- #
# Main dispatch loop
# --------------------------------------------------------------------------- #

HANDLERS = {
    "initialize": handle_initialize,
    "session/new": handle_session_new,
    "session/prompt": handle_session_prompt,
}


async def run() -> None:
    loop = asyncio.get_event_loop()

    # Connect stdin as asyncio StreamReader
    reader = asyncio.StreamReader()
    read_proto = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: read_proto, sys.stdin.buffer)

    # Connect stdout as asyncio StreamWriter
    w_transport, w_proto = await loop.connect_write_pipe(
        asyncio.BaseProtocol, sys.stdout.buffer
    )
    writer = asyncio.StreamWriter(w_transport, w_proto, reader, loop)  # type: ignore[arg-type]

    log.info("%s v%s ACP agent started (proxy=%s model=%s)", AGENT_NAME, AGENT_VERSION, PROXY_URL, MODEL)

    while True:
        msg = await _read_one(reader)
        if msg is None:
            log.info("stdin closed — exiting")
            break

        method = msg.get("method", "")
        msg_id = msg.get("id")         # None for notifications
        params = msg.get("params", {}) or {}

        log.debug("→ %s (id=%s)", method, msg_id)

        handler = HANDLERS.get(method)
        if handler:
            try:
                response = await handler(params, msg_id, writer)
            except Exception as exc:  # noqa: BLE001
                log.exception("Handler error for %s", method)
                response = _err(msg_id, -32603, str(exc))

            if msg_id is not None:
                _send(writer, response)
                await _flush(writer)
        elif msg_id is not None:
            # Unknown method — respond with error
            _send(writer, _err(msg_id, -32601, f"Method not found: {method}"))
            await _flush(writer)
        # else: notification we don't handle — silently ignore


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
