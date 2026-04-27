"""First-run scaffold: copy embedded templates to the project's .claude/templates/ directory.

Usage (standalone):
    python -m cybersecsuite.scaffold [project_dir]
"""
from __future__ import annotations

import importlib.resources as _res
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_PKG = "cybersecsuite.data.templates"


def _embedded_templates() -> list[tuple[str, bytes]]:
    """Return list of (relative_path, content) for all embedded templates."""
    results: list[tuple[str, bytes]] = []

    def _walk(node, prefix: str = "") -> None:
        for entry in node.iterdir():
            name = entry.name
            # Skip Python internals (__init__.py, __pycache__, etc.)
            if name.startswith("__"):
                continue
            rel = f"{prefix}{name}" if prefix else name
            try:
                # Try directory
                list(entry.iterdir())
                _walk(entry, f"{rel}/")
            except (NotADirectoryError, TypeError):
                # It's a file
                try:
                    results.append((rel, entry.read_bytes()))
                except Exception as exc:
                    logger.warning("scaffold: could not read embedded template %r: %s", rel, exc)

    try:
        root = _res.files(_DATA_PKG)
        _walk(root)
    except (ModuleNotFoundError, TypeError):
        pass
    return results


def scaffold_project_templates(project_dir: Path | None = None) -> int:
    """Copy each missing embedded template into <project_dir>/.claude/templates/.

    Never overwrites existing files. Returns number of files copied.
    """
    project_dir = Path(project_dir) if project_dir else Path.cwd()
    target_root = project_dir / ".claude" / "templates"

    copied = 0
    for rel_path, content in _embedded_templates():
        dest = target_root / rel_path
        if dest.exists():
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            copied += 1
            logger.debug("scaffold: wrote %s", dest)
        except OSError as exc:
            logger.warning("scaffold: could not write %s: %s", dest, exc)

    if copied:
        logger.info("scaffold: copied %d template(s) to %s", copied, target_root)
    return copied


def get_embedded_template(name: str) -> str | None:
    """Return embedded template content by relative name (e.g. 'artifact.md').

    Returns None if not found.
    """
    try:
        parts = name.replace("\\", "/").split("/")
        ref = _res.files(_DATA_PKG)
        for part in parts:
            ref = ref.joinpath(part)
        return ref.read_text(encoding="utf-8")
    except Exception:
        return None


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    n = scaffold_project_templates(d)
    print(f"Scaffolded {n} template(s).")
