"""Settings toggle API: MCPs, skill domains, plugins, global ~/.claude settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_SETTINGS_PATH = _PROJECT_ROOT / ".claude" / "settings.json"
_MCP_PATH = _PROJECT_ROOT / "mcp.json"
_SKILLS_DIR = _PROJECT_ROOT / ".claude" / "skills"

# GLOBAL_CLAUDE_DIR env var lets Docker override the global ~/.claude path
# (container mounts host ~/.claude at /app/.claude-global via docker-compose volume)
_GLOBAL_CLAUDE_DIR = Path(os.environ.get("GLOBAL_CLAUDE_DIR", str(Path.home() / ".claude")))
_GLOBAL_SETTINGS_PATH = _GLOBAL_CLAUDE_DIR / "settings.json"
_GLOBAL_PLUGINS_PATH = _GLOBAL_CLAUDE_DIR / "plugins" / "installed_plugins.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _dump_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def _project_settings() -> dict:
    return _load_json(_SETTINGS_PATH)


def _save_project_settings(data: dict) -> None:
    _dump_json(_SETTINGS_PATH, data)


# ── MCP Servers ──────────────────────────────────────────────────────────────

async def api_settings_mcps_get(request: Request) -> JSONResponse:
    """List all MCP servers from mcp.json with enabled state."""
    try:
        mcp_data = _load_json(_MCP_PATH)
        settings = _project_settings()
        # enabledMcps is stored as list of enabled server names; if absent, all are enabled
        enabled_list = settings.get("enabledMcps", None)
        servers = []
        for name, cfg in mcp_data.get("mcpServers", {}).items():
            enabled = (enabled_list is None) or (name in enabled_list)
            servers.append({
                "name": name,
                "command": cfg.get("command", ""),
                "enabled": enabled,
            })
        return JSONResponse({"servers": servers})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_mcps_patch(request: Request) -> JSONResponse:
    """Toggle MCP server enabled state. Body: {"name": str, "enabled": bool}"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    name = body.get("name")
    enabled = body.get("enabled")
    if not name or enabled is None:
        return JSONResponse({"error": "name and enabled required"}, status_code=400)

    try:
        mcp_data = _load_json(_MCP_PATH)
        all_names = list(mcp_data.get("mcpServers", {}).keys())
        settings = _project_settings()
        # Initialize from all names if not set (all enabled by default)
        enabled_list = settings.get("enabledMcps", list(all_names))
        if enabled:
            if name not in enabled_list:
                enabled_list.append(name)
        else:
            enabled_list = [n for n in enabled_list if n != name]
        settings["enabledMcps"] = enabled_list
        _save_project_settings(settings)
        return JSONResponse({"ok": True, "name": name, "enabled": enabled})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Skill Domains ─────────────────────────────────────────────────────────────

