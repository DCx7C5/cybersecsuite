"""Skill ↔ Marketplace bridge — register/lookup skills as marketplace items.

A Skill is a first-class marketplace item (``MarketplaceItemType.skill``).
This module provides helpers that convert between a ``Skill`` domain object
and a ``MarketplaceItem`` ORM record without coupling the skills module to
the marketplace module's ORM layer.

Usage::

    from css.modules.skills.marketplace_bridge import skill_to_marketplace_item

    item = await skill_to_marketplace_item(my_skill)  # saves to DB
"""


import logging

from css.modules.skills.types import Skill
from css.modules.marketplace.models import MarketplaceItem
from css.modules.marketplace.enums import MarketplaceItemType, MarketplaceItemStatus
from css.modules.marketplace.cache import marketplace_cache

logger = logging.getLogger(__name__)


async def skill_to_marketplace_item(skill: Skill):
    """Create or update a ``MarketplaceItem`` record from *skill*.

    The item's ``kind`` is set to ``MarketplaceItemType.skill`` and its
    ``meta`` dict is populated with skill-specific fields (``skill_id``,
    ``install_path``, ``tags``).

    Args:
        skill: :class:`~css.modules.skills.types.Skill` instance.

    Returns:
        The created/updated :class:`~css.modules.marketplace.models.MarketplaceItem`.
    """

    slug = f"skill:{skill.skill_id}"
    existing = await MarketplaceItem.get_or_none(slug=slug)

    meta = {
        "skill_id": skill.skill_id,
        "install_path": str(skill.install_path) if skill.install_path else None,
        "tags": getattr(skill, "tags", []),
    }

    if existing:
        existing.name = skill.name
        existing.description = getattr(skill, "description", "")
        existing.meta = {**existing.meta, **meta}
        if skill.is_installed:
            existing.status = MarketplaceItemStatus.installed
        await existing.save()
        logger.debug("Updated marketplace item for skill: %s", slug)
        marketplace_cache.invalidate(f"item:{slug}")
        marketplace_cache.invalidate_prefix("items:skill")
        return existing

    item = MarketplaceItem(
        slug=slug,
        name=skill.name,
        description=getattr(skill, "description", ""),
        kind=MarketplaceItemType.skill,
        status=MarketplaceItemStatus.installed if skill.is_installed else MarketplaceItemStatus.disabled,
        meta=meta,
    )
    await item.save()
    logger.debug("Created marketplace item for skill: %s", slug)
    marketplace_cache.invalidate_prefix("items:skill")
    return item


async def get_skill_marketplace_item(skill_id: str) -> MarketplaceItem | None:
    """Return the ``MarketplaceItem`` for *skill_id*, or ``None``.

    Args:
        skill_id: The skill's unique identifier.

    Returns:
        :class:`~css.modules.marketplace.models.MarketplaceItem` or ``None``.
    """
    from css.modules.marketplace.models import MarketplaceItem

    return await MarketplaceItem.get_or_none(slug=f"skill:{skill_id}")


__all__ = ["skill_to_marketplace_item", "get_skill_marketplace_item"]
