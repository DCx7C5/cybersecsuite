"""Canonical default tags and startup seed helper."""

from typing import TYPE_CHECKING

from .enums import TagColor
from .manager import TagManager, normalize_slug

if TYPE_CHECKING:
    from .models import Tag


DEFAULT_SYSTEM_TAGS: tuple[tuple[str, TagColor, str], ...] = (
    ("critical", TagColor.RED, "Critical severity findings and incidents"),
    ("high-priority", TagColor.ORANGE, "High priority work and escalations"),
    ("investigation", TagColor.BLUE, "Investigation workflows and evidence collection"),
    ("compliance", TagColor.PURPLE, "Compliance and policy-driven records"),
    ("automation", TagColor.GREEN, "Automation tasks and repeatable pipelines"),
    ("triage", TagColor.YELLOW, "Triage classifications and first-pass analysis"),
)


async def seed_default_tags(manager: TagManager | None = None) -> list["Tag"]:
    """Create missing default tags through TagManager APIs only."""
    tag_manager = manager or TagManager()
    created: list["Tag"] = []
    for name, color, description in DEFAULT_SYSTEM_TAGS:
        slug = normalize_slug(name)
        existing = await tag_manager.get_tag_by_slug(slug)
        if existing is not None:
            continue
        tag = await tag_manager.create_tag(
            name=name,
            color=color,
            description=description,
        )
        created.append(tag)
    return created

