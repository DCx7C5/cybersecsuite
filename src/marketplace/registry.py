"""Marketplace in-memory registry with JSON persistence.

Provides a singleton ``MarketplaceRegistry`` that holds the full catalog of
available items and the subset that has been installed locally.  The catalog
is seeded at module load time from ``seed.py``; installed state is persisted
to ``~/.cybersecsuite/marketplace/installed.json``.

Referenz:
    plan.md T033 — Marketplace module
    plan.md T039 — Seed data
    src/marketplace/models.py — MarketplaceItem, MarketplaceItemStatus
    src/marketplace/seed.py — SEED_ITEMS
"""


import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from marketplace.models import MarketplaceItem, MarketplaceItemStatus

logger = logging.getLogger("marketplace.registry")

# ── Storage paths ──────────────────────────────────────────────────────────────
_BASE_DIR = Path.home() / ".cybersecsuite" / "marketplace"
_CATALOG_PATH = _BASE_DIR / "catalog.json"
_INSTALLED_PATH = _BASE_DIR / "installed.json"

# ── In-memory stores ───────────────────────────────────────────────────────────
_ITEMS: dict[str, MarketplaceItem] = {}
_INSTALLED: dict[str, MarketplaceItem] = {}

_ProviderLiteral = Literal[
    "claude", "copilot", "cursor", "openai", "gemini", "grok", "universal"
]
_KindLiteral = Literal["agent", "skill", "combo", "template"]


def seed(items: list[MarketplaceItem]) -> None:
    """Populate the in-memory catalog.

    Called once at module load; replaces any existing catalog entries only
    when the ID is not already present (idempotent for subsequent calls).

    Args:
        items: List of ``MarketplaceItem`` objects to register.
    """
    for item in items:
        _ITEMS[item.id] = item
    logger.debug("Seeded %d items into marketplace catalog", len(items))


def load_catalog() -> None:
    """Load catalog from ``_CATALOG_PATH`` if it exists; otherwise retain seed data.

    The file must be a JSON array of serialised ``MarketplaceItem`` dicts.
    """
    if not _CATALOG_PATH.exists():
        logger.debug("No catalog file found at %s — using seed data", _CATALOG_PATH)
        return
    try:
        raw: list[dict] = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
        for entry in raw:
            item = MarketplaceItem.model_validate(entry)
            _ITEMS[item.id] = item
        logger.info("Loaded %d items from %s", len(raw), _CATALOG_PATH)
    except Exception:
        logger.exception("Failed to load catalog from %s", _CATALOG_PATH)


def list_items(
        kind: _KindLiteral | None = None,
    provider: _ProviderLiteral | None = None,
    tags: list[str] | None = None,
    status: MarketplaceItemStatus | None = None,
) -> list[MarketplaceItem]:
    """Return catalog items filtered by optional criteria, sorted by name.

    Args:
        kind: Restrict to ``"agent"``, ``"skill"``, ``"combo"``, or ``"template"``.
        provider: Restrict to a specific provider slug.
        tags: Return only items that have *all* of the given tags.
        status: Filter by lifecycle status.

    Returns:
        Sorted list of matching ``MarketplaceItem`` objects.
    """
    results: list[MarketplaceItem] = []
    for item in _ITEMS.values():
        if kind is not None and item.kind != kind:
            continue
        if provider is not None and item.provider != provider:
            continue
        if tags is not None and not all(t in item.tags for t in tags):
            continue
        if status is not None and item.status != status:
            continue
        results.append(item)
    return sorted(results, key=lambda i: i.name.lower())


def get_item(item_id: str) -> MarketplaceItem | None:
    """Look up a single catalog item by its kebab-case ID.

    Args:
        item_id: The unique item identifier.

    Returns:
        The ``MarketplaceItem`` if found, otherwise ``None``.
    """
    return _ITEMS.get(item_id)


def search(query: str) -> list[MarketplaceItem]:
    """Fuzzy (substring, case-insensitive) search across name, description, and tags.

    Args:
        query: Search string.

    Returns:
        Matching items sorted by name.
    """
    q = query.strip().lower()
    if not q:
        return list_items()
    results: list[MarketplaceItem] = []
    for item in _ITEMS.values():
        haystack = (
            item.name.lower()
            + " "
            + item.description.lower()
            + " "
            + " ".join(t.lower() for t in item.tags)
        )
        if q in haystack:
            results.append(item)
    return sorted(results, key=lambda i: i.name.lower())


