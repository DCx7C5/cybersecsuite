"""Scoped workspace management for agent sessions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class WorkingDirectory:
    """Represents a scoped working directory for one session."""

    session_id: str
    agent_id: str
    mode: str
    root: Path
    findings_dir: Path
    artifacts_dir: Path
    notes_dir: Path
    scratch_dir: Path


class WorkingDirectoryManager:
    """Creates and resolves agent-scoped working directories."""

    def __init__(self, base_path: Path | None = None):
        self.base_path = (base_path or Path.cwd() / ".css" / "sessions").resolve()

    def create(self, session_id: str, agent_id: str, mode: str = "default") -> WorkingDirectory:
        session_root = (self.base_path / session_id / agent_id).resolve()
        findings = session_root / "findings"
        artifacts = session_root / "artifacts"
        notes = session_root / "notes"
        scratch = session_root / "scratch"

        for path in (session_root, findings, artifacts, notes, scratch):
            path.mkdir(parents=True, exist_ok=True)

        if mode == "planner":
            plan_file = session_root / "plan.md"
            if not plan_file.exists():
                plan_file.write_text("# Plan\n\n## Objective\n\n## Steps\n", encoding="utf-8")

        return WorkingDirectory(
            session_id=session_id,
            agent_id=agent_id,
            mode=mode,
            root=session_root,
            findings_dir=findings,
            artifacts_dir=artifacts,
            notes_dir=notes,
            scratch_dir=scratch,
        )

    def get(self, session_id: str, agent_id: str, mode: str = "default") -> WorkingDirectory:
        session_root = (self.base_path / session_id / agent_id).resolve()
        if not session_root.exists():
            return self.create(session_id=session_id, agent_id=agent_id, mode=mode)
        return WorkingDirectory(
            session_id=session_id,
            agent_id=agent_id,
            mode=mode,
            root=session_root,
            findings_dir=session_root / "findings",
            artifacts_dir=session_root / "artifacts",
            notes_dir=session_root / "notes",
            scratch_dir=session_root / "scratch",
        )


class FileManager:
    """Scoped file read/write/delete with path traversal protection."""

    def __init__(self, working_directory: WorkingDirectory):
        self.working_directory = working_directory
        self.root = working_directory.root.resolve()

    def resolve_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"Path escapes working directory: {relative_path}")
        return candidate

    def write_text(self, relative_path: str, content: str) -> Path:
        path = self.resolve_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_text(self, relative_path: str) -> str:
        path = self.resolve_path(relative_path)
        return path.read_text(encoding="utf-8")

    def delete_file(self, relative_path: str) -> bool:
        path = self.resolve_path(relative_path)
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False

    def list_files(self, relative_dir: str = ".", suffixes: Iterable[str] | None = None) -> list[str]:
        target = self.resolve_path(relative_dir)
        if not target.exists():
            return []

        wanted = tuple(suffixes) if suffixes else None
        paths: list[str] = []
        for item in target.rglob("*"):
            if not item.is_file():
                continue
            if wanted and item.suffix not in wanted:
                continue
            paths.append(str(item.relative_to(self.root)))
        return sorted(paths)
