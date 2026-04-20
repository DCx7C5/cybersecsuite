"""Python SDK hook registry for Claude Agent SDK runtime."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claude_agent_sdk import HookMatcher

from hooks._utils import PROJECT_ROOT, audit


_PROJECT_ROOT_RESOLVED = PROJECT_ROOT.resolve()


def _safe_json_size(value: Any) -> int:
    try:
        return len(json.dumps(value, ensure_ascii=True))
    except Exception:
        return len(str(value))


def _extract_candidate_paths(tool_input: dict[str, Any]) -> list[Path]:
    keys = ("path", "filePath", "target_file", "target_notebook", "working_directory", "cwd")
    out: list[Path] = []
    for key in keys:
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            out.append(Path(val).expanduser())
    return out


def _is_within_project(path: Path) -> bool:
    try:
        resolved = path.resolve()
        resolved.relative_to(_PROJECT_ROOT_RESOLVED)
        return True
    except Exception:
        return False


async def _pre_tool_write_guard(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        tool_input = event.get("tool_input", {}) if isinstance(event.get("tool_input"), dict) else {}
        for candidate in _extract_candidate_paths(tool_input):
            if not _is_within_project(candidate):
                reason = f"Tool path outside PROJECT_ROOT denied: {candidate}"
                audit({"event": "PreToolUseDenied", "tool": event.get("tool_name", ""), "reason": reason})
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
    except Exception as exc:
        audit({"event": "HookError", "hook": "_pre_tool_write_guard", "error": str(exc)})
    return {}


async def _pre_tool_audit(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        # Fire-and-forget style: keep hook response immediate.
        asyncio.create_task(
            asyncio.to_thread(
                audit,
                {
                    "event": "PreToolUse",
                    "tool": event.get("tool_name", ""),
                    "agent": event.get("agent_type", ""),
                    "ts": datetime.now(timezone.utc).isoformat(),
                },
            )
        )
    except Exception as exc:
        audit({"event": "HookError", "hook": "_pre_tool_audit", "error": str(exc)})
    return {}


async def _post_tool_audit(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        result = event.get("tool_response")
        if result is None:
            result = event.get("tool_result")
        audit({
            "event": "PostToolUse",
            "tool": event.get("tool_name", ""),
            "result_size": _safe_json_size(result),
        })
    except Exception as exc:
        audit({"event": "HookError", "hook": "_post_tool_audit", "error": str(exc)})
    return {}


async def _post_tool_failure_audit(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        err = event.get("error") or event.get("message") or ""
        audit({"event": "PostToolUseFailure", "tool": event.get("tool_name", ""), "error": str(err)[:500]})
    except Exception as exc:
        audit({"event": "HookError", "hook": "_post_tool_failure_audit", "error": str(exc)})
    return {}


async def _user_prompt_context(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        from template_engine.context import get_context

        ctx = get_context(project_dir=PROJECT_ROOT)
        if ctx:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"Current scope context: {json.dumps(ctx, ensure_ascii=True)[:3000]}",
                }
            }
    except Exception:
        pass
    return {}


async def _stop_snapshot(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        from cybersecsuite import CyberSecSuiteSDK

        info = CyberSecSuiteSDK(project_dir=PROJECT_ROOT).last_session()
        audit(
            {
                "event": "Stop",
                "agent": event.get("agent_type", ""),
                "last_session": info.name if info else None,
                "last_session_path": str(info.path) if info else None,
            }
        )
    except Exception as exc:
        audit({"event": "HookError", "hook": "_stop_snapshot", "error": str(exc)})
    return {}


async def _subagent_start(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        audit(
            {
                "event": "SubagentStart",
                "agent": event.get("agent_name") or event.get("agent_type", ""),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as exc:
        audit({"event": "HookError", "hook": "_subagent_start", "error": str(exc)})
    return {}


async def _subagent_stop(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        audit(
            {
                "event": "SubagentStop",
                "agent": event.get("agent_name") or event.get("agent_type", ""),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as exc:
        audit({"event": "HookError", "hook": "_subagent_stop", "error": str(exc)})
    return {}


async def _pre_compact(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        asyncio.create_task(asyncio.to_thread(audit, {"event": "PreCompact", "agent": event.get("agent_type", "")}))
        return {"async_": True}
    except Exception as exc:
        audit({"event": "HookError", "hook": "_pre_compact", "error": str(exc)})
    return {}


async def _permission_auto_allow(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Auto-approved safe read-only tool",
                },
            }
        }
    except Exception:
        return {}


async def _permission_default_ask(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "permissionDecision": "ask",
                    "permissionDecisionReason": "Default interactive approval",
                },
            }
        }
    except Exception:
        return {}


async def _notification_hook(event: dict[str, Any], *_: Any) -> dict[str, Any]:
    try:
        message = str(event.get("message") or event.get("text") or "")
        title = str(event.get("hook_event_name") or "Notification")
        asyncio.create_task(asyncio.to_thread(audit, {"event": "Notification", "title": title, "message": message[:300]}))

        try:
            from dbus.notifier import DbusNotifier

            notifier = DbusNotifier()
            await notifier.notify(title=title, body=message)
        except Exception:
            pass
    except Exception as exc:
        audit({"event": "HookError", "hook": "_notification_hook", "error": str(exc)})
    return {}


def build_python_hooks() -> dict[str, list[HookMatcher]]:
    """Return SDK hook matcher registry for Python-available hook events."""
    return {
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit|Bash", hooks=[_pre_tool_write_guard]),
            HookMatcher(matcher=".*", hooks=[_pre_tool_audit]),
        ],
        "PostToolUse": [HookMatcher(matcher=".*", hooks=[_post_tool_audit])],
        "PostToolUseFailure": [HookMatcher(matcher=".*", hooks=[_post_tool_failure_audit])],
        "UserPromptSubmit": [HookMatcher(matcher=".*", hooks=[_user_prompt_context])],
        "Stop": [HookMatcher(matcher=".*", hooks=[_stop_snapshot])],
        "SubagentStart": [HookMatcher(matcher=".*", hooks=[_subagent_start])],
        "SubagentStop": [HookMatcher(matcher=".*", hooks=[_subagent_stop])],
        "PreCompact": [HookMatcher(matcher=".*", hooks=[_pre_compact])],
        "PermissionRequest": [
            HookMatcher(matcher="Read|Grep|Glob", hooks=[_permission_auto_allow]),
            HookMatcher(matcher=".*", hooks=[_permission_default_ask]),
        ],
        "Notification": [HookMatcher(matcher=".*", hooks=[_notification_hook])],
    }
