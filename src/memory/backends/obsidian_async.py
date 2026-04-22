"""
BetaAsyncObsidianMemoryTool — async Anthropic SDK memory tool backed by an Obsidian vault.

Drop-in async replacement for ObsidianMemoryBackend.
Uses anyio for non-blocking file I/O, suitable for ASGI proxy and MCP server.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from anyio import Path as AsyncPath
from anyio.to_thread import run_sync

from anthropic.lib.tools._beta_builtin_memory_tool import (
    BetaAsyncAbstractMemoryTool,
    _DIR_CREATE_MODE,
    _async_atomic_write_file,
    _async_read_file_content,
    _async_validate_no_symlink_escape,
    _format_file_size,
    MAX_LINES,
    LINE_NUMBER_WIDTH,
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

from memory.backends.obsidian import _VAULT_ALIASES, _DEFAULT_VAULT_PATH


class BetaAsyncObsidianMemoryTool(BetaAsyncAbstractMemoryTool):
    """
    Async Anthropic memory tool backed by an Obsidian vault.

    Identical contract to ObsidianMemoryBackend but async throughout.
    Use in ASGI context (routes.py) and async MCP tools.

    Usage:
        backend = BetaAsyncObsidianMemoryTool(vault_path="/path/to/vault")
        # pass backend to tools= in client.beta.messages.run_tools()
    """

    def __init__(self, vault_path: str | Path | None = None) -> None:
        super().__init__()
        self.vault_path = Path(vault_path if vault_path is not None else _DEFAULT_VAULT_PATH).expanduser().resolve()
        self.memory_root = self.vault_path / "memories"

    async def _ensure_dirs(self) -> None:
        mem = AsyncPath(str(self.memory_root))
        wiki = AsyncPath(str(self.vault_path / "wiki"))
        await mem.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)
        await wiki.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)

    # ── Path resolution ───────────────────────────────────────────────────────

    async def _resolve(self, memory_path: str) -> AsyncPath:
        if not memory_path.startswith("/memories"):
            raise ToolError(f"Path must start with /memories, got: {memory_path}")

        relative = memory_path[len("/memories"):].lstrip("/")
        first_segment = relative.split("/")[0] if relative else ""

        if first_segment in _VAULT_ALIASES:
            alias_target = _VAULT_ALIASES[first_segment]
            rest = "/".join(relative.split("/")[1:])
            base = self.vault_path / alias_target
            full = Path(str(base) + "/" + rest) if rest else base
        elif relative:
            full = self.memory_root / relative
        else:
            full = self.memory_root

        sync_vault = self.vault_path
        resolved = full.resolve()
        resolved_root = sync_vault.resolve()
        if resolved != resolved_root and not resolved.is_relative_to(resolved_root):
            raise ToolError(f"Path {memory_path} would escape vault directory")

        await _async_validate_no_symlink_escape(
            AsyncPath(str(resolved)), AsyncPath(str(self.vault_path))
        )
        return AsyncPath(str(resolved))

    async def _ensure_parent(self, path: AsyncPath) -> None:
        parent = path.parent
        await parent.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)

    # ── view ──────────────────────────────────────────────────────────────────

    @override
    async def view(self, command: BetaMemoryTool20250818ViewCommand) -> str:
        await self._ensure_dirs()
        full = await self._resolve(command.path)

        if not await full.exists():
            raise ToolError(f"Path {command.path} does not exist.")

        if await full.is_dir():
            items: list[tuple[str, str]] = []

            async def _collect(dir_path: AsyncPath, rel: str, depth: int) -> None:
                if depth > 2:
                    return
                try:
                    contents = sorted(
                        [item async for item in dir_path.iterdir()],
                        key=lambda x: x.name,
                    )
                except Exception:
                    return
                for item in contents:
                    if item.name.startswith("."):
                        continue
                    item_rel = f"{rel}/{item.name}" if rel else item.name
                    try:
                        st = await item.stat()
                    except Exception:
                        continue
                    if await item.is_dir():
                        items.append((_format_file_size(st.st_size), f"{item_rel}/"))
                        if depth < 2:
                            await _collect(item, item_rel, depth + 1)
                    else:
                        items.append((_format_file_size(st.st_size), item_rel))

            await _collect(full, "", 1)
            st = await full.stat()
            lines = [f"{_format_file_size(st.st_size)}\t{command.path}"]
            lines += [f"{sz}\t{command.path}/{p}" for sz, p in items]
            return f"Files in {command.path} (up to 2 levels):\n" + "\n".join(lines)

        elif await full.is_file():
            content = await _async_read_file_content(full, command.path)
            split = content.split("\n")
            if len(split) > MAX_LINES:
                raise ToolError(f"File exceeds {MAX_LINES} lines.")

            lines = split
            start = 1
            if command.view_range and len(command.view_range) == 2:
                s = max(1, command.view_range[0]) - 1
                e = len(split) if command.view_range[1] == -1 else command.view_range[1]
                lines = split[s:e]
                start = s + 1

            numbered = [f"{str(i + start).rjust(LINE_NUMBER_WIDTH)}\t{ln}" for i, ln in enumerate(lines)]
            return f"Content of {command.path}:\n" + "\n".join(numbered)

        raise ToolError(f"Unsupported type at {command.path}")

    # ── create ────────────────────────────────────────────────────────────────

    @override
    async def create(self, command: BetaMemoryTool20250818CreateCommand) -> str:
        await self._ensure_dirs()
        full = await self._resolve(command.path)
        await self._ensure_parent(full)

        if await full.exists() and await full.is_dir():
            raise ToolError(f"A directory exists at {command.path}.")

        content = command.file_text or ""
        if str(full).endswith(".md") and content and not content.startswith("---"):
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            stem = Path(str(full)).stem
            content = f"---\ntitle: \"{stem}\"\ncreated: {now}\ntags: []\n---\n\n" + content

        await _async_atomic_write_file(full, content)
        return f"Created {command.path}"

    # ── str_replace ───────────────────────────────────────────────────────────

    @override
    async def str_replace(self, command: BetaMemoryTool20250818StrReplaceCommand) -> str:
        await self._ensure_dirs()
        full = await self._resolve(command.path)

        if not await full.exists():
            raise ToolError(f"File {command.path} does not exist.")

        content = await _async_read_file_content(full, command.path)
        count = content.count(command.old_str)
        if count == 0:
            raise ToolError(f"String not found in {command.path}.")
        if count > 1:
            raise ToolError("Multiple occurrences of old_str — make it unique.")

        new_str = command.new_str if command.new_str is not None else ""
        new_content = content.replace(command.old_str, new_str, 1)
        await _async_atomic_write_file(full, new_content)
        return f"Replaced in {command.path}"

    # ── insert ────────────────────────────────────────────────────────────────

    @override
    async def insert(self, command: BetaMemoryTool20250818InsertCommand) -> str:
        await self._ensure_dirs()
        full = await self._resolve(command.path)

        content = await _async_read_file_content(full, command.path)
        lines = content.splitlines()

        if command.insert_line < 0 or command.insert_line > len(lines):
            raise ToolError(f"insert_line {command.insert_line} out of range.")

        lines.insert(command.insert_line, command.insert_text.rstrip("\n"))
        new_content = "\n".join(lines)
        if not new_content.endswith("\n"):
            new_content += "\n"
        await _async_atomic_write_file(full, new_content)
        return f"Inserted at line {command.insert_line} in {command.path}"

    # ── delete ────────────────────────────────────────────────────────────────

    @override
    async def delete(self, command: BetaMemoryTool20250818DeleteCommand) -> str:
        await self._ensure_dirs()
        full = await self._resolve(command.path)

        if command.path in ("/memories", "/memories/"):
            raise ToolError("Cannot delete /memories root.")

        try:
            if await full.is_file():
                await full.unlink()
            elif await full.is_dir():
                await run_sync(shutil.rmtree, Path(str(full)))
            else:
                raise ToolError(f"Path {command.path} does not exist.")
        except FileNotFoundError as err:
            raise ToolError(f"Path {command.path} not found.") from err

        return f"Deleted {command.path}"

    # ── rename ────────────────────────────────────────────────────────────────

    @override
    async def rename(self, command: BetaMemoryTool20250818RenameCommand) -> str:
        await self._ensure_dirs()
        old = await self._resolve(command.old_path)
        new = await self._resolve(command.new_path)

        if await new.exists():
            raise ToolError(f"Destination {command.new_path} already exists.")

        await self._ensure_parent(new)
        sync_old = Path(str(old))
        sync_new = Path(str(new))
        try:
            await run_sync(sync_old.rename, sync_new)
        except FileNotFoundError as err:
            raise ToolError(f"Path {command.old_path} not found.") from err

        return f"Renamed {command.old_path} → {command.new_path}"

    # ── clear ─────────────────────────────────────────────────────────────────

    @override
    async def clear_all_memory(self) -> str:
        mem = AsyncPath(str(self.memory_root))
        if await mem.exists():
            await run_sync(shutil.rmtree, Path(str(self.memory_root)))
        await mem.mkdir(parents=True, exist_ok=True, mode=_DIR_CREATE_MODE)
        return "Memory cleared (wiki/ preserved)"
