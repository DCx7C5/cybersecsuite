"""
Agent SDK Integration — bridges cybersecsuite agents with the Claude Agent SDK.

Loads all .claude/agents/*.md agent definitions and exposes them as:
  1. SDK AgentDefinitions for subagent dispatch
  2. All 36 MCP tools via csmcp (cybersec + dystopian) in-process
  3. A high-level query runner for programmatic agent invocation

Caching
-------
``build_agent_options()`` and ``build_agent_definitions()`` are expensive on first
call (reads all .md files, inits MCP servers). Results are cached at module level
so subsequent calls in the same process are O(1). Call ``clear_caches()`` in tests
or after adding new agents.

Session continuity
------------------
``run_agent_query()`` accepts an optional ``_session_out`` dict. When provided,
the SDK-allocated ``session_id`` from the ``SystemMessage.init`` event is written
into it so callers can thread the same session across multiple queries::

    session_out: dict = {}
    result = await run_agent_query("cybersec-analyst", prompt,
                                   session_id=task.session_id,
                                   _session_out=session_out)
    task.session_id = session_out.get("session_id") or task.session_id

Usage:
    from a2a.agent_sdk import build_agent_options, run_agent_query

    options = build_agent_options()
    result = await run_agent_query("cybersec-analyst", "Triage CVE-2024-1234")
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    ResultMessage,
    SystemMessage,
)
from claude_agent_sdk.types import PreToolUseHookInput, HookContext

from a2a.agent_loader import (
    ClaudeAgentCard,
    frontmatter_to_claude_agent,
    iter_agent_markdown_files,
)
try:
    from hooks.sdk_hooks import build_python_hooks
except ImportError:  # optional during minimal/test installs
    build_python_hooks = None  # type: ignore[assignment]

logger = logging.getLogger("a2a.agent_sdk")


# ── Module-level caches ──────────────────────────────────────────────────────

_OPTIONS_CACHE: ClaudeAgentOptions | None = None  # default build (no extra_tools)
_AGENT_DEFS_CACHE: dict[str, AgentDefinition] | None = None  # all agent defs


def clear_caches() -> None:
    """Invalidate all module-level caches. Use in tests or after adding agents."""
    global _OPTIONS_CACHE, _AGENT_DEFS_CACHE
    _OPTIONS_CACHE = None
    _AGENT_DEFS_CACHE = None


# ── Agent Discovery ──────────────────────────────────────────────────────────


def _find_project_root() -> Path | None:
    """Auto-detect cybersecsuite project root."""
    here = Path(__file__).resolve()
    for candidate in (here.parent.parent.parent, Path.cwd()):
        if (candidate / ".claude" / "agents").exists():
            return candidate
    return None


def load_claude_agents() -> dict[str, ClaudeAgentCard]:
    """Load all .claude/agents/*.md into ClaudeAgentCard instances."""
    root = _find_project_root()
    if not root:
        return {}
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.exists():
        return {}
    result: dict[str, ClaudeAgentCard] = {}
    for md in iter_agent_markdown_files(agents_dir, recurse=True, include_sub_agents=True):
        card = frontmatter_to_claude_agent(md)
        if card and card.card.name not in result:
            result[card.card.name] = card
    return result


# ── AgentDefinition Conversion ───────────────────────────────────────────────


_MODEL_MAP: dict[str, str] = {
    "haiku":  "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-5",
    "opus":   "claude-opus-4-5",
}

_SDK_TOOL_MAP: dict[str, str] = {
    "Read": "Read",
    "Write": "Write",
    "Edit": "Edit",
    "Bash": "Bash",
    "Glob": "Glob",
    "Grep": "Grep",
    "WebSearch": "WebSearch",
    "WebFetch": "WebFetch",
    "Monitor": "Monitor",
    "Task": "Agent",
    "Agent": "Agent",
}


def _claude_card_to_agent_def(card: ClaudeAgentCard) -> AgentDefinition:
    """Convert a ClaudeAgentCard to an SDK AgentDefinition."""
    sdk_tools = []
    for t in card.tools:
        mapped = _SDK_TOOL_MAP.get(t)
        if mapped and mapped not in sdk_tools:
            sdk_tools.append(mapped)
    if not sdk_tools:
        sdk_tools = ["Read", "Glob", "Grep"]

    model_id = _MODEL_MAP.get(card.model.lower(), card.model) if card.model else None

    return AgentDefinition(
        description=card.card.description,
        prompt=(
            f"You are {card.card.name}, a specialist agent in cybersecsuite.\n"
            f"Role: {card.role or 'specialist'}\n"
            f"Max turns: {card.max_turns}\n\n"
            f"{card.card.description}"
        ),
        tools=sdk_tools,
        model=model_id,
    )


def build_agent_definitions() -> dict[str, AgentDefinition]:
    """Build (and cache) SDK AgentDefinitions from all discovered .claude agents."""
    global _AGENT_DEFS_CACHE
    if _AGENT_DEFS_CACHE is None:
        agents = load_claude_agents()
        _AGENT_DEFS_CACHE = {name: _claude_card_to_agent_def(card) for name, card in agents.items()}
    return _AGENT_DEFS_CACHE


# ── Hooks ────────────────────────────────────────────────────────────────────


_AI_HOOKS_DIR = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "/home/daen/Projects/AI")
_HOOKS_OK = False

try:
    import sys as _sys
    if _AI_HOOKS_DIR not in _sys.path:
        _sys.path.insert(0, _AI_HOOKS_DIR)
    from hooks.database import write_scoped_entry_async  # type: ignore[import]
    _HOOKS_OK = True
except ImportError:
    pass


async def _audit_hook(
    input_data: PreToolUseHookInput,
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """PreToolUse hook — logs every tool invocation to the audit trail."""
    if _HOOKS_OK:
        try:
            await write_scoped_entry_async(  # type: ignore[name-defined]
                entry_type="tool_call",
                data={
                    "tool_name": input_data["tool_name"],
                    "tool_input": input_data.get("tool_input", {}),
                    "tool_use_id": tool_use_id,
                    "agent_id": input_data.get("agent_id", ""),
                    "agent_type": input_data.get("agent_type", ""),
                },
            )
        except Exception:
            pass  # never block execution on audit failure
    return {}


# ── High-Level Query Runner ──────────────────────────────────────────────────


def build_agent_options(
    extra_tools: list[str] | None = None,
    include_mcp: bool = True,
) -> ClaudeAgentOptions:
    """Build ClaudeAgentOptions with all 36 csmcp tools + all agent definitions.

    The default configuration (no extra_tools, include_mcp=True) is cached at
    module level so repeated calls within the same process are O(1).  Any
    non-default arguments bypass the cache and build fresh options.

    Args:
        extra_tools: Additional built-in tool names to include (bypasses cache).
        include_mcp: Include all csmcp servers (cybersec + dystopian, 36 tools).
    """
    global _OPTIONS_CACHE

    # Non-default configs are never cached (rare code paths)
    if extra_tools or not include_mcp:
        return _build_agent_options_uncached(extra_tools, include_mcp)

    if _OPTIONS_CACHE is None:
        _OPTIONS_CACHE = _build_agent_options_uncached(None, True)
    return _OPTIONS_CACHE


def _build_agent_options_uncached(
    extra_tools: list[str] | None,
    include_mcp: bool,
) -> ClaudeAgentOptions:
    """Build ClaudeAgentOptions without consulting or populating the cache."""
    from csmcp import all_servers, allowed_tools as mcp_tools

    agents = build_agent_definitions()
    builtin = ["Read", "Glob", "Grep", "Bash", "Agent", "WebSearch"]
    if extra_tools:
        builtin.extend(extra_tools)

    mcp_servers: dict[str, Any] = {}
    allowed: list[str] = list(builtin)

    if include_mcp:
        mcp_servers = all_servers()
        allowed.extend(mcp_tools())

    hooks = (
        build_python_hooks()
        if callable(build_python_hooks)
        else {"PreToolUse": [HookMatcher(hooks=[_audit_hook])]}
    )

    return ClaudeAgentOptions(
        allowed_tools=allowed,
        agents=agents,
        mcp_servers=mcp_servers,
        hooks=hooks,
        env={
            "ANTHROPIC_BASE_URL": os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        },
    )


def _copy_options_with(base: ClaudeAgentOptions, **overrides: Any) -> ClaudeAgentOptions:
    """Return a shallow copy of ClaudeAgentOptions with overrides applied.

    Never mutates the cached singleton — always create a copy before setting
    per-call fields like ``resume`` or ``model``.
    """
    import dataclasses
    if dataclasses.is_dataclass(base):
        copy = dataclasses.replace(base, **overrides)
    else:
        # Pydantic or plain object — copy via __dict__
        copy = base.__class__(**{**base.__dict__, **overrides})
    return copy


async def run_agent_query(
    agent_name: str,
    prompt: str,
    session_id: str | None = None,
    db_session_id: int | None = None,
    project_id: int | None = None,
    link_session: bool = False,
    _session_out: dict[str, Any] | None = None,
) -> str | None:
    """Run a query as a specific named agent and return the result text.

    The agent's ``AgentDefinition.prompt`` (built from its ``.claude/agents/*.md``
    frontmatter) is prepended as context so Claude knows which specialist persona
    to adopt, without relying on fragile subagent-dispatch wording.

    If the agent's ``.md`` frontmatter declares a ``model:`` field, that model is
    passed to the AI proxy so the request is routed to the correct provider
    (e.g. ``deepseek-v3`` → DeepSeek, ``gemini-2.0-flash`` → Google Gemini).

    Args:
        agent_name: Name of the agent to run as (e.g. ``'cybersec-analyst'``).
        prompt: The task prompt.
        session_id: Optional Claude SDK session ID to resume.
        db_session_id: Optional DB session ID; resolves to SDK session_id.
        project_id: Optional project ID for auto-linking (if link_session=True).
        link_session: If True, auto-create DB session and link to SDK session.
        _session_out: Optional dict; if provided, the SDK-allocated
            ``session_id`` from ``SystemMessage.init`` is written into
            ``_session_out["session_id"]`` so callers can thread sessions.

    Returns:
        The result text, or ``None`` if no result was produced.
    """
    # Resolve db_session_id to sdk session_id
    if db_session_id and not session_id:
        try:
            from agent.session_linking import resolve_sdk_id
            session_id = await resolve_sdk_id(db_session_id) or None
        except Exception:
            pass

    agent_defs = build_agent_definitions()

    overrides: dict[str, Any] = {}
    if session_id:
        overrides["resume"] = session_id
    if agent_name in agent_defs and agent_defs[agent_name].model:
        overrides["model"] = agent_defs[agent_name].model

    options = _copy_options_with(build_agent_options(), **overrides) if overrides else build_agent_options()

    agent_context = ""
    if agent_name in agent_defs:
        agent_context = f"[AGENT CONTEXT]\n{agent_defs[agent_name].prompt}\n[/AGENT CONTEXT]\n\n"
    else:
        agent_context = f"[AGENT: {agent_name}]\n\n"

    full_prompt = f"{agent_context}{prompt}"
    result_text: str | None = None

    logger.debug("run_agent_query: agent=%s", agent_name)

    async for message in query(prompt=full_prompt, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            captured = message.data.get("session_id")
            if _session_out is not None:
                _session_out["session_id"] = captured
            logger.debug("run_agent_query: session_id=%s agent=%s", captured, agent_name)
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    # Auto-link session to DB if requested
    if link_session and captured and project_id:
        try:
            from agent.session_linking import create_linked_session
            await create_linked_session(
                project_id=project_id,
                name=f"Auto-linked session for {agent_name}",
                sdk_session_id=captured,
                agent=agent_name,
            )
        except Exception as exc:
            logger.warning("auto-link failed: %s", exc)

    return result_text


async def run_orchestrator_query(
    prompt: str,
    mode: str = "blue",
    session_id: str | None = None,
) -> dict[str, Any]:
    """Run a full orchestrator query (CYBERSEC-AGENT style).

    Routes through the AI proxy at ANTHROPIC_BASE_URL. Returns session_id
    and result for chaining into subsequent calls.
    """
    overrides: dict[str, Any] = {"extra_tools": ["Write", "Edit"]}
    if session_id:
        overrides["resume"] = session_id

    base = build_agent_options(extra_tools=["Write", "Edit"])
    options = _copy_options_with(base, **{k: v for k, v in overrides.items() if k != "extra_tools"})

    captured_session: str | None = None
    result_text: str | None = None

    mode_prefix = f"[MODE: {mode.upper()}] " if mode != "blue" else ""
    full_prompt = f"{mode_prefix}{prompt}"

    async for message in query(prompt=full_prompt, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            captured_session = message.data.get("session_id")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    return {
        "session_id": captured_session,
        "result": result_text,
        "mode": mode,
    }


def _stream_proxy_url() -> str:
    """Resolve OpenAI-compatible chat completion URL from ANTHROPIC_BASE_URL."""
    base = os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1").rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _extract_delta_text(delta: Any) -> str:
    """Extract text chunks from OpenAI delta payloads."""
    if not isinstance(delta, dict):
        return ""

    content = delta.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                txt = item.get("text")
                if isinstance(txt, str):
                    parts.append(txt)
        return "".join(parts)

    return ""


async def run_agent_stream(
    agent_name: str,
    prompt: str,
    queue: asyncio.Queue[dict[str, Any]],
    stream: bool = True,
) -> None:
    """Stream an agent response into queue events for dashboard SSE consumers."""
    started = time.monotonic()
    collected: list[str] = []
    open_tools: dict[str, tuple[str, float]] = {}

    agent_defs = build_agent_definitions()
    default_model = os.environ.get("CYBERSEC_DEFAULT_MODEL", os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"))
    model = default_model
    if agent_name in agent_defs and agent_defs[agent_name].model:
        model = agent_defs[agent_name].model

    if agent_name in agent_defs:
        agent_context = (
            f"[AGENT CONTEXT]\n{agent_defs[agent_name].prompt}\n[/AGENT CONTEXT]\n\n"
        )
    else:
        agent_context = f"[AGENT: {agent_name}]\n\n"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": f"{agent_context}{prompt}"}],
        "stream": True,
    }

    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    stop_reason = "end_turn"

    try:
        timeout = httpx.Timeout(connect=10.0, write=30.0, pool=30.0, read=None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                _stream_proxy_url(),
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code >= 400:
                    body = (await resp.aread()).decode("utf-8", errors="replace")
                    raise RuntimeError(
                        f"stream request failed ({resp.status_code}): {body[:320]}"
                    )

                async for raw_line in resp.aiter_lines():
                    line = raw_line.strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data:
                        continue
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk.get("choices")
                    if not isinstance(choices, list) or not choices:
                        continue
                    choice = choices[0] if isinstance(choices[0], dict) else {}
                    delta = choice.get("delta") if isinstance(choice, dict) else {}
                    finish_reason = (
                        choice.get("finish_reason") if isinstance(choice, dict) else None
                    )

                    if isinstance(delta, dict):
                        tool_calls = delta.get("tool_calls")
                        if isinstance(tool_calls, list):
                            for tc in tool_calls:
                                if not isinstance(tc, dict):
                                    continue
                                tid = str(
                                    tc.get("id")
                                    or tc.get("index")
                                    or f"tool-{len(open_tools) + 1}"
                                )
                                fn = tc.get("function")
                                fn_name = fn.get("name") if isinstance(fn, dict) else None
                                tool_name = fn_name or "tool"
                                if tid not in open_tools:
                                    open_tools[tid] = (tool_name, time.monotonic())
                                    await queue.put(
                                        {
                                            "type": "tool_start",
                                            "name": tool_name,
                                            "ts": int((time.monotonic() - started) * 1000),
                                        }
                                    )

                    text = _extract_delta_text(delta)
                    if text:
                        collected.append(text)
                        if stream:
                            await queue.put({"type": "token", "text": text})

                    if finish_reason:
                        stop_reason = (
                            "end_turn" if finish_reason == "stop" else str(finish_reason)
                        )

                        if finish_reason in ("tool_calls", "stop", "end_turn"):
                            now = time.monotonic()
                            for tool_id, (name, ts) in list(open_tools.items()):
                                await queue.put(
                                    {
                                        "type": "tool_done",
                                        "name": name,
                                        "elapsed_ms": int((now - ts) * 1000),
                                    }
                                )
                                open_tools.pop(tool_id, None)

                        if finish_reason in ("stop", "end_turn"):
                            break

    except asyncio.CancelledError:
        await queue.put({"type": "error", "error": "cancelled"})
        raise
    except Exception as exc:
        await queue.put({"type": "error", "error": str(exc)})
        return

    done_event: dict[str, Any] = {
        "type": "done",
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "stop_reason": stop_reason,
    }
    if not stream:
        done_event["text"] = "".join(collected)
    await queue.put(done_event)
