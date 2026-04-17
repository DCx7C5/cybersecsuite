"""
Agent SDK Integration — bridges cybersecsuite agents with the Claude Agent SDK.

Loads all .claude/agents/*.md agent definitions and exposes them as:
  1. SDK AgentDefinitions for subagent dispatch
  2. Custom MCP tools via create_sdk_mcp_server
  3. A high-level query runner for programmatic agent invocation

Usage:
    from a2a.agent_sdk import build_agent_options, run_agent_query

    # Get options with all agents loaded as subagents
    options = build_agent_options()

    # Run a query through a specific agent
    result = await run_agent_query(
        "cybersec-analyst",
        "Triage CVE-2024-1234 and map to MITRE ATT&CK"
    )
"""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    ResultMessage,
    SystemMessage,
    tool,
    create_sdk_mcp_server,
    ToolAnnotations,
)
from claude_agent_sdk.types import PreToolUseHookInput, HookContext

from a2a.agent_loader import (
    ClaudeAgentCard,
    frontmatter_to_claude_agent,
    load_agents_from_dir,
)
from a2a.registry import AgentRegistry

logger = logging.getLogger("a2a.agent_sdk")


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
    for md in sorted(agents_dir.glob("*.md")):
        card = frontmatter_to_claude_agent(md)
        if card:
            result[card.card.name] = card
    return result


# ── AgentDefinition Conversion ───────────────────────────────────────────────


# Map .claude model shorthand → full Claude API model IDs
_MODEL_MAP: dict[str, str] = {
    "haiku":  "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-5",
    "opus":   "claude-opus-4-5",
}


def _claude_card_to_agent_def(card: ClaudeAgentCard) -> AgentDefinition:
    """Convert a ClaudeAgentCard to an SDK AgentDefinition."""
    # Map .claude tools to SDK built-in tool names
    sdk_tools = []
    for t in card.tools:
        if t in ("Read", "Write", "Edit", "Bash", "Glob", "Grep",
                 "WebSearch", "WebFetch", "Monitor"):
            sdk_tools.append(t)
    # Ensure at least read-only tools
    if not sdk_tools:
        sdk_tools = ["Read", "Glob", "Grep"]

    # Resolve model — prefer frontmatter shorthand, fall back to sonnet
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
    """Build SDK AgentDefinitions from all discovered .claude agents."""
    agents = load_claude_agents()
    defs: dict[str, AgentDefinition] = {}
    for name, card in agents.items():
        # Skip orchestrator — it IS the main agent
        if card.role == "orchestrator":
            continue
        defs[name] = _claude_card_to_agent_def(card)
    return defs


# ── Custom MCP Tools ─────────────────────────────────────────────────────────


@tool(
    "case_open",
    "Open a new investigation case (Phase 0). Collects structured facts for "
    "threat hunting: problem statement, attack hypothesis, known facts, IOCs, "
    "affected assets, timeline hints, and scope constraints.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Short case title"},
            "problem": {"type": "string", "description": "What happened?"},
            "hypothesis": {"type": "string", "description": "Attack hypothesis"},
            "facts": {
                "type": "array", "items": {"type": "string"},
                "description": "Known facts (IPs, hashes, timestamps)",
            },
            "iocs": {
                "type": "array", "items": {"type": "string"},
                "description": "Suspected IOC candidates",
            },
            "assets": {
                "type": "array", "items": {"type": "string"},
                "description": "Affected hosts/services/accounts",
            },
        },
        "required": ["title", "problem"],
    },
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def sdk_case_open(args: dict[str, Any]) -> dict[str, Any]:
    """SDK tool wrapper for Phase 0 case opening."""
    import hashlib
    import json
    from datetime import datetime, timezone

    case_data = {
        "title": args["title"],
        "problem_statement": args["problem"],
        "attack_hypothesis": args.get("hypothesis", ""),
        "known_facts": args.get("facts", []),
        "suspected_iocs": args.get("iocs", []),
        "affected_assets": args.get("assets", []),
        "opened_at": datetime.now(timezone.utc).isoformat(),
    }
    content_hash = hashlib.blake2b(
        json.dumps(case_data, sort_keys=True).encode(), digest_size=32
    ).hexdigest()

    return {
        "content": [{
            "type": "text",
            "text": (
                f"Case opened: {args['title']}\n"
                f"Hash: blake2b:{content_hash}\n"
                f"Facts: {len(args.get('facts', []))}\n"
                f"IOCs: {len(args.get('iocs', []))}\n"
                f"Assets: {len(args.get('assets', []))}\n"
                f"Ready for Phase 1 (Recon)."
            ),
        }],
    }


@tool(
    "list_agents",
    "List all available specialist agents with their roles and capabilities.",
    {},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def sdk_list_agents(args: dict[str, Any]) -> dict[str, Any]:
    """List all registered agents."""
    agents = load_claude_agents()
    lines = []
    for name, card in sorted(agents.items()):
        role = card.role or "specialist"
        skills = ", ".join(s.name for s in card.card.skills[:3])
        lines.append(f"- {name} [{role}] ({card.model}): {skills}")
    return {
        "content": [{
            "type": "text",
            "text": f"Registered agents ({len(agents)}):\n" + "\n".join(lines),
        }],
    }


def create_cybersec_mcp_server():
    """Create an in-process MCP server with cybersecsuite custom tools."""
    return create_sdk_mcp_server(
        name="cybersec",
        version="1.0.0",
        tools=[sdk_case_open, sdk_list_agents],
    )


# ── Hooks ───────────────────────────────────────────────────────────────────


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
    """Build ClaudeAgentOptions with all cybersecsuite agents as subagents.

    Args:
        extra_tools: Additional built-in tools to allow.
        include_mcp: Include the cybersec MCP server with custom tools.
    """
    agents = build_agent_definitions()
    allowed = ["Read", "Glob", "Grep", "Bash", "Agent", "WebSearch"]
    if extra_tools:
        allowed.extend(extra_tools)

    # Add MCP tool wildcards
    if include_mcp:
        allowed.append("mcp__cybersec__*")

    opts = ClaudeAgentOptions(
        allowed_tools=allowed,
        agents=agents,
        hooks={"PreToolUse": [HookMatcher(hooks=[_audit_hook])]},
    )
    if include_mcp:
        opts.mcp_servers = {"cybersec": create_cybersec_mcp_server()}

    return opts


async def run_agent_query(
    agent_name: str,
    prompt: str,
    session_id: str | None = None,
) -> str | None:
    """Run a query delegated to a specific agent and return the result.

    Args:
        agent_name: Name of the agent to delegate to (e.g. 'cybersec-analyst')
        prompt: The task prompt
        session_id: Optional session ID to resume

    Returns:
        The result text, or None if no result.
    """
    options = build_agent_options()
    if session_id:
        options.resume = session_id

    full_prompt = f"Use the {agent_name} agent to: {prompt}"
    result_text: str | None = None

    async for message in query(prompt=full_prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    return result_text


async def run_orchestrator_query(
    prompt: str,
    mode: str = "blue",
    session_id: str | None = None,
) -> dict[str, Any]:
    """Run a full orchestrator query (CYBERSEC-AGENT style).

    Returns session_id and result for chaining.
    """
    options = build_agent_options(extra_tools=["Write", "Edit"])
    if session_id:
        options.resume = session_id

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

