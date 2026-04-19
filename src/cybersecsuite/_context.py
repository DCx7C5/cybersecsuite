"""Thin context wrapper — avoids circular imports between sdk.py and template_engine."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from template_engine.context import get_context as _get_context


def get_context(
    project_dir: Path | None = None,
    session_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _get_context(project_dir=project_dir, session_id=session_id, extra=extra)
