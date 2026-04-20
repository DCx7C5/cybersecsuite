"""
HotCache — manages wiki/hot.md as a rolling ~500-word session context.

The hot cache exists so any Claude session (or any other project pointing at
this vault) can load recent context in ~500 tokens without crawling the full wiki.

Adapted from the claude-obsidian hot cache pattern.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


_TEMPLATE = """\
---
type: meta
title: "Hot Cache"
updated: {updated}
---

# Recent Context

## Last Updated
{updated_short}. {summary}

## Key Recent Facts
{facts}

## Recent Changes
{changes}

## Active Threads
{threads}
"""

_HOT_PATH = "wiki/hot.md"
_MAX_WORDS = 500


@dataclass
class HotCacheState:
    summary: str = "Session started."
    facts: list[str] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)
    threads: list[str] = field(default_factory=list)


class HotCache:
    """
    Manages wiki/hot.md — the ~500-word rolling session context.

    Every VaultManager operation (ingest, query, scaffold) should call
    update() to keep the hot cache fresh. The next session reads it first.
    """

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).resolve()
        self.hot_path = self.vault_path / _HOT_PATH
        self.hot_path.parent.mkdir(parents=True, exist_ok=True)

    # ── read ──────────────────────────────────────────────────────────────────

    def read(self) -> str:
        """Return current hot.md content, or empty string if not present."""
        if not self.hot_path.exists():
            return ""
        return self.hot_path.read_text(encoding="utf-8")

    def read_summary(self) -> str:
        """Return just the '## Last Updated' paragraph for quick context."""
        content = self.read()
        if not content:
            return "No hot cache found."
        for line in content.splitlines():
            if line.startswith("## Last Updated"):
                # Return the next non-empty line
                lines = content.splitlines()
                idx = lines.index(line)
                for follow in lines[idx + 1:]:
                    if follow.strip():
                        return follow.strip()
        return content[:300]

    # ── write ─────────────────────────────────────────────────────────────────

    def update(self, state: HotCacheState) -> None:
        """Overwrite hot.md with the given state (keep under 500 words)."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%S")
        now_short = time.strftime("%Y-%m-%d")

        facts_md = "\n".join(f"- {f}" for f in state.facts[-10:]) or "- (none yet)"
        changes_md = "\n".join(f"- {c}" for c in state.changes[-10:]) or "- (none yet)"
        threads_md = "\n".join(f"- {t}" for t in state.threads[-5:]) or "- (none yet)"

        content = _TEMPLATE.format(
            updated=now_iso,
            updated_short=now_short,
            summary=state.summary,
            facts=facts_md,
            changes=changes_md,
            threads=threads_md,
        )

        # Trim to 500 words if needed
        words = content.split()
        if len(words) > _MAX_WORDS:
            content = " ".join(words[:_MAX_WORDS]) + "\n"

        self.hot_path.write_text(content, encoding="utf-8")

    def append_fact(self, fact: str) -> None:
        """Quick add a single fact to the hot cache without full re-render."""
        state = self._parse()
        state.facts.append(fact)
        self.update(state)

    def append_change(self, change: str) -> None:
        """Quick record a wiki change."""
        state = self._parse()
        state.changes.append(change)
        self.update(state)

    def set_thread(self, thread: str) -> None:
        """Set the active thread (replaces last entry)."""
        state = self._parse()
        state.threads = [thread]
        self.update(state)

    def clear(self) -> None:
        """Reset hot cache to empty state."""
        self.update(HotCacheState())

    # ── parse ─────────────────────────────────────────────────────────────────

    def _parse(self) -> HotCacheState:
        """Parse current hot.md back into a HotCacheState (best-effort)."""
        content = self.read()
        if not content:
            return HotCacheState()

        state = HotCacheState()
        lines = content.splitlines()
        section: Optional[str] = None

        for line in lines:
            if line.startswith("## Last Updated"):
                section = "summary"
            elif line.startswith("## Key Recent Facts"):
                section = "facts"
            elif line.startswith("## Recent Changes"):
                section = "changes"
            elif line.startswith("## Active Threads"):
                section = "threads"
            elif line.startswith("## "):
                section = None
            elif section == "summary" and line.strip() and not line.startswith("#"):
                # The line after "## Last Updated" is "DATE. summary"
                parts = line.split(". ", 1)
                state.summary = parts[1] if len(parts) > 1 else line
            elif section == "facts" and line.startswith("- "):
                state.facts.append(line[2:])
            elif section == "changes" and line.startswith("- "):
                state.changes.append(line[2:])
            elif section == "threads" and line.startswith("- "):
                state.threads.append(line[2:])

        return state

    # ── mirror ────────────────────────────────────────────────────────────────

    def mirror_to_memories(self, memories_root: Path) -> None:
        """
        Copy hot.md → memories/hot.md so the SDK memory tool can read it
        at /memories/hot without going through the vault alias.
        """
        content = self.read()
        if content:
            dest = memories_root / "hot.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
