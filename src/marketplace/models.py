"""Marketplace data models — provider-agnostic agent/skill/combo catalog.

Referenz:
    plan.md T033 — Marketplace module
    plan.md T039 — Seed data
    src/marketplace/registry.py — in-memory catalog
    src/marketplace/__init__.py — public API
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class MarketplaceItemStatus(str, Enum):
    """Lifecycle status of a marketplace item."""

    available = "available"
    installed = "installed"
    update_available = "update_available"
    deprecated = "deprecated"


class ProviderMeta(BaseModel):
    """Provider-specific frontmatter fields — all optional.

    Captures structured metadata used by each AI provider's agent format
    (SKILL.md, AGENTS.md, .mdc rules, etc.).
    """

    model: str | None = None
    tools: list[str] = Field(default_factory=list)
    max_turns: int | None = None
    domain: str | None = None
    tags: list[str] = Field(default_factory=list)
    mitre_attack: list[str] = Field(default_factory=list)
    capec: list[str] = Field(default_factory=list)
    nist_csf: list[str] = Field(default_factory=list)


class MarketplaceItem(BaseModel):
    """A single installable marketplace item (agent, skill, combo, or template).

    Items are uniquely identified by a kebab-case ``id`` and can be installed
    into the local CyberSecSuite workspace.  Once installed, ``status`` is
    updated to ``installed`` and ``installed_at`` is stamped.
    """

    id: str = Field(..., description="Kebab-case unique identifier")
    name: str
    description: str
    kind: Literal["agent", "skill", "combo", "template"]
    provider: Literal[
        "claude", "copilot", "cursor", "openai", "gemini", "grok", "universal"
    ]
    version: str = "0.1.0"
    status: MarketplaceItemStatus = MarketplaceItemStatus.available
    tags: list[str] = Field(default_factory=list)
    meta: ProviderMeta = Field(default_factory=ProviderMeta)
    install_path: str | None = Field(
        default=None, description="Relative path where item is installed"
    )
    source_url: str | None = None
    installed_at: datetime | None = None
