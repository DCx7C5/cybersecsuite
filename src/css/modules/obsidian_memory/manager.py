"""
VaultManager — scaffold and manage a CyberSecSuite forensic Obsidian vault.

Adapted from the claude-obsidian wiki pattern for forensic/security domains.
Provides: scaffold, ingest (with delta-tracking), query, lint, status.
"""
import msgspec

import hashlib
import json
import os
import time

from pathlib import Path
from typing import Any

from css.core.logger import getLogger
logger = getLogger("vault")

_DEFAULT_VAULT_PATH = str(
    Path(os.environ.get("CYBERSECSUITE_HOME", str(Path.home() / ".cybersecsuite"))).expanduser()
    / "vault"
)

# ── Vault structure ────────────────────────────────────────────────────────────

_WIKI_DIRS = [
    "wiki/entities",       # Threat actors, malware families, orgs
    "wiki/iocs",           # Indicators of compromise
    "wiki/ttps",           # MITRE ATT&CK techniques
    "wiki/cases",          # Investigation cases
    "wiki/findings",       # Analyst findings
    "wiki/concepts",       # Frameworks, patterns, ideas
    "wiki/domains",        # Topic areas
    "wiki/canvases",       # Obsidian Canvas visual boards
    "wiki/sources",        # Per-source summary pages
    "wiki/meta",           # Dashboards, lint reports
    ".raw/malware",        # Malware samples / reports (immutable)
    ".raw/articles",       # Fetched articles
    ".raw/intel",          # Threat intel feeds
    ".raw/pcaps",          # Packet captures
    ".raw/logs",           # Log files
    "memories",            # SDK memory tools root
]

_INDEX_TEMPLATE = """\
---
type: meta
title: "Vault Index"
created: {date}
---

# {vault_name} — Index

**Purpose:** {purpose}

## Domains
<!-- one line per wiki/ subdomain, e.g. - [[entities/_index]] -->

## Recent Ingests
<!-- append after each ingest: - YYYY-MM-DD [[sources/slug]] -->

## Cases
<!-- active cases: - [[cases/case-name]] (status) -->
"""

_LOG_TEMPLATE = """\
---
type: meta
title: "Operation Log"
created: {date}
---

# Operation Log

New entries go at the TOP.

---

### {date} — Vault scaffolded
- Purpose: {purpose}
- Dirs created: {dirs}
"""

_HOT_INIT = """\
---
type: meta
title: "Hot Cache"
updated: {date}
---

# Recent Context

## Last Updated
{date}. Vault scaffolded for: {purpose}

## Key Recent Facts
- (none yet)

## Recent Changes
- Scaffolded vault structure

## Active Threads
- (none yet)
"""

@msgspec.struct
class IngestResult:
    source: str
    skipped: bool = False
    skip_reason: str = ""
    pages_created: list[str] = msgspec.field(default_factory=list)
    pages_updated: list[str] = msgspec.field(default_factory=list)
    entities_extracted: list[str] = msgspec.field(default_factory=list)
    error: str | None = None

