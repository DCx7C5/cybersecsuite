"""
ObsidianMemoryBackend — Anthropic SDK memory_20250818 tool backed by an Obsidian vault.

Maps the SDK's /memories/* path contract to Obsidian-flavored Markdown files
inside a vault's wiki/ directory, enabling Claude's native memory tool to persist
knowledge as properly-formatted Obsidian notes with YAML frontmatter and wikilinks.

Path mapping:
  /memories/           →  vault/memories/       (flat memory files)
  /memories/entities/  →  vault/wiki/entities/   (threat actors, malware, orgs)
  /memories/iocs/      →  vault/wiki/iocs/       (indicators of compromise)
  /memories/ttps/      →  vault/wiki/ttps/       (MITRE techniques)
  /memories/cases/     →  vault/wiki/cases/      (investigation cases)
  /memories/findings/  →  vault/wiki/findings/   (analyst findings)
  /memories/hot        →  vault/wiki/hot.md      (hot cache — session context)
  /memories/index      →  vault/wiki/index.md    (master catalog)
"""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from anthropic.lib.tools._beta_builtin_memory_tool import (
    BetaAbstractMemoryTool,
    _DIR_CREATE_MODE,
    _atomic_write_file,
    _read_file_content,
    _validate_no_symlink_escape,
    MAX_LINES,
    LINE_NUMBER_WIDTH,
    _format_file_size,
    ToolError,
)
from anthropic.types.beta import (
    BetaMemoryTool20250818ViewCommand,
    BetaMemoryTool20250818CreateCommand,
    BetaMemoryTool20250818DeleteCommand,
    BetaMemoryTool20250818InsertCommand,
    BetaMemoryTool20250818RenameCommand,
    BetaMemoryTool20250818StrReplaceCommand,
)
from typing_extensions import override

_DEFAULT_VAULT_PATH = str(
    Path(os.environ.get("CYBERSECSUITE_HOME", str(Path.home() / ".cybersecsuite"))).expanduser()
    / "vault"
)

# Vault-level path aliases — /memories/<alias> → wiki/<target>
_VAULT_ALIASES: dict[str, str] = {
    "entities": "wiki/entities",
    "iocs": "wiki/iocs",
    "ttps": "wiki/ttps",
    "cases": "wiki/cases",
    "findings": "wiki/findings",
    "concepts": "wiki/concepts",
    "hot": "wiki/hot.md",
    "index": "wiki/index.md",
    "log": "wiki/log.md",
    "overview": "wiki/overview.md",
}


