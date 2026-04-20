"""Vault & Canvas status API endpoint."""
from __future__ import annotations

import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

_VAULT_PATH = os.getenv(
    "CYBERSEC_VAULT_PATH",
    str(Path.home() / ".cybersecsuite" / "data" / "vault"),
)


def _count_files(directory: Path, suffix: str = ".md") -> int:
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.rglob(f"*{suffix}") if _.is_file())


def _hot_cache_summary(vault: Path) -> dict:
    hot = vault / "wiki" / "hot.md"
    if not hot.exists():
        return {"exists": False, "words": 0, "last_updated": None}
    text = hot.read_text(encoding="utf-8", errors="replace")
    words = len(text.split())
    import datetime
    mtime = datetime.datetime.fromtimestamp(hot.stat().st_mtime).isoformat()
    return {"exists": True, "words": words, "last_updated": mtime}


def _recent_memories(vault: Path, limit: int = 5) -> list[dict]:
    mem_root = vault / "memories"
    if not mem_root.exists():
        return []
    files = sorted(
        mem_root.rglob("*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )[:limit]
    results = []
    for f in files:
        results.append({
            "id": f.stem,
            "type": f.parent.name,
            "path": str(f.relative_to(vault)),
        })
    return results


def _canvas_list(vault: Path) -> list[str]:
    canvas_dir = vault / "wiki" / "canvases"
    if not canvas_dir.exists():
        return []
    return [f.name for f in sorted(canvas_dir.glob("*.canvas"), key=lambda f: f.stat().st_mtime, reverse=True)]


async def api_vault_status(request: Request) -> JSONResponse:
    """GET /api/vault/status — vault and canvas health snapshot."""
    vault = Path(_VAULT_PATH).resolve()
    exists = vault.exists()

    if not exists:
        return JSONResponse({
            "vault_path": str(vault),
            "exists": False,
            "memories": {"total": 0, "by_type": {}},
            "wiki": {"total": 0},
            "canvases": [],
            "hot_cache": {"exists": False, "words": 0, "last_updated": None},
            "recent_memories": [],
        })

    mem_root = vault / "memories"
    by_type: dict[str, int] = {}
    if mem_root.exists():
        for d in mem_root.iterdir():
            if d.is_dir():
                by_type[d.name] = _count_files(d)

    return JSONResponse({
        "vault_path": str(vault),
        "exists": True,
        "memories": {
            "total": sum(by_type.values()),
            "by_type": by_type,
        },
        "wiki": {
            "total": _count_files(vault / "wiki"),
            "entities": _count_files(vault / "wiki" / "entities"),
            "iocs": _count_files(vault / "wiki" / "iocs"),
            "ttps": _count_files(vault / "wiki" / "ttps"),
            "cases": _count_files(vault / "wiki" / "cases"),
            "findings": _count_files(vault / "wiki" / "findings"),
        },
        "canvases": _canvas_list(vault),
        "hot_cache": _hot_cache_summary(vault),
        "recent_memories": _recent_memories(vault),
    })
