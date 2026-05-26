"""Source tree analyzer for planner bootstrap context."""

from __future__ import annotations

from pathlib import Path


class ArchitectureAnalyzer:
    """Collects quick architecture facts from src/ for planning."""

    def __init__(self, source_root: Path | None = None):
        self.source_root = (source_root or Path.cwd() / "src").resolve()

    def summarize(self) -> dict:
        py_files = list(self.source_root.rglob("*.py"))
        module_dirs = [p for p in self.source_root.iterdir() if p.is_dir()] if self.source_root.exists() else []
        return {
            "source_root": str(self.source_root),
            "python_file_count": len(py_files),
            "top_level_modules": sorted(p.name for p in module_dirs),
        }
