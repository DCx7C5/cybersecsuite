"""Template registry API: scan templates/ and expose indexed metadata."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TEMPLATES_DIR = _REPO_ROOT / "templates"
_INDEX_TYPES = ("agents", "skills", "hooks", "mcp", "other")


def _parse_scalar(value: str) -> Any:
    raw = value.strip()
    if raw == "":
        return ""
    if raw.lower() in {"true", "yes"}:
        return True
    if raw.lower() in {"false", "no"}:
        return False
    if raw.isdigit():
        try:
            return int(raw)
        except ValueError:
            pass
    return raw.strip('"').strip("'")


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse a simple YAML frontmatter block using stdlib only."""
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        return {}

    result: dict[str, Any] = {}
    current_list_key: str | None = None

    for line in match.group(1).splitlines():
        if not line.strip():
            continue

        stripped = line.lstrip()
        if current_list_key and (stripped.startswith("- ") or line.startswith("  - ")):
            result[current_list_key].append(_parse_scalar(stripped[2:]))
            continue

        current_list_key = None
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if value == "":
            result[key] = []
            current_list_key = key
            continue

        result[key] = _parse_scalar(value)

    return result


def _classify_type(rel_path: Path) -> str:
    if not rel_path.parts:
        return "other"
    first = rel_path.parts[0].lower()
    if first in {"agents", "skills", "hooks", "mcp"}:
        return first
    return "other"


def build_template_index() -> dict[str, list[dict[str, Any]]]:
    """Build template index from project templates/ directory."""
    index: dict[str, list[dict[str, Any]]] = {k: [] for k in _INDEX_TYPES}
    if not _TEMPLATES_DIR.exists():
        return index

    for path in sorted(_TEMPLATES_DIR.rglob("*")):
        if not path.is_file():
            continue

        rel_path = path.relative_to(_TEMPLATES_DIR)
        item_type = _classify_type(rel_path)
        frontmatter: dict[str, Any] = {}
        description = ""

        if path.suffix.lower() == ".md":
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                text = ""
            frontmatter = _parse_frontmatter(text)
            desc = frontmatter.get("description")
            description = desc if isinstance(desc, str) else ""

        name = path.stem if path.suffix else path.name
        index[item_type].append(
            {
                "name": name,
                "path": str(Path("templates") / rel_path),
                "type": item_type,
                "scope": "project",
                "description": description,
                "frontmatter": frontmatter,
            }
        )

    return index


def _filter_items(items: list[dict[str, Any]], search: str) -> list[dict[str, Any]]:
    if not search:
        return items
    q = search.casefold()
    out: list[dict[str, Any]] = []
    for item in items:
        name = str(item.get("name", ""))
        desc = str(item.get("description", ""))
        if q in name.casefold() or q in desc.casefold():
            out.append(item)
    return out


async def api_template_registry_list(request: Request) -> JSONResponse:
    """GET /api/templates — list templates with optional type/search filters."""
    template_type = request.query_params.get("type", "").strip().lower()
    search = request.query_params.get("search", "").strip()

    index = build_template_index()

    if template_type:
        items = _filter_items(index.get(template_type, []), search)
        return JSONResponse({template_type: items})

    if search:
        filtered = {k: _filter_items(v, search) for k, v in index.items()}
        return JSONResponse(filtered)

    return JSONResponse(index)


async def api_template_create(request: Request) -> JSONResponse:
    """POST /api/templates — instantiate a template to .claude/."""
    body = await request.json()
    template_type = body.get("type", "")
    template_id = body.get("id", "")
    target_path = body.get("target", "")

    if not template_type or not template_id:
        return JSONResponse({"error": "type and id required"}, status=400)

    index = build_template_index()
    templates = index.get(template_type, [])
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        return JSONResponse({"error": "template not found"}, status=404)

    source_path = Path(template.get("path", ""))
    if not source_path.exists():
        return JSONResponse({"error": "template file not found"}, status=404)

    claude_dir = _REPO_ROOT / ".claude"
    if target_path:
        dest = Path(target_path)
    else:
        dest = claude_dir / template_type / source_path.name

    dest.parent.mkdir(parents=True, exist_ok=True)

    import shutil
    shutil.copy2(source_path, dest)

    return JSONResponse({"created": str(dest)})


async def api_template_delete(request: Request) -> JSONResponse:
    """DELETE /api/templates/{type}/{id} — remove a custom template."""
    template_type = request.query_params.get("type", "")
    template_id = request.path_params.get("id", "")

    if not template_type or not template_id:
        return JSONResponse({"error": "type and id required"}, status=400)

    index = build_template_index()
    templates = index.get(template_type, [])
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        return JSONResponse({"error": "template not found"}, status=404)

    template_path = Path(template.get("path", ""))
    if template_path.exists() and ".claude" in str(template_path):
        template_path.unlink()
        return JSONResponse({"deleted": str(template_path)})

    return JSONResponse({"error": "cannot delete non-custom template"}, status=400)


async def api_template_update(request: Request) -> JSONResponse:
    """PATCH /api/templates/{id} — update a custom template's content."""
    template_id = request.path_params.get("id", "")
    template_type = request.query_params.get("type", "")

    if not template_id:
        return JSONResponse({"error": "id required"}, status_code=400)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    index = build_template_index()
    templates = index.get(template_type, []) if template_type else [
        t for tl in index.values() for t in tl
    ]
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        return JSONResponse({"error": "template not found"}, status_code=404)

    template_path = Path(template.get("path", ""))
    if not template_path.exists() or ".claude" not in str(template_path):
        return JSONResponse({"error": "cannot edit non-custom template"}, status_code=400)

    if "content" in body:
        template_path.write_text(body["content"], encoding="utf-8")

    return JSONResponse({"ok": True, "id": template_id})
