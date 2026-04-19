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


# ── Global ~/.claude/settings.json view ──────────────────────────────────────

async def api_settings_global_get(request: Request) -> JSONResponse:
    """Return a summary of key global ~/.claude settings."""
    try:
        data = _load_json(_GLOBAL_SETTINGS_PATH)
        # Return safe summary — exclude sensitive env values
        summary = {
            "effortLevel": data.get("effortLevel", ""),
            "codemossProviderId": data.get("codemossProviderId", ""),
            "enabledPlugins": data.get("enabledPlugins", {}),
            "mcpServers": list(data.get("mcpServers", {}).keys()),
            "extraKnownMarketplaces": list(data.get("extraKnownMarketplaces", {}).keys()),
        }
        return JSONResponse({"global": summary})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
