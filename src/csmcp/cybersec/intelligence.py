"""MITRE suggestion and project memory tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import (
    JsonDict, _get_current_scope, get_workspace_dir, get_project_dir,
    get_session_dir, sdk_result, sdk_error,
)


_KEYWORDS_TO_MITRE: dict[str, list[str]] = {
    "screenshot": ["T1113 - Screen Capture"],
    "keylog": ["T1056.001 - Keylogging"],
    "browser": ["T1555.003 - Web Browsers", "T1539 - Steal Web Session Cookie"],
    "cookie": ["T1539 - Steal Web Session Cookie"],
    "arp": ["T1557.002 - ARP Cache Poisoning"],
    "network": ["T1040 - Network Sniffing", "T1557 - Man-in-the-Middle"],
    "persistence": ["T1547 - Boot or Logon Autostart Execution"],
    "log": ["T1070.002 - Clear Windows Event Logs", "T1562.002 - Disable Windows Event Logging"],
    "injection": ["T1055 - Process Injection"],
    "c2": ["T1071 - Application Layer Protocol", "T1573 - Encrypted Channel"],
    "scheduled task": ["T1053.005 - Scheduled Task", "T1053 - Scheduled Task/Job"],
    "download": ["T1105 - Ingress Tool Transfer", "T1071.001 - Web Protocols"],
    "payload": ["T1105 - Ingress Tool Transfer", "T1204 - User Execution"],
    "task": ["T1053.005 - Scheduled Task", "T1053 - Scheduled Task/Job"],
    "cron": ["T1053.003 - Cron", "T1053 - Scheduled Task/Job"],
}


@tool(
    "suggest_mitre",
    "Suggest MITRE ATT&CK techniques based on a description of observed behaviour.",
    {
        "description": "string",
        "category": {"type": "string", "default": ""},
    },
)
def suggest_mitre(args: dict[str, Any]) -> JsonDict:
    description = args.get("description", "")
    category = args.get("category", "")
    suggestions: list[str] = []
    matched: list[str] = []
    seen: set[str] = set()
    desc_lower = description.lower()

    for keyword, techniques in _KEYWORDS_TO_MITRE.items():
        if keyword in desc_lower:
            matched.append(keyword)
            for t in techniques:
                if t not in seen:
                    seen.add(t)
                    suggestions.append(t)

    return sdk_result({
        "status": "success",
        "description": description,
        "suggested_techniques": suggestions,
        "matched_keywords": matched,
        "category": category,
    })


@tool(
    "get_project_memory",
    "Return project memory: findings, recent entries and IOCs from the current scope.",
    {"query": {"type": "string", "default": ""}},
)
async def get_project_memory(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import get_recent_entries_async, get_scoped_entries_async, ScopeContext
    except ImportError:
        return sdk_error("hooks.database not available")

    scope = _get_current_scope()
    session_dir = get_session_dir(scope)
    findings_file = get_project_dir(scope) / "findings.md"

    memory_data: JsonDict = {
        "findings": findings_file.read_text(encoding="utf-8") if findings_file.exists() else "",
        "scope": scope,
        "workspace_dir": str(get_workspace_dir(scope)),
        "project_dir": str(get_project_dir(scope)),
        "session_dir": str(session_dir) if session_dir else None,
    }

    sc = ScopeContext(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
    )
    memory_data["recent_entries"] = await get_recent_entries_async(sc, limit=20)
    memory_data["recent_iocs"] = await get_scoped_entries_async(
        workspace_name=scope["workspace"], project_name=scope["project"],
        session_id=scope["session"], value_type="ioc", limit=10,
    )

    return sdk_result({"status": "success", "memory": memory_data, "query": args.get("query", "")})


ALL_TOOLS = [suggest_mitre, get_project_memory]