class ObsidianMemoryBackend(BetaAbstractMemoryTool):
    """
    Sync Anthropic memory tool backed by an Obsidian vault.

    Memory files are Obsidian-flavored Markdown with YAML frontmatter.
    Vault aliases map common /memories/* paths directly to wiki/ subdirs.

    Usage:
        backend = ObsidianMemoryBackend(vault_path="/path/to/vault")
        message = client.beta.messages.run_tools(
            model="claude-sonnet-4-5",
            messages=[...],
            tools=[backend],
            betas=["memory-2025-08-18"],
        ).until_done()
    """

    def __init__(self, vault_path: str | Path | None = None) -> None:
        super().__init__()
        self.vault_path = Path(vault_path if vault_path is not None else _DEFAULT_VAULT_PATH).expanduser().resolve()
        self.memory_root = self.vault_path / "memories"
        self.memory_root.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)
        # Ensure wiki dir exists for aliases
        (self.vault_path / "wiki").mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)

    # ── Path resolution ───────────────────────────────────────────────────────

    def _resolve(self, memory_path: str) -> Path:
        """
        Map a /memories/... path to an absolute vault path.

        Alias rules (applied before standard resolution):
          /memories/entities  →  vault/wiki/entities/
          /memories/hot       →  vault/wiki/hot.md
          (see _VAULT_ALIASES)
        """
        if not memory_path.startswith("/memories"):
            raise ToolError(f"Path must start with /memories, got: {memory_path}")

        relative = memory_path[len("/memories"):].lstrip("/")

        # Check vault alias (first path segment)
        first_segment = relative.split("/")[0] if relative else ""
        if first_segment in _VAULT_ALIASES:
            alias_target = _VAULT_ALIASES[first_segment]
            rest = "/".join(relative.split("/")[1:])
            if rest:
                full = self.vault_path / alias_target / rest
            else:
                full = self.vault_path / alias_target
        elif relative:
            full = self.memory_root / relative
        else:
            full = self.memory_root

        resolved = full.resolve()
        resolved_root = self.vault_path.resolve()
        if resolved != resolved_root and not str(resolved).startswith(str(resolved_root) + os.sep):
            raise ToolError(f"Path {memory_path} would escape vault directory")

        _validate_no_symlink_escape(resolved, self.vault_path)
        return resolved

    def _ensure_parent(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)

    # ── view ──────────────────────────────────────────────────────────────────

    @override
    def view(self, command: BetaMemoryTool20250818ViewCommand) -> str:
        full = self._resolve(command.path)

        if not full.exists():
            raise ToolError(f"The path {command.path} does not exist.")

        if full.is_dir():
            items: list[tuple[str, str]] = []

            def _collect(dir_path: Path, rel: str, depth: int) -> None:
                if depth > 2:
                    return
                try:
                    contents = sorted(dir_path.iterdir(), key=lambda x: x.name)
                except Exception:
                    return
                for item in contents:
                    if item.name.startswith("."):
                        continue
                    item_rel = f"{rel}/{item.name}" if rel else item.name
                    try:
                        st = item.stat()
                    except Exception:
                        continue
                    if item.is_dir():
                        items.append((_format_file_size(st.st_size), f"{item_rel}/"))
                        if depth < 2:
                            _collect(item, item_rel, depth + 1)
                    elif item.is_file():
                        items.append((_format_file_size(st.st_size), item_rel))

            _collect(full, "", 1)
            lines = [f"{_format_file_size(full.stat().st_size)}\t{command.path}"]
            lines += [f"{sz}\t{command.path}/{p}" for sz, p in items]
            return f"Files and directories in {command.path} (up to 2 levels):\n" + "\n".join(lines)

        elif full.is_file():
            content = _read_file_content(full, command.path)
            split = content.split("\n")
            if len(split) > MAX_LINES:
                raise ToolError(f"File {command.path} exceeds {MAX_LINES} lines.")

            lines = split
            start = 1
            if command.view_range and len(command.view_range) == 2:
                s = max(1, command.view_range[0]) - 1
                e = len(split) if command.view_range[1] == -1 else command.view_range[1]
                lines = split[s:e]
                start = s + 1

            numbered = [f"{str(i + start).rjust(LINE_NUMBER_WIDTH)}\t{ln}" for i, ln in enumerate(lines)]
            return f"Content of {command.path}:\n" + "\n".join(numbered)

        raise ToolError(f"Unsupported file type at {command.path}")

    # ── create ────────────────────────────────────────────────────────────────

    @override
    def create(self, command: BetaMemoryTool20250818CreateCommand) -> str:
        full = self._resolve(command.path)
        self._ensure_parent(full)

        if full.exists() and full.is_dir():
            raise ToolError(f"Cannot create file at {command.path}: a directory exists there.")

        content = command.file_text or ""
        # Auto-inject Obsidian frontmatter if it's a .md file without one
        if full.suffix == ".md" and content and not content.startswith("---"):
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            stem = full.stem
            frontmatter = f"---\ntitle: \"{stem}\"\ncreated: {now}\ntags: []\n---\n\n"
            content = frontmatter + content

        _atomic_write_file(full, content)
        return f"Created {command.path} ({len(content)} chars)"

    # ── str_replace ───────────────────────────────────────────────────────────

    @override
    def str_replace(self, command: BetaMemoryTool20250818StrReplaceCommand) -> str:
        full = self._resolve(command.path)
        if not full.exists():
            raise ToolError(f"File {command.path} does not exist.")
        if not full.is_file():
            raise ToolError(f"Path {command.path} is not a file.")

        content = _read_file_content(full, command.path)
        count = content.count(command.old_str)
        if count == 0:
            raise ToolError(f"String not found in {command.path}: {command.old_str!r}")
        if count > 1:
            lines = [content[:m].count("\n") + 1 for m in
                     [i for i in range(len(content)) if content[i:].startswith(command.old_str)]]
            raise ToolError(f"Multiple occurrences of old_str in lines: {lines}. Make it unique.")

        pos = content.find(command.old_str)
        changed_line = content[:pos].count("\n")
        new_content = content.replace(command.old_str, command.new_str, 1)
        _atomic_write_file(full, new_content)

        new_lines = new_content.split("\n")
        ctx_start = max(0, changed_line - 2)
        ctx_end = min(len(new_lines), changed_line + 3)
        snippet = "\n".join(
            f"{str(n + 1).rjust(LINE_NUMBER_WIDTH)}\t{new_lines[n]}"
            for n in range(ctx_start, ctx_end)
        )
        return f"Replaced in {command.path}:\n{snippet}"

    # ── insert ────────────────────────────────────────────────────────────────

    @override
    def insert(self, command: BetaMemoryTool20250818InsertCommand) -> str:
        full = self._resolve(command.path)
        if not full.exists():
            raise ToolError(f"File {command.path} does not exist.")
        if not full.is_file():
            raise ToolError(f"Path {command.path} is not a file.")

        content = _read_file_content(full, command.path)
        lines = content.splitlines()

        if command.insert_line < 0 or command.insert_line > len(lines):
            raise ToolError(f"insert_line {command.insert_line} out of range [0, {len(lines)}].")

        lines.insert(command.insert_line, command.insert_text.rstrip("\n"))
        new_content = "\n".join(lines)
        if not new_content.endswith("\n"):
            new_content += "\n"
        _atomic_write_file(full, new_content)
        return f"Inserted at line {command.insert_line} in {command.path}"

    # ── delete ────────────────────────────────────────────────────────────────

    @override
    def delete(self, command: BetaMemoryTool20250818DeleteCommand) -> str:
        full = self._resolve(command.path)

        if command.path in ("/memories", "/memories/"):
            raise ToolError("Cannot delete the /memories root.")
        # Protect vault aliases
        first_seg = command.path.lstrip("/").split("/")[1] if "/" in command.path.lstrip("/") else ""
        if first_seg in ("wiki", "memories"):
            pass  # fine to delete within these

        try:
            if full.is_file():
                full.unlink()
            elif full.is_dir():
                shutil.rmtree(full)
            else:
                raise ToolError(f"Path {command.path} does not exist.")
        except FileNotFoundError as err:
            raise ToolError(f"Path {command.path} not found.") from err

        return f"Deleted {command.path}"

    # ── rename ────────────────────────────────────────────────────────────────

    @override
    def rename(self, command: BetaMemoryTool20250818RenameCommand) -> str:
        old = self._resolve(command.old_path)
        new = self._resolve(command.new_path)

        if new.exists():
            raise ToolError(f"Destination {command.new_path} already exists.")

        self._ensure_parent(new)
        try:
            old.rename(new)
        except FileNotFoundError as err:
            raise ToolError(f"Path {command.old_path} not found.") from err

        return f"Renamed {command.old_path} → {command.new_path}"

    # ── clear ─────────────────────────────────────────────────────────────────

    @override
    def clear_all_memory(self) -> str:
        if self.memory_root.exists():
            shutil.rmtree(self.memory_root)
        self.memory_root.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)
        return "Memory cleared (wiki/ contents preserved)"
