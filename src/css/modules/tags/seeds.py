"""Canonical default tags and startup seed helper."""

from typing import Protocol

from .enums import TagColor
from .manager import TagManager, normalize_slug

class TagSeedManager(Protocol):
    async def get_tag_by_slug(self, slug: str) -> object | None:
        ...

    async def create_tag(
        self,
        *,
        name: str,
        color: TagColor = TagColor.GRAY,
        description: str = "",
        parent_tag_id: int | None = None,
    ) -> object:
        ...


DEFAULT_SYSTEM_TAGS: tuple[tuple[str, TagColor, str], ...] = (
    ("critical", TagColor.RED, "Critical severity findings and incidents"),
    ("high-priority", TagColor.ORANGE, "High priority work and escalations"),
    ("investigation", TagColor.BLUE, "Investigation workflows and evidence collection"),
    ("compliance", TagColor.PURPLE, "Compliance and policy-driven records"),
    ("automation", TagColor.GREEN, "Automation tasks and repeatable pipelines"),
    ("triage", TagColor.YELLOW, "Triage classifications and first-pass analysis"),
)


async def seed_default_tags(manager: TagSeedManager | None = None) -> list[object]:
    """Create missing default tags through TagManager APIs only."""
    tag_manager = manager or TagManager()
    created: list[object] = []
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