class VaultManager:
    """
    Manages a CyberSecSuite forensic Obsidian vault.

    vault_path/
      .raw/          — immutable source documents
      wiki/          — Claude-generated rag_vector base
      memories/      — SDK memory tools root
    """

    def __init__(self, vault_path: str | Path | None = None) -> None:
        if vault_path is None:
            vault_path = _DEFAULT_VAULT_PATH
        self.vault_path = Path(vault_path).expanduser().resolve()
        self._manifest_path = self.vault_path / ".raw" / ".manifest.json"

    # ── scaffold ──────────────────────────────────────────────────────────────

    def scaffold(self, vault_name: str, purpose: str) -> dict[str, Any]:
        """
        Create full vault structure with index, log, hot cache, and subdirectory
        indexes. Idempotent — safe to call again if vault already partially exists.
        """
        created: list[str] = []
        date = time.strftime("%Y-%m-%d")

        for d in _WIKI_DIRS:
            full = self.vault_path / d
            full.mkdir(parents=True, exist_ok=True)
            created.append(d)

        # Core wiki files
        self._init_file("wiki/index.md", _INDEX_TEMPLATE.format(
            date=date, vault_name=vault_name, purpose=purpose))
        self._init_file("wiki/log.md", _LOG_TEMPLATE.format(
            date=date, purpose=purpose, dirs=", ".join(_WIKI_DIRS[:6])))
        self._init_file("wiki/hot.md", _HOT_INIT.format(date=date, purpose=purpose))
        self._init_file("wiki/overview.md", f"---\ntitle: Overview\n---\n\n# {vault_name}\n\n{purpose}\n")

        # Sub-indexes
        for sub in ("entities", "iocs", "ttps", "cases", "findings", "concepts"):
            self._init_file(f"wiki/{sub}/_index.md",
                f"---\ntitle: {sub.title()}\n---\n\n# {sub.title()}\n\n<!-- wikilinks will be added here -->\n")

        # CLAUDE.md for cross-project referencing
        self._init_file("CLAUDE.md", _CLAUDE_MD_TEMPLATE.format(
            vault_name=vault_name, purpose=purpose, date=date,
            vault_path=str(self.vault_path)))

        logger.info("Scaffolded vault %s at %s", vault_name, self.vault_path)
        return {"scaffolded": True, "dirs_created": len(created), "vault_path": str(self.vault_path)}

    # ── ingest ────────────────────────────────────────────────────────────────

    def check_already_ingested(self, source_path: str | Path) -> tuple[bool, str]:
        """Return (already_ingested, current_hash)."""
        src = Path(source_path)
        if not src.exists():
            return False, ""
        h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
        manifest = self._load_manifest()
        key = str(src.relative_to(self.vault_path) if src.is_relative_to(self.vault_path) else src)
        entry = manifest.get("sources", {}).get(key, {})
        return entry.get("hash") == h, h

    def record_ingest(self, source_path: str | Path, file_hash: str,
                      pages_created: list[str], pages_updated: list[str]) -> None:
        """Update .raw/.manifest.json after a successful ingest."""
        manifest = self._load_manifest()
        src = Path(source_path)
        key = str(src.relative_to(self.vault_path) if src.is_relative_to(self.vault_path) else src)
        manifest.setdefault("sources", {})[key] = {
            "hash": file_hash,
            "ingested_at": time.strftime("%Y-%m-%d"),
            "pages_created": pages_created,
            "pages_updated": pages_updated,
        }
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # ── status ────────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        """Return vault health summary."""
        if not (self.vault_path / "wiki").exists():
            return {"exists": False, "vault_path": str(self.vault_path)}

        wiki = self.vault_path / "wiki"
        md_files = list(wiki.rglob("*.md"))
        canvas_files = list((wiki / "canvases").glob("*.canvas")) if (wiki / "canvases").exists() else []

        hot_path = wiki / "hot.md"
        hot_age: float | None = None
        if hot_path.exists():
            hot_age = time.time() - hot_path.stat().st_mtime

        manifest = self._load_manifest()
        sources_count = len(manifest.get("sources", {}))

        return {
            "exists": True,
            "vault_path": str(self.vault_path),
            "wiki_pages": len(md_files),
            "canvases": len(canvas_files),
            "sources_ingested": sources_count,
            "hot_cache_age_seconds": round(hot_age) if hot_age is not None else None,
            "memories_files": len(list((self.vault_path / "memories").rglob("*"))) if (self.vault_path / "memories").exists() else 0,
        }

    # ── lint ──────────────────────────────────────────────────────────────────

    def lint(self) -> dict[str, Any]:
        """Basic vault health check: orphan detection, missing indexes, stale hot cache."""
        issues: list[str] = []
        wiki = self.vault_path / "wiki"

        if not wiki.exists():
            return {"healthy": False, "issues": ["wiki/ directory not found — run scaffold first"]}

        # Check required files
        for required in ("index.md", "hot.md", "log.md"):
            if not (wiki / required).exists():
                issues.append(f"Missing {required}")

        # Check hot cache staleness (>24h)
        hot = wiki / "hot.md"
        if hot.exists():
            age_hours = (time.time() - hot.stat().st_mtime) / 3600
            if age_hours > 24:
                issues.append(f"Hot cache is stale ({age_hours:.0f}h old)")

        # Check sub-indexes
        for sub in ("entities", "iocs", "ttps", "cases"):
            if (wiki / sub).exists() and not (wiki / sub / "_index.md").exists():
                issues.append(f"Missing {sub}/_index.md")

        # Check for orphan pages (no wikilinks pointing to them) — simplified
        index_content = (wiki / "index.md").read_text(encoding="utf-8") if (wiki / "index.md").exists() else ""
        all_pages = list(wiki.rglob("*.md"))
        unreferenced = []
        for page in all_pages:
            rel = str(page.relative_to(wiki))
            if rel in ("index.md", "hot.md", "log.md", "overview.md"):
                continue
            stem = page.stem
            if f"[[{stem}]]" not in index_content and not rel.endswith("_index.md"):
                unreferenced.append(rel)

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "unreferenced_pages": unreferenced[:20],
            "page_count": len(all_pages),
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    def _init_file(self, rel_path: str, content: str) -> None:
        """Write file only if it doesn't already exist."""
        full = self.vault_path / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.exists():
            full.write_text(content, encoding="utf-8")

    def _load_manifest(self) -> dict[str, Any]:
        if self._manifest_path.exists():
            try:
                return json.loads(self._manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"sources": {}}

# ── CLAUDE.md template ────────────────────────────────────────────────────────

_CLAUDE_MD_TEMPLATE = """\
# {vault_name}: Forensic Wiki Vault

Mode: Forensic / CyberSecSuite
Purpose: {purpose}
Created: {date}
Vault Path: {vault_path}

## Structure

```
.raw/           immutable source documents (malware reports, articles, intel, logs, pcaps)
wiki/           Claude-generated rag_vector base
  entities/     threat actors, malware families, orgs
  iocs/         indicators of compromise (IPs, hashes, domains)
  ttps/         MITRE ATT&CK techniques (TxxYY pages)
  cases/        investigation cases (active + closed)
  findings/     analyst findings and conclusions
  canvases/     Obsidian Canvas visual boards
  hot.md        hot cache (~500 words, recent context)
  index.md      master catalog
memories/       SDK memory tools root (/memories/* paths)
```

## Reading Order (token-efficient)

When you need context from this vault:
1. Read `wiki/hot.md` first (~500 words, costs ~650 tokens)
2. If not enough, read `wiki/index.md`
3. If you need domain specifics, read `wiki/<domain>/_index.md`
4. Only then read individual wiki pages

Do NOT read the wiki for: general coding questions, things already in context.

## Operations

| You say | Action |
|---------|--------|
| "scaffold vault for [purpose]" | `vault_scaffold` MCP tools |
| "ingest [file or url]" | `vault_ingest` MCP tools |
| "what do you know about X" | `vault_query` MCP tools |
| "lint vault" | `vault_lint` MCP tools |
| "vault status" | `vault_status` MCP tools |
| "/canvas [type]" | `canvas_create` MCP tools |

## Conventions

- All notes use YAML frontmatter: type, created, tags (minimum)
- Wikilinks: [[Note Name]] — filenames are unique, no paths needed
- `.raw/` is immutable — never modify source documents
- `wiki/log.md` is append-only — new entries go at the TOP
- `wiki/hot.md` updates after every ingest, query, and session end
"""
