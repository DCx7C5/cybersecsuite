#!/usr/bin/env python3
"""Load hook-specific markdown rules and emit Copilot additional context."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


RULES_DIR = Path(__file__).resolve().parents[1] / "rules" / "hooks"

PAYLOAD_MATCH_KEYS: dict[str, tuple[str, ...]] = {
    "sessionStart": (),
    "sessionEnd": (),
    "userPromptSubmitted": ("prompt", "userPrompt", "user_prompt"),
    "preToolUse": ("toolName", "tool_name"),
    "postToolUse": ("toolName", "tool_name"),
    "postToolUseFailure": ("toolName", "tool_name"),
    "errorOccurred": ("errorContext", "error_context", "recoverable"),
    "notification": ("notification_type", "notificationType"),
    "permissionRequest": ("toolName", "tool_name"),
    "preCompact": ("trigger",),
    "agentStop": ("stopReason", "stop_reason"),
    "subagentStart": ("agentName", "agentDisplayName", "agent_name", "agent_display_name"),
    "subagentStop": ("agentName", "agentDisplayName", "agent_name", "agent_display_name"),
}


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: load_hook_rules.py <event>")

    event = sys.argv[1]
    payload = _read_payload()
    contexts: list[str] = []

    for path in sorted(RULES_DIR.rglob("*.md")):
        frontmatter, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter.get("event") != event:
            continue

        matcher = frontmatter.get("matcher")
        if matcher and not _matches(matcher, _payload_values(event, payload)):
            continue

        title = frontmatter.get("title") or path.stem.replace("-", " ").title()
        content = body.strip()
        if content:
            contexts.append(f"### {title}\n{content}")

    if contexts:
        print(json.dumps({"additionalContext": "\n\n".join(contexts)}))
    else:
        print("{}")
    return 0


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _payload_values(event: str, payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in PAYLOAD_MATCH_KEYS.get(event, ()):
        value = payload.get(key)
        if value is None:
            continue
        values.append(str(value))
    return values


def _matches(pattern: str, candidates: list[str]) -> bool:
    if not candidates:
        return False
    regex = re.compile(pattern)
    return any(regex.fullmatch(candidate) for candidate in candidates)


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break

    if end is None:
        return {}, text

    frontmatter: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.+)$", line)
        if not match:
            continue
        key, value = match.groups()
        frontmatter[key] = _unquote(value.strip())

    body = "\n".join(lines[end + 1 :])
    return frontmatter, body


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
        return str(parsed)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