def _get_skill_domains() -> list[str]:
    """Return top-level skill domain directories."""
    if not _SKILLS_DIR.exists():
        return []
    return sorted(
        d.name for d in _SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


async def api_settings_skills_get(request: Request) -> JSONResponse:
    """List skill domains with enabled state."""
    try:
        domains = _get_skill_domains()
        settings = _project_settings()
        # If not set, all domains are enabled
        enabled_domains = settings.get("enabledSkillDomains", None)
        result = []
        for d in domains:
            enabled = (enabled_domains is None) or (d in enabled_domains)
            # Count skills in domain
            domain_path = _SKILLS_DIR / d
            skill_count = sum(1 for f in domain_path.rglob("*.md") if f.is_file())
            result.append({"name": d, "enabled": enabled, "skills": skill_count})
        return JSONResponse({"domains": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_skills_patch(request: Request) -> JSONResponse:
    """Toggle skill domain. Body: {"name": str, "enabled": bool}"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    name = body.get("name")
    enabled = body.get("enabled")
    if not name or enabled is None:
        return JSONResponse({"error": "name and enabled required"}, status_code=400)

    try:
        domains = _get_skill_domains()
        settings = _project_settings()
        enabled_domains = settings.get("enabledSkillDomains", list(domains))
        if enabled:
            if name not in enabled_domains:
                enabled_domains.append(name)
        else:
            enabled_domains = [d for d in enabled_domains if d != name]
        settings["enabledSkillDomains"] = sorted(enabled_domains)
        _save_project_settings(settings)
        return JSONResponse({"ok": True, "name": name, "enabled": enabled})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Plugins (global ~/.claude/settings.json enabledPlugins) ──────────────────

async def api_settings_plugins_get(request: Request) -> JSONResponse:
    """List installed plugins with enabled state from global ~/.claude."""
    try:
        plugins_data = _load_json(_GLOBAL_PLUGINS_PATH)
        global_settings = _load_json(_GLOBAL_SETTINGS_PATH)
        enabled_plugins = global_settings.get("enabledPlugins", {})

        plugins = []
        for plugin_id, installs in plugins_data.get("plugins", {}).items():
            # installs is a list of install records
            install = installs[0] if installs else {}
            enabled = enabled_plugins.get(plugin_id, True)
            plugins.append({
                "id": plugin_id,
                "version": install.get("version", "?"),
                "scope": install.get("scope", "?"),
                "enabled": bool(enabled),
            })
        return JSONResponse({"plugins": plugins})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_plugins_patch(request: Request) -> JSONResponse:
    """Toggle plugin. Body: {"id": str, "enabled": bool}"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    plugin_id = body.get("id")
    enabled = body.get("enabled")
    if not plugin_id or enabled is None:
        return JSONResponse({"error": "id and enabled required"}, status_code=400)

    try:
        global_settings = _load_json(_GLOBAL_SETTINGS_PATH)
        enabled_plugins = global_settings.get("enabledPlugins", {})
        enabled_plugins[plugin_id] = bool(enabled)
        global_settings["enabledPlugins"] = enabled_plugins
        _dump_json(_GLOBAL_SETTINGS_PATH, global_settings)
        return JSONResponse({"ok": True, "id": plugin_id, "enabled": enabled})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Global ~/.claude MCP Servers ─────────────────────────────────────────────

async def api_settings_global_mcps_get(request: Request) -> JSONResponse:
    """List MCP servers from global ~/.claude/settings.json with enabled state."""
    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        enabled_list = data.get("enabledGlobalMcps", None)  # None = all enabled
        servers = []
        for name, cfg in data.get("mcpServers", {}).items():
            enabled = (enabled_list is None) or (name in enabled_list)
            servers.append({
                "name": name,
                "command": cfg.get("command", ""),
                "enabled": enabled,
            })
        return JSONResponse({"servers": servers})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_global_mcps_patch(request: Request) -> JSONResponse:
    """Toggle global MCP server. Body: {"name": str, "enabled": bool}"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    name = body.get("name")
    enabled = body.get("enabled")
    if not name or enabled is None:
        return JSONResponse({"error": "name and enabled required"}, status_code=400)

    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        all_names = list(data.get("mcpServers", {}).keys())
        enabled_list = data.get("enabledGlobalMcps", list(all_names))
        if enabled:
            if name not in enabled_list:
                enabled_list.append(name)
        else:
            enabled_list = [n for n in enabled_list if n != name]
        data["enabledGlobalMcps"] = enabled_list
        _dump_json(_GLOBAL_SETTINGS_PATH, data)
        return JSONResponse({"ok": True, "name": name, "enabled": enabled})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Env vars (read-only views) ────────────────────────────────────────────────

async def api_settings_global_env_get(request: Request) -> JSONResponse:
    """Return global ~/.claude env vars (values masked for security)."""
    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        env = data.get("env", {})
        _SAFE_KEYS = {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
                      "NODE_EXTRA_CA_CERTS", "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS_MAX_AGENTS"}
        result = {k: (v if k in _SAFE_KEYS else "•••") for k, v in env.items()}
        return JSONResponse({"env": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_project_env_get(request: Request) -> JSONResponse:
    """Return project .claude env vars."""
    try:
        data = _load_json(_SETTINGS_PATH)
        env = data.get("env", {})
        return JSONResponse({"env": env})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Global ~/.claude/settings.json summary view ───────────────────────────────

async def api_settings_global_get(request: Request) -> JSONResponse:
    """Return full global ~/.claude settings summary."""
    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        summary = {
            "effortLevel": data.get("effortLevel", ""),
            "codemossProviderId": data.get("codemossProviderId", ""),
            "enabledPlugins": data.get("enabledPlugins", {}),
            "mcpServers": list(data.get("mcpServers", {}).keys()),
            "extraKnownMarketplaces": list(data.get("extraKnownMarketplaces", {}).keys()),
            "hooks": list(data.get("hooks", {}).keys()),
        }
        return JSONResponse({"global": summary})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── MCP Installer ─────────────────────────────────────────────────────────────

async def api_settings_install_mcp(request: Request) -> JSONResponse:
    """Install a new MCP server into ~/.claude/settings.json.
    Body: {"name": str, "command": str, "args": list[str], "env": dict[str,str]}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    name = (body.get("name") or "").strip()
    command = (body.get("command") or "").strip()
    args = body.get("args", [])
    env = body.get("env", {})

    if not name or not command:
        return JSONResponse({"error": "name and command are required"}, status_code=400)

    # Validate: no shell injection — command must be a bare executable name or path
    import re as _re
    if _re.search(r'[;&|`$<>]', command):
        return JSONResponse({"error": "invalid characters in command"}, status_code=400)

    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        mcp_servers = data.get("mcpServers", {})
        if name in mcp_servers:
            return JSONResponse({"error": f"MCP server '{name}' already exists. Use update instead."}, status_code=409)
        entry: dict = {"command": command, "args": args}
        if env:
            entry["env"] = env
        mcp_servers[name] = entry
        data["mcpServers"] = mcp_servers
        _dump_json(_GLOBAL_SETTINGS_PATH, data)
        return JSONResponse({"ok": True, "name": name, "entry": entry})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_remove_mcp(request: Request) -> JSONResponse:
    """Remove a global MCP server from ~/.claude/settings.json.
    Body: {"name": str}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse({"error": "name required"}, status_code=400)

    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        mcp_servers = data.get("mcpServers", {})
        if name not in mcp_servers:
            return JSONResponse({"error": f"MCP server '{name}' not found"}, status_code=404)
        del mcp_servers[name]
        data["mcpServers"] = mcp_servers
        _dump_json(_GLOBAL_SETTINGS_PATH, data)
        return JSONResponse({"ok": True, "removed": name})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Hooks Manager ─────────────────────────────────────────────────────────────

_VALID_HOOK_EVENTS = {
    "PreToolUse", "PostToolUse", "Stop", "SessionStart", "UserPromptSubmit",
    "SubagentStart", "SubagentStop", "TeammateIdle", "PreCompact", "PostCompact",
    "Notification",
}


async def api_settings_hooks_get(request: Request) -> JSONResponse:
    """List all hooks from ~/.claude/settings.json."""
    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        hooks = data.get("hooks", {})
        result = {}
        for event, entries in hooks.items():
            result[event] = []
            for entry in entries:
                for hook in entry.get("hooks", []):
                    result[event].append({
                        "command": hook.get("command", ""),
                        "matcher": entry.get("matcher", ""),
                        "type": hook.get("type", "command"),
                    })
        return JSONResponse({"hooks": result, "valid_events": sorted(_VALID_HOOK_EVENTS)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_hooks_post(request: Request) -> JSONResponse:
    """Add a hook to ~/.claude/settings.json.
    Body: {"event": str, "command": str, "matcher": str (optional)}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    event = (body.get("event") or "").strip()
    command = (body.get("command") or "").strip()
    matcher = (body.get("matcher") or "").strip()

    if event not in _VALID_HOOK_EVENTS:
        return JSONResponse({"error": f"Invalid event. Must be one of: {sorted(_VALID_HOOK_EVENTS)}"}, status_code=400)
    if not command:
        return JSONResponse({"error": "command is required"}, status_code=400)

    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        hooks = data.get("hooks", {})
        event_list = hooks.get(event, [])
        new_entry: dict = {"hooks": [{"type": "command", "command": command}]}
        if matcher:
            new_entry["matcher"] = matcher
        event_list.append(new_entry)
        hooks[event] = event_list
        data["hooks"] = hooks
        _dump_json(_GLOBAL_SETTINGS_PATH, data)
        return JSONResponse({"ok": True, "event": event, "command": command})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_hooks_delete(request: Request) -> JSONResponse:
    """Remove a hook by event + command match.
    Body: {"event": str, "command": str}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    event = (body.get("event") or "").strip()
    command = (body.get("command") or "").strip()

    if not event or not command:
        return JSONResponse({"error": "event and command required"}, status_code=400)

    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        hooks = data.get("hooks", {})
        event_list = hooks.get(event, [])
        # Remove entries whose hooks list contains the matching command
        filtered = [
            e for e in event_list
            if not any(h.get("command") == command for h in e.get("hooks", []))
        ]
        hooks[event] = filtered
        data["hooks"] = hooks
        _dump_json(_GLOBAL_SETTINGS_PATH, data)
        return JSONResponse({"ok": True, "event": event, "removed_command": command})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Agent Templates ───────────────────────────────────────────────────────────
_CLAUDE_DIR = _PROJECT_ROOT / ".claude"
_AGENTS_TEMPLATES_DIR = _CLAUDE_DIR / "agents" / "agents"


async def api_settings_agent_templates(request: Request) -> JSONResponse:
    """GET /api/settings/agent-agents — list template .md files in .claude/agents/agents/."""
    try:
        if not _AGENTS_TEMPLATES_DIR.exists():
            return JSONResponse({"agents": []})
        files = sorted(p.stem for p in _AGENTS_TEMPLATES_DIR.glob("*.md"))
        return JSONResponse({"agents": files})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
