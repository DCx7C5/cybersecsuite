"""
Vault MCP tools — scaffold, ingest, query, lint, status.

These tools expose the VaultManager via the CyberSecSuite MCP server.
The vault path defaults to CYBERSEC_VAULT_PATH env var, or ./data/vault.
"""
from __future__ import annotations

import os
from typing import Any

from ..helpers import JsonDict, sdk_error, sdk_result
from ..sdk_compat import tool

_VAULT_PATH = os.getenv("CYBERSEC_VAULT_PATH", "./data/vault")


def _get_vault():
    from memory.vault.manager import VaultManager
    return VaultManager(_VAULT_PATH)


@tool(
    "vault_scaffold",
    "Scaffold a new CyberSecSuite forensic Obsidian vault. Creates wiki/, .raw/, memories/ directories and seed files. Idempotent.",
    {
        "vault_name": {"type": "string", "description": "Display name for the vault, e.g. 'APT29 Investigation'"},
        "purpose": {"type": "string", "description": "One-line description of the investigation or purpose"},
    },
)
async def vault_scaffold(args: dict[str, Any]) -> JsonDict:
    vault_name = args.get("vault_name", "CyberSecSuite Vault")
    purpose = args.get("purpose", "Forensic investigation workspace")
    try:
        vm = _get_vault()
        result = vm.scaffold(vault_name, purpose)
        return sdk_result(result)
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "vault_status",
    "Return vault health summary: page count, canvas count, sources ingested, hot cache age.",
    {},
)
async def vault_status(args: dict[str, Any]) -> JsonDict:
    try:
        vm = _get_vault()
        return sdk_result(vm.status())
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "vault_ingest",
    "Ingest a file or URL into the forensic vault. Delta-tracked — unchanged sources are skipped unless force=true.",
    {
        "source": {"type": "string", "description": "File path or URL to ingest into .raw/"},
        "category": {
            "type": "string",
            "enum": ["articles", "intel", "malware", "logs", "pcaps"],
            "description": "Where to place the raw source. Defaults to 'articles' for URLs.",
            "default": "articles",
        },
        "force": {"type": "boolean", "default": False, "description": "Re-ingest even if hash unchanged"},
        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags to apply to extracted wiki pages"},
    },
)
async def vault_ingest(args: dict[str, Any]) -> JsonDict:
    source = args.get("source", "")
    _category = args.get("category", "articles")
    force = args.get("force", False)
    tags = args.get("tags", [])

    if not source:
        return sdk_error("'source' is required")

    try:
        import time
        from pathlib import Path

        vm = _get_vault()

        # URL handling — save to .raw/articles/<slug>-<date>.md
        if source.startswith("http://") or source.startswith("https://"):
            from urllib.parse import urlparse
            parsed = urlparse(source)
            slug = (parsed.path.rstrip("/").split("/")[-1] or parsed.netloc).lower().replace(" ", "-")[:50]
            date = time.strftime("%Y-%m-%d")
            raw_path = Path(_VAULT_PATH) / ".raw" / "articles" / f"{slug}-{date}.md"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            if not raw_path.exists():
                raw_path.write_text(f"---\nsource_url: {source}\ningested_at: {date}\ntags: {tags}\n---\n\n# {slug}\n\nFetch content manually via web_search or web_fetch.\n", encoding="utf-8")
            source = str(raw_path)

        src_path = Path(source)
        if not src_path.exists():
            return sdk_error(f"Source not found: {source}")

        # Delta check
        already_done, file_hash = vm.check_already_ingested(src_path)
        if already_done and not force:
            return sdk_result({"skipped": True, "reason": "Already ingested (unchanged). Use force=true to re-ingest.", "source": source})

        # Record ingest — actual content extraction is done by the agent
        # The MCP tool records tracking metadata; Claude handles wiki page creation
        vm.record_ingest(src_path, file_hash, pages_created=[], pages_updated=["wiki/log.md", "wiki/hot.md"])

        return sdk_result({
            "ingested": True,
            "source": source,
            "hash": file_hash,
            "vault_path": str(vm.vault_path),
            "instructions": (
                "Source recorded. Now: (1) read the source file, "
                "(2) extract entities/IOCs/TTPs/findings, "
                "(3) create wiki pages in wiki/<domain>/<name>.md, "
                "(4) update wiki/index.md and wiki/log.md, "
                "(5) update wiki/hot.md with key facts."
            ),
        })
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "vault_query",
    "Query the forensic vault for information. Reads hot cache first, then index, then relevant pages.",
    {
        "question": {"type": "string", "description": "What to look up in the vault"},
        "domain": {
            "type": "string",
            "enum": ["entities", "iocs", "ttps", "cases", "findings", "concepts", "all"],
            "default": "all",
            "description": "Which wiki domain to search",
        },
        "limit": {"type": "integer", "default": 10, "description": "Max pages to include in result"},
    },
)
async def vault_query(args: dict[str, Any]) -> JsonDict:
    question = args.get("question", "")
    domain = args.get("domain", "all")
    limit = min(args.get("limit", 10), 50)

    if not question:
        return sdk_error("'question' is required")

    try:
        from pathlib import Path

        vault = Path(_VAULT_PATH)
        wiki = vault / "wiki"

        if not wiki.exists():
            return sdk_error("Vault not found. Run vault_scaffold first.")

        # Read hot cache
        hot_content = ""
        hot_path = wiki / "hot.md"
        if hot_path.exists():
            hot_content = hot_path.read_text(encoding="utf-8")

        # Find relevant pages by keyword matching
        search_terms = question.lower().split()
        domains = [domain] if domain != "all" else ["entities", "iocs", "ttps", "cases", "findings", "concepts"]
        matches: list[dict[str, Any]] = []
        for d in domains:
            d_path = wiki / d
            if not d_path.exists():
                continue
            for md_file in sorted(d_path.glob("*.md")):
                if md_file.name.startswith("_"):
                    continue
                content = md_file.read_text(encoding="utf-8")
                score = sum(term in content.lower() for term in search_terms)
                if score > 0:
                    matches.append({"path": str(md_file.relative_to(vault)), "score": score, "content": content[:1000]})

        matches.sort(key=lambda m: m["score"], reverse=True)
        matches = matches[:limit]

        return sdk_result({
            "question": question,
            "hot_cache": hot_content[:2000],
            "matches": matches,
            "match_count": len(matches),
        })
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "vault_lint",
    "Check vault health: orphan pages, missing indexes, stale hot cache.",
    {},
)
async def vault_lint(args: dict[str, Any]) -> JsonDict:
    try:
        vm = _get_vault()
        return sdk_result(vm.lint())
    except Exception as e:
        return sdk_error(str(e))

ALL_TOOLS = [vault_scaffold, vault_status, vault_ingest, vault_query, vault_lint]
