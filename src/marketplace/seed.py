"""Marketplace seed data — one item per supported provider.

Referenz:
    plan.md T039 — Seed data (provider frontmatter standards table)
    src/marketplace/models.py — MarketplaceItem, ProviderMeta
    src/marketplace/registry.py — seed() call-site
"""
from __future__ import annotations

from marketplace.models import MarketplaceItem, ProviderMeta

SEED_ITEMS: list[MarketplaceItem] = [
    MarketplaceItem(
        id="claude-forensic-analyst",
        name="Forensic Analyst",
        description=(
            "Deep-dive file system + memory forensics specialist. "
            "SKILL.md format for Claude Code."
        ),
        kind="agent",
        provider="claude",
        tags=["forensics", "filesystem", "memory"],
        meta=ProviderMeta(
            domain="forensics",
            tags=["filesystem", "memory", "artifact"],
            mitre_attack=["T1059", "T1078"],
        ),
    ),
    MarketplaceItem(
        id="copilot-threat-hunter",
        name="Threat Hunter",
        description=(
            "GitHub Copilot agent for hunting TTPs and IOCs across repositories."
        ),
        kind="agent",
        provider="copilot",
        tags=["threat-hunting", "ttp", "ioc"],
    ),
    MarketplaceItem(
        id="cursor-security-rules",
        name="Security Glob Rules",
        description=(
            "Cursor .mdc rules for secure coding practices — "
            "SQL injection, XSS, auth checks."
        ),
        kind="template",
        provider="cursor",
        tags=["security", "rules", "cursor"],
    ),
    MarketplaceItem(
        id="openai-pentest-agent",
        name="PenTest Agent",
        description=(
            "OpenAI AGENTS.md format pentest workflow — "
            "recon, exploitation, reporting phases."
        ),
        kind="agent",
        provider="openai",
        tags=["pentest", "red-team"],
    ),
    MarketplaceItem(
        id="gemini-network-analyst",
        name="Network Analyst",
        description=(
            "Gemini CLI AGENTS.md agent for network traffic analysis "
            "and anomaly detection."
        ),
        kind="agent",
        provider="gemini",
        tags=["network", "anomaly", "pcap"],
    ),
    MarketplaceItem(
        id="grok-osint-researcher",
        name="OSINT Researcher",
        description=(
            "xAI Grok agent for open-source intelligence gathering and correlation."
        ),
        kind="agent",
        provider="grok",
        tags=["osint", "intelligence"],
    ),
    MarketplaceItem(
        id="universal-ioc-scanner",
        name="IOC Scanner",
        description=(
            "Universal (AGENTS.md + SKILL.md) IOC extraction and enrichment workflow."
        ),
        kind="skill",
        provider="universal",
        tags=["ioc", "scanner", "enrichment"],
    ),
    MarketplaceItem(
        id="claude-qol-silent",
        name="Silent Mode Preset",
        description=(
            "Apply 'silent' QoL preset — no chat, no thinking, file-only output."
        ),
        kind="combo",
        provider="claude",
        tags=["qol", "output-control"],
    ),
]
