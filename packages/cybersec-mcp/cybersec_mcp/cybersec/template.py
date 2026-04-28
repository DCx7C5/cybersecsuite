"""Template rendering MCP tools."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ..sdk_compat import tool
from ..helpers import JsonDict, sdk_result, sdk_error


def _render_template_string(source: str, ctx: dict) -> str:
    """Render {{ var }} placeholders using regex substitution."""
    def replace(m):
        key = m.group(1).strip()
        return str(ctx.get(key, ""))
    return re.sub(r'\{\{\s*(\w+)\s*\}\}', replace, source)


def _resolve_template(name: str) -> Path | None:
    """Find template file across session → project → app → global scopes."""
    from cybersecsuite.session_scope import project_sessions_dir, legacy_project_sessions_dir

    project_dir = Path.cwd()
    global_dir = Path("~/.claude").expanduser()
    app_dir = Path("~/.cybersecsuite").expanduser()

    sessions_dir = project_sessions_dir(project_dir)
    legacy_sessions_dir = legacy_project_sessions_dir(project_dir)

    sid = os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    session_dirs: list[Path] = []
    if sid:
        primary = sessions_dir / sid / "templates"
        legacy = legacy_sessions_dir / sid / "templates"
        if primary.exists():
            session_dirs.append(primary)
        if legacy.exists() and legacy != primary:
            session_dirs.append(legacy)
    else:
        latest = sessions_dir / "latest" / "templates"
        if latest.is_symlink() or latest.is_dir():
            session_dirs.append(latest)

    search_dirs: list[Path] = session_dirs + [
        project_dir / ".claude" / "templates",
        app_dir / "templates",
        global_dir / "templates",
    ]

    for d in search_dirs:
        candidate = (d / name).resolve()
        # Security: ensure resolved path stays within the search dir
        try:
            candidate.relative_to(d.resolve())
        except ValueError:
            continue
        if candidate.exists():
            return candidate
    return None


@tool(
    "render_template",
    "Render a template with extra variables",
    {
        "name": "string",
        "extra_vars": {"type": "object", "description": "Additional template variables"},
    },
)
async def render_template(args: dict[str, Any]) -> JsonDict:
    """Render a named template from the scope-aware template search path."""
    name = args.get("name", "")
    if not name:
        return sdk_error("name is required")

    # Security: reject path traversal attempts
    if ".." in name or name.startswith("/"):
        return sdk_error("invalid template name")

    extra_vars = args.get("extra_vars", {})
    try:
        path = _resolve_template(name)
        if path is not None:
            source = path.read_text(encoding="utf-8")
        else:
            from cybersecsuite.scaffold import get_embedded_template
            source = get_embedded_template(name)
            if source is None:
                return sdk_error(f"Template '{name}' not found")
        rendered = _render_template_string(source, extra_vars)
        return sdk_result({"name": name, "rendered": rendered})
    except Exception as e:
        return sdk_error(str(e))


ALL_TOOLS = [render_template]