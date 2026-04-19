"""
CyberSecSuite ACP Agent Server

JSON-RPC 2.0 over stdio with Content-Length framing (LSP-style).
Implements the Agent Client Protocol (ACP) so JetBrains AI Assistant
can delegate to the CyberSecSuite AI proxy.

Supported methods:
  initialize              — negotiate protocol version + capabilities
  session/new             — create a new chat session (accepts model/agent/reasoning_effort options)
  session/prompt          — process a user turn (streams session/update notifications)
  session/configure       — update model/agent/reasoning_effort for an existing session
  session/status          — return session metadata

Slash commands (type in chat):
  /model <name>                    — switch model (e.g. claude-opus-4.6, gpt-5.4)
  /agent <name>                    — switch agent persona (forensics, code, osint, pentest, general)
  /effort <low|medium|high>        — set OpenAI reasoning_effort (passed directly to the API)
  /reset                           — clear conversation history
  /status                          — show current session configuration
  /help                            — list available commands
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
# Constants / defaults
# --------------------------------------------------------------------------- #
PROTOCOL_VERSION = 1
AGENT_NAME = "CyberSecSuite"
AGENT_VERSION = "1.1.0"

PROXY_URL = os.environ.get("CYBERSEC_PROXY_URL", "http://localhost:8000/v1")
API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "sk-placeholder")

DEFAULT_MODEL           = os.environ.get("CYBERSEC_MODEL",            "claude-sonnet-4-5")
DEFAULT_AGENT           = os.environ.get("CYBERSEC_AGENT",            "forensics")
DEFAULT_REASONING_EFFORT = os.environ.get("CYBERSEC_REASONING_EFFORT", "medium")

REASONING_EFFORT_VALUES = {"low", "medium", "high"}
REASONING_EFFORT_ALIASES = {"lo": "low", "med": "medium", "hi": "high"}

# --------------------------------------------------------------------------- #
# Agent personas (system prompts)
# --------------------------------------------------------------------------- #
_PROJECT_ROOT = "/home/daen/Projects/cybersecsuite"

AGENT_PERSONAS: dict[str, str] = {
    "forensics": (
        "You are CyberSecSuite — an elite cybersecurity forensics AI assistant.\n"
        "You have deep expertise in: threat hunting, incident response, MITRE ATT&CK, "
        "CVE/CWE analysis, network forensics, malware reverse engineering, OSINT, "
        "cryptography, digital forensics, and security architecture review.\n\n"
        "When analysing artefacts or logs, structure findings with:\n"
        "  Observation → MITRE technique → Severity → Remediation\n"
        "Always cite CVE/CWE IDs and MITRE technique IDs when relevant.\n"
        f"The project root is {_PROJECT_ROOT}."
    ),
    "code": (
        "You are CyberSecSuite Code — a security-focused software engineering assistant.\n"
        "Specialise in: secure Python (FastAPI, asyncio, Tortoise ORM, Pydantic v2), "
        "cryptography (Ed25519, BLAKE2b, Argon2id, AES-GCM), "
        "SAST/DAST, supply-chain security, and hardened CI/CD pipelines.\n\n"
        "Review code for OWASP Top 10, CWE patterns, and injection vectors. "
        "Suggest fixes with minimal diffs. Cite CWE IDs for vulnerabilities found.\n"
        f"The project root is {_PROJECT_ROOT}."
    ),
    "osint": (
        "You are CyberSecSuite OSINT — an open-source intelligence specialist.\n"
        "Specialise in: passive reconnaissance, domain/IP/ASN pivoting, "
        "certificate transparency, breach data correlation, social engineering indicators, "
        "dark web intelligence, threat actor attribution, and IOC enrichment.\n\n"
        "Structure outputs as: Target → Data Sources → Findings → Confidence → Next Steps.\n"
        f"The project root is {_PROJECT_ROOT}."
    ),
    "pentest": (
        "You are CyberSecSuite PenTest — an offensive security and penetration testing assistant.\n"
        "Specialise in: attack surface mapping, exploitation techniques (OWASP, CVE-based), "
        "privilege escalation, lateral movement, persistence mechanisms, "
        "Active Directory attacks, and red team tradecraft.\n\n"
        "Always include defensive mitigations alongside attack paths. "
        "Reference MITRE ATT&CK techniques by ID.\n"
        f"The project root is {_PROJECT_ROOT}."
    ),
    "general": (
        "You are CyberSecSuite — a versatile cybersecurity AI assistant.\n"
        "You can help with any security topic: analysis, coding, research, planning, "
        "documentation, architecture review, or general questions.\n"
        "Be concise and accurate. Cite relevant standards (NIST, ISO 27001, CIS) when applicable.\n"
        f"The project root is {_PROJECT_ROOT}."
    ),
}

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
class Session:
    def __init__(self, model: str, agent: str, reasoning_effort: str) -> None:
        self.history: list[dict] = []
        self.model            = model
        self.agent            = agent
        self.reasoning_effort = reasoning_effort

    def system_prompt(self) -> str:
        return AGENT_PERSONAS.get(self.agent, AGENT_PERSONAS["forensics"])

    def status_text(self) -> str:
        return (
            f"**Session config**\n"
            f"- model:            `{self.model}`\n"
            f"- agent:            `{self.agent}` — {_agent_summary(self.agent)}\n"
            f"- reasoning_effort: `{self.reasoning_effort}` (passed directly to the API)\n"
            f"- turns:            {len(self.history) // 2}\n\n"
            f"**Available agents:** {', '.join(f'`{k}`' for k in AGENT_PERSONAS)}\n"
            f"**Effort levels:** `low` · `medium` · `high`\n"
            f"**Slash commands:** `/model` · `/agent` · `/effort` · `/reset` · `/status` · `/help`"
        )


def _agent_summary(agent: str) -> str:
    summaries = {
        "forensics": "incident response & MITRE ATT&CK",
        "code":      "secure coding & vulnerability review",
        "osint":     "open-source intelligence & attribution",
        "pentest":   "penetration testing & red team",
        "general":   "general-purpose security assistant",
    }
    return summaries.get(agent, "unknown")


def _normalise_effort(value: str) -> str | None:
    v = value.lower().strip()
    v = REASONING_EFFORT_ALIASES.get(v, v)
    return v if v in REASONING_EFFORT_VALUES else None


_sessions: dict[str, Session] = {}

HELP_TEXT = (
    "**CyberSecSuite ACP — slash commands**\n\n"
    "| Command | Description |\n"
    "|---------|-------------|\n"
    "| `/model <name>` | Switch model (e.g. `claude-opus-4.6`, `gpt-5.4`, `gpt-4.1`) |\n"
    "| `/agent <name>` | Switch persona: `forensics` `code` `osint` `pentest` `general` |\n"
    "| `/effort <level>` | Set depth: `low` (fast) · `medium` (default) · `high` (thorough) |\n"
    "| `/reset` | Clear conversation history |\n"
    "| `/status` | Show current model / agent / effort |\n"
    "| `/help` | Show this message |"
)


# --------------------------------------------------------------------------- #
# Slash-command parser
# --------------------------------------------------------------------------- #

def _handle_slash_command(text: str, session: Session) -> str | None:
    """
    If *text* is a slash command, mutate *session* and return a reply string.
    Return None if it is not a slash command.
    """
    stripped = text.strip()
    if not stripped.startswith("/"):
        return None

    parts = stripped.split(maxsplit=1)
    cmd   = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ""

    if cmd == "/help":
        return HELP_TEXT

    if cmd == "/status":
        return session.status_text()

    if cmd == "/reset":
        session.history.clear()
        return "✅ Conversation history cleared."

    if cmd == "/model":
        if not arg:
            return f"Usage: `/model <name>` — current model is `{session.model}`"
        session.model = arg
        log.info("Session model → %s", arg)
        return f"✅ Model set to `{arg}`."

    if cmd == "/agent":
        if not arg:
            opts = ", ".join(f"`{k}`" for k in AGENT_PERSONAS)
            return f"Usage: `/agent <name>` — available: {opts}"
        if arg not in AGENT_PERSONAS:
            opts = ", ".join(f"`{k}`" for k in AGENT_PERSONAS)
            return f"❌ Unknown agent `{arg}`. Available: {opts}"
        session.agent = arg
        log.info("Session agent → %s", arg)
        return f"✅ Agent set to `{arg}` — {_agent_summary(arg)}."

    if cmd == "/effort":
        if not arg:
            return f"Usage: `/effort <low|medium|high>` — current reasoning_effort is `{session.reasoning_effort}`"
        normed = _normalise_effort(arg)
        if normed is None:
            return f"❌ Unknown effort `{arg}`. Use `low`, `medium`, or `high`."
        session.reasoning_effort = normed
        log.info("Session reasoning_effort → %s", normed)
        return f"✅ reasoning_effort set to `{normed}` (passed directly to the API)."

    # Unknown slash command — pass through to AI so it can explain or handle it
    return None


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
        "meta": {
            "name": AGENT_NAME,
            "version": AGENT_VERSION,
            "description": (
                "CyberSecSuite forensics AI — supports /model, /agent, /effort slash commands. "
                f"Agents: {', '.join(AGENT_PERSONAS)}. "
                "Effort: low | medium | high."
            ),
        },
        "authenticationMethods": [],
    })


async def handle_session_new(params: dict, msg_id: Any, writer: asyncio.StreamWriter) -> dict:
    """
    Create a new session. Accepts optional options:
      { model: str, agent: str, effort: str }
    These can also be set via env vars CYBERSEC_MODEL / CYBERSEC_AGENT / CYBERSEC_EFFORT.
    """
    options = params.get("options", {}) or {}
    model            = options.get("model",            DEFAULT_MODEL)
    agent            = options.get("agent",            DEFAULT_AGENT)
    reasoning_effort = _normalise_effort(options.get("reasoning_effort", DEFAULT_REASONING_EFFORT)) or DEFAULT_REASONING_EFFORT

    if agent not in AGENT_PERSONAS:
        agent = DEFAULT_AGENT

    session_id = str(uuid.uuid4())
    _sessions[session_id] = Session(model=model, agent=agent, reasoning_effort=reasoning_effort)
    log.info("New session %s (model=%s agent=%s reasoning_effort=%s)", session_id, model, agent, reasoning_effort)
    return _ok(msg_id, {"sessionId": session_id})


async def handle_session_configure(params: dict, msg_id: Any, writer: asyncio.StreamWriter) -> dict:
    """Update model/agent/effort for an existing session without resetting history."""
    session_id = params.get("sessionId", "")
    session = _sessions.get(session_id)
    if not session:
        return _err(msg_id, -32602, f"Unknown sessionId: {session_id!r}")

    changed: list[str] = []
    if model := params.get("model"):
        session.model = model
        changed.append(f"model={model}")
    if agent := params.get("agent"):
        if agent in AGENT_PERSONAS:
            session.agent = agent
            changed.append(f"agent={agent}")
    if effort_raw := params.get("reasoning_effort"):
        if normed := _normalise_effort(effort_raw):
            session.reasoning_effort = normed
            changed.append(f"reasoning_effort={normed}")

    log.info("Session %s configured: %s", session_id, ", ".join(changed) or "no changes")
    return _ok(msg_id, {"sessionId": session_id, "applied": changed})


async def handle_session_status(params: dict, msg_id: Any, writer: asyncio.StreamWriter) -> dict:
    session_id = params.get("sessionId", "")
    session = _sessions.get(session_id)
    if not session:
        return _err(msg_id, -32602, f"Unknown sessionId: {session_id!r}")
    return _ok(msg_id, {
        "sessionId":       session_id,
        "model":           session.model,
        "agent":           session.agent,
        "reasoning_effort": session.reasoning_effort,
        "turns":           len(session.history) // 2,
    })


async def handle_session_prompt(
    params: dict, msg_id: Any, writer: asyncio.StreamWriter
) -> dict:
    session_id = params.get("sessionId", "")
    if not session_id or session_id not in _sessions:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = Session(
            model=DEFAULT_MODEL, agent=DEFAULT_AGENT, reasoning_effort=DEFAULT_REASONING_EFFORT
        )

    session = _sessions[session_id]

    user_text = _extract_user_text(params)
    if not user_text:
        return _err(msg_id, -32602, "No user text in prompt params")

    # Check for slash command — handle locally without calling the AI
    slash_reply = _handle_slash_command(user_text, session)
    if slash_reply is not None:
        _send(writer, {
            "jsonrpc": "2.0",
            "method": "session/update",
            "params": {
                "sessionId": session_id,
                "update": {
                    "kind": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": slash_reply}],
                },
            },
        })
        await _flush(writer)
        return _ok(msg_id, {
            "sessionId": session_id,
            "content": [{"type": "text", "text": slash_reply}],
        })

    session.history.append({"role": "user", "content": user_text})
    full_text = await _call_ai_proxy(session, writer)
    session.history.append({"role": "assistant", "content": full_text})

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


async def _call_ai_proxy(session: Session, writer: asyncio.StreamWriter) -> str:
    """Stream a completion from the AI proxy and emit session/update notifications."""
    full_text = ""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0)) as client:
            async with client.stream(
                "POST",
                f"{PROXY_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                json={
                    "model":            session.model,
                    "stream":           True,
                    "system":           session.system_prompt(),
                    "messages":         session.history,
                    "reasoning_effort": session.reasoning_effort,
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

                    delta = (
                        chunk.get("choices", [{}])[0].get("delta", {})
                        if "choices" in chunk
                        else chunk.get("delta", {})
                    )
                    text = delta.get("content", "") or delta.get("text", "")
                    if not text:
                        continue

                    full_text += text
                    _send(writer, {
                        "jsonrpc": "2.0",
                        "method": "session/update",
                        "params": {
                            "sessionId": id(session),  # stable within process
                            "update": {
                                "kind": "message",
                                "role": "assistant",
                                "content": [{"type": "text", "text": text}],
                            },
                        },
                    })
                    await _flush(writer)

    except httpx.ConnectError:
        log.warning("AI proxy unavailable at %s", PROXY_URL)
        full_text = (
            "⚠️ CyberSecSuite AI proxy is offline. "
            "Start it with `docker-compose up -d` at "
            f"`{_PROJECT_ROOT}`."
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("Unexpected error calling AI proxy")
        full_text = f"[Error: {exc}]"

    return full_text


# --------------------------------------------------------------------------- #
# Main dispatch loop
# --------------------------------------------------------------------------- #

HANDLERS = {
    "initialize":        handle_initialize,
    "session/new":       handle_session_new,
    "session/prompt":    handle_session_prompt,
    "session/configure": handle_session_configure,
    "session/status":    handle_session_status,
}


async def run() -> None:
    loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    read_proto = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: read_proto, sys.stdin.buffer)

    w_transport, w_proto = await loop.connect_write_pipe(
        asyncio.BaseProtocol, sys.stdout.buffer
    )
    writer = asyncio.StreamWriter(w_transport, w_proto, reader, loop)  # type: ignore[arg-type]

    log.info(
        "%s v%s started — proxy=%s default=(model=%s agent=%s reasoning_effort=%s)",
        AGENT_NAME, AGENT_VERSION, PROXY_URL,
        DEFAULT_MODEL, DEFAULT_AGENT, DEFAULT_REASONING_EFFORT,
    )

    while True:
        msg = await _read_one(reader)
        if msg is None:
            log.info("stdin closed — exiting")
            break

        method = msg.get("method", "")
        msg_id = msg.get("id")
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
            _send(writer, _err(msg_id, -32601, f"Method not found: {method}"))
            await _flush(writer)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