def list_installed() -> list[MarketplaceItem]:
    """Return all currently installed items, sorted by name.

    Returns:
        Sorted list of installed ``MarketplaceItem`` objects.
    """
    return sorted(_INSTALLED.values(), key=lambda i: i.name.lower())


def save_installed() -> None:
    """Persist the installed item registry to ``_INSTALLED_PATH`` (JSON)."""
    try:
        _BASE_DIR.mkdir(parents=True, exist_ok=True)
        payload = [item.model_dump(mode="json") for item in _INSTALLED.values()]
        _INSTALLED_PATH.write_text(
            json.dumps(payload, indent=2, default=str), encoding="utf-8"
        )
        logger.debug("Saved %d installed items to %s", len(payload), _INSTALLED_PATH)
    except Exception(BaseException):
        logger.exception("Failed to save installed items to %s", _INSTALLED_PATH)


def _load_installed() -> None:
    """Reload installed items from disk into ``_INSTALLED`` (called at startup)."""
    if not _INSTALLED_PATH.exists():
        return
    try:
        raw: list[dict] = json.loads(_INSTALLED_PATH.read_text(encoding="utf-8"))
        for entry in raw:
            item = MarketplaceItem.model_validate(entry)
            _INSTALLED[item.id] = item
            # Sync status back into catalog.
            if item.id in _ITEMS:
                _ITEMS[item.id] = item
        logger.debug("Loaded %d installed items from %s", len(raw), _INSTALLED_PATH)
    except Exception:
        logger.exception("Failed to load installed items from %s", _INSTALLED_PATH)


class MarketplaceRegistry:
    """In-memory catalog registry with JSON-backed installed-item persistence.

    Usage::

        reg = get_registry()
        items = reg.list_items(kind="agent", provider="claude")
        item  = reg.install("claude-forensic-analyst")
    """

    # ── Catalog management ─────────────────────────────────────────────────────

    # ── Querying ───────────────────────────────────────────────────────────────

    # ── Install / uninstall ────────────────────────────────────────────────────

    def install(self, item_id: str) -> MarketplaceItem:
        """Mark a catalog item as installed and persist the installed list.

        Args:
            item_id: The unique item identifier.

        Returns:
            The updated ``MarketplaceItem`` with ``status=installed``.

        Raises:
            KeyError: If ``item_id`` is not found in the catalog.
        """
        item = _ITEMS.get(item_id)
        if item is None:
            raise KeyError(f"Marketplace item not found: {item_id!r}")

        # Mutate a copy so the catalog entry remains pristine.
        installed = item.model_copy(
            update={
                "status": MarketplaceItemStatus.installed,
                "installed_at": datetime.now(timezone.utc),
            }
        )
        _ITEMS[item_id] = installed  # reflect status in catalog too
        _INSTALLED[item_id] = installed
        save_installed()
        logger.info("Installed marketplace item: %s", item_id)
        return installed

    def uninstall(self, item_id: str) -> bool:
        """Remove an item from the installed set and revert its catalog status.

        Args:
            item_id: The unique item identifier.

        Returns:
            ``True`` if the item was previously installed, ``False`` otherwise.
        """
        if item_id not in _INSTALLED:
            return False
        del _INSTALLED[item_id]
        # Revert catalog entry to available if still present.
        if item_id in _ITEMS:
            _ITEMS[item_id] = _ITEMS[item_id].model_copy(
                update={
                    "status": MarketplaceItemStatus.available,
                    "installed_at": None,
                }
            )
        save_installed()
        logger.info("Uninstalled marketplace item: %s", item_id)
        return True

    # ── Persistence ────────────────────────────────────────────────────────────


# ── Singleton ──────────────────────────────────────────────────────────────────

_registry: MarketplaceRegistry | None = None


def get_registry() -> MarketplaceRegistry | None:
    """Return the process-level singleton ``MarketplaceRegistry``.

    Returns:
        The initialized ``MarketplaceRegistry`` instance.
    """
    global _registry
    if _registry is None:
        _registry = MarketplaceRegistry()
    return _registry


# ── Module-level seed (always executed on import) ──────────────────────────────
from marketplace.seed import SEED_ITEMS as _SEED_ITEMS  # noqa: E402

_reg = get_registry()
seed(_SEED_ITEMS)
load_catalog()
_load_installed()
