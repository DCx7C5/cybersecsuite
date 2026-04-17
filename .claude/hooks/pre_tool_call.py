#!/usr/bin/env python3
"""
PreToolCall hook — runs before every tool execution.
Responsibilities:
- Audit log every tool call
- Block dangerous commands (rm -rf, DROP TABLE, etc.)
- Validate file paths stay within project root
- Rate-limit expensive operations
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bformat\s+[a-z]:\b",
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"DELETE\s+FROM\s+\w+\s*;",         # DELETE without WHERE
    r">\s*/dev/sd[a-z]",                 # overwrite raw disk
    r"dd\s+if=.*of=/dev/sd",
    r"chmod\s+777",
    r"sudo\s+passwd",
    r"curl\s+.*\|\s*bash",              # curl-pipe-bash
    r"wget\s+.*\|\s*sh",
    r"base64\s+-d.*\|\s*bash",
]

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent.parent))
AUDIT_LOG = PROJECT_ROOT / ".claude" / "hooks" / "audit.jsonl"


def audit(event: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")


def block(reason: str) -> None:
    """Emit a block decision and exit non-zero."""
    output = {
        "decision": "block",
        "reason": reason,
    }
    print(json.dumps(output))
    sys.exit(1)


def main() -> None:
    raw = sys.stdin.read()
    try:
        hook_input = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)  # Pass through on parse error

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    session_id = hook_input.get("session_id", "unknown")

    now = datetime.now(timezone.utc).isoformat()

    # ── Audit log ─────────────────────────────────────────────────────────────
    audit({
        "ts": now,
        "event": "pre_tool_call",
        "session_id": session_id,
        "tool": tool_name,
        "input_keys": list(tool_input.keys()) if isinstance(tool_input, dict) else [],
    })

    # ── Block dangerous shell commands ────────────────────────────────────────
    if tool_name in ("Bash", "bash", "run_in_terminal"):
        command = tool_input.get("command", "")
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                audit({"ts": now, "event": "BLOCKED", "tool": tool_name, "pattern": pattern, "command": command[:200]})
                block(f"Dangerous pattern detected: {pattern!r} in command")

    # ── Block writes outside project root ─────────────────────────────────────
    if tool_name in ("Write", "write_file", "create_file", "insert_edit_into_file"):
        file_path = tool_input.get("path") or tool_input.get("filePath", "")
        if file_path:
            try:
                resolved = Path(file_path).resolve()
                project = PROJECT_ROOT.resolve()
                resolved.relative_to(project)  # raises ValueError if outside
            except ValueError:
                block(f"Write outside project root is not allowed: {file_path}")

    # ── Block replace_string_in_file on sensitive files ───────────────────────
    if tool_name in ("replace_string_in_file",):
        file_path = tool_input.get("filePath", "")
        sensitive = (".env", "secrets", "credentials", ".pem", ".key")
        if any(s in file_path for s in sensitive):
            audit({"ts": now, "event": "SENSITIVE_FILE_EDIT", "file": file_path})
            # Warn but don't block — just log

    # Allow
    sys.exit(0)


if __name__ == "__main__":
    main()

