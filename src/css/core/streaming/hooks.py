"""agents.hooks — SDK hook callbacks for CyberSecSuite.

Provides four hooks for use in ClaudeAgentOptions.hooks:
  - security_hook   (PreToolUse)   — block dangerous commands
  - audit_hook      (PreToolUse)   — log every tools call
"""


from css.core.logger import getLogger
import importlib
import importlib.util
import os
import re
import sys
from typing import Any



logger = getLogger("agents.hooks")


def _load_optional_module(module_name: str) -> object | None:
    if importlib.util.find_spec(module_name) is None:
        return None
    return importlib.import_module(module_name)

# ── Dangerous pattern blocklist ──────────────────────────────────────────────

_BLOCKED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\brm\s+-[rf]{1,2}\s+/"),            # rm -rf /…
    re.compile(r"\bdd\s+if=.*of=/dev/[sh]d"),         # dd wipe
    re.compile(r"DROP\s+TABLE\b", re.IGNORECASE),     # SQL DROP
    re.compile(r"curl\s+.*\|\s*(ba)?sh\b"),           # curl|bash
    re.compile(r"wget\s+.*\|\s*(ba)?sh\b"),           # wget|bash
    re.compile(r"mkfs\b"),                            # format disk
    re.compile(r":(){ :|:& };:"),                     # fork bomb
]

# ── IOC extraction patterns ──────────────────────────────────────────────────

_IPv4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)
_DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}\b")
_SHA256_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
_MD5_RE = re.compile(r"\b[0-9a-fA-F]{32}\b")


# ── Hook callbacks ───────────────────────────────────────────────────────────


async def security_hook(input_data: dict[str, Any], **_: Any) -> dict[str, Any]:
    """PreToolUse — block dangerous shell patterns and SQL drops."""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only inspect Bash/shell invocations
    if tool_name not in ("Bash", "bash", "Shell"):
        return {}

    cmd = tool_input.get("command", "") or tool_input.get("cmd", "")
    for pattern in _BLOCKED_PATTERNS:
        if pattern.search(cmd):
            logger.warning("security_hook BLOCKED: tools=%s pattern=%s", tool_name, pattern.pattern)
            return {
                "action": "block",
                "reason": f"Blocked by security policy: matches pattern '{pattern.pattern}'",
            }
    return {}


async def audit_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    """PreToolUse — log every tools call to structured audit trail."""
    tool_name = input_data.get("tool_name", "")
    agent_id = input_data.get("agent_id", "")
    logger.info("TOOL_CALL tools=%s agents=%s id=%s", tool_name, agent_id, tool_use_id)

    hooks_dir = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "~/Projects/AI")
    if hooks_dir not in sys.path:
        sys.path.insert(0, hooks_dir)

    hooks_module = _load_optional_module("hooks.database")
    if hooks_module is None:
        return {}
    write_scoped_entry_async = getattr(hooks_module, "write_scoped_entry_async", None)
    if not callable(write_scoped_entry_async):
        return {}

    try:
        await write_scoped_entry_async(
            entry_type="tool_call",
            data={
                "tool_name": tool_name,
                "tool_input": input_data.get("tool_input", {}),
                "tool_use_id": tool_use_id,
                "agent_id": agent_id,
            },
        )
    except Exception:
        pass  # audit failures must never block execution
    return {}


async def ioc_hook(
    input_data: dict[str, Any],
    output_data: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """PostToolUse — extract IPs, domains, hashes from tools output."""
    if not output_data:
        return {}

    # Collect all text content from output
    content_blocks = output_data.get("content", [])
    text = " ".join(
        block.get("text", "") for block in content_blocks
        if isinstance(block, dict) and block.get("type") == "text"
    )
    if not text:
        return {}

    iocs: dict[str, list[str]] = {
        "ipv4": list(set(_IPv4_RE.findall(text))),
        "domain": list(set(_DOMAIN_RE.findall(text)))[:20],  # cap domains
        "sha256": list(set(_SHA256_RE.findall(text))),
        "md5": list(set(_MD5_RE.findall(text))),
    }
    iocs = {k: v for k, v in iocs.items() if v}

    if iocs:
        logger.info("ioc_hook found: %s", {k: len(v) for k, v in iocs.items()})
        findings_module = _load_optional_module("cssmcp.cybersec.findings")
        if findings_module is None:
            return {}

        add_ioc = getattr(findings_module, "add_ioc", None)
        handler = getattr(add_ioc, "handler", None)
        if not callable(handler):
            return {}

        for ioc_type, values in iocs.items():
            for value in values[:5]:  # cap at 5 per type
                try:
                    await handler({
                        "value": value,
                        "ioc_type": ioc_type,
                        "source": "ioc_hook",
                        "confidence": "low",
                    })
                except Exception:
                    pass

    return {}


async def cost_hook(stop_data: dict[str, Any], **_: Any) -> dict[str, Any]:
    """Stop hook — log total cost and session ID."""
    cost = stop_data.get("total_cost_usd") or stop_data.get("cost_usd", 0.0)
    session_id = stop_data.get("session_id", "unknown")
    logger.info("SESSION_END session=%s cost_usd=%.4f", session_id, cost)
    return {}
