#!/usr/bin/env python3
"""
PostToolUse Hook — runs after every MCP tool call.
Logs to session changelog and emits A2A task delegation events when relevant.
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import get_project_dir, get_session_dir, audit, append_file, emit, read_stdin

# Tools that produced artifacts worth signing
ARTIFACT_TOOLS = frozenset({
    "create_file", "insert_edit_into_file", "replace_string_in_file",
    "write_file", "Write",
})

# Tools that indicate a delegate/orchestration action
A2A_TOOLS = frozenset({"tasks/send", "tasks/get", "a2a_delegate", "a2a_fanout"})


async def main():
    data = read_stdin()

    tool_name   = data.get("tool_name") or data.get("tool") or "unknown"
    agent_name  = data.get("agent_name") or "MCP"
    tool_output = data.get("tool_result") or data.get("output") or {}
    ts          = datetime.now(timezone.utc)

    project_dir = get_project_dir()
    session_dir = get_session_dir()

    loop = asyncio.get_running_loop()

    # Changelog
    log_line = (
        f"[{ts.isoformat(timespec='seconds')}] post_tool_use:"
        f" agent={agent_name} tool={tool_name}\n"
    )
    await loop.run_in_executor(None, append_file, project_dir / "session_changes.log", log_line)

    # Artifact auto-sign hint
    if tool_name in ARTIFACT_TOOLS:
        file_path = data.get("tool_input", {}).get("filePath") or data.get("tool_input", {}).get("path", "")
        if session_dir and file_path:
            entry = f"- `{file_path}` written by `{agent_name}` at {ts.strftime('%H:%M:%S')}\n"
            await loop.run_in_executor(None, append_file, session_dir / "artifacts.md", entry)

    # IOC capture hint — if output contains IP/hash/domain patterns
    if session_dir:
        output_str = json.dumps(tool_output)
        ioc_hints = _extract_ioc_hints(output_str)
        if ioc_hints:
            ioc_entry = "\n".join(
                f"| `{ioc}` | {kind} | {agent_name} | {ts.strftime('%H:%M:%S')} | auto-detected |"
                for ioc, kind in ioc_hints
            ) + "\n"
            await loop.run_in_executor(None, append_file, session_dir / "iocs.md", ioc_entry)

    audit({"event": "PostToolUse", "tool": tool_name, "agent": agent_name})

    emit({
        "status":    "success",
        "tool":      tool_name,
        "agent":     agent_name,
        "timestamp": ts.isoformat(),
    })

import re  # noqa: E402

_IP_RE   = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
_SHA_RE  = re.compile(r'\b[0-9a-f]{64}\b', re.I)          # SHA256
_DOM_RE  = re.compile(r'\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|ru|cn|onion)\b', re.I)


def _extract_ioc_hints(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for ip in _IP_RE.findall(text)[:5]:
        if not ip.startswith(("127.", "10.", "192.168.", "172.")):
            hits.append((ip, "IP"))
    for sha in _SHA_RE.findall(text)[:3]:
        hits.append((sha[:16] + "…", "SHA256"))
    for dom in _DOM_RE.findall(text)[:3]:
        hits.append((dom, "Domain"))
    return hits


if __name__ == "__main__":
    asyncio.run(main())

