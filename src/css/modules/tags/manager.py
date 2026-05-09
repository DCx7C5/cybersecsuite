"""Tag management and assignment — wraps Tortoise ORM Tag model."""

from css.core.logger import getLogger
import re
from typing import TYPE_CHECKING

from tortoise.expressions import Q

from .enums import TagColor
from .exceptions import TagNotFoundError, TagCreationError, TagValidationError
from .types import TagConflictResolution, TagSuggestion

if TYPE_CHECKING:
    from .models import Tag

logger = getLogger(__name__)


def normalize_slug(text: str) -> str:
    """Normalize text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\-_]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


class TagManager:
    """Tag CRUD backed by Tortoise ORM (Tag model).

    Tag-to-resource assignments are handled by each module's own M2M
    junction tables (e.g. MarketplaceItemTag, HybridToolDefinitionTag).
    """

    @staticmethod
    def _tag_model() -> type["Tag"]:
        from .models import Tag

        return Tag

    async def create_tag(
        self,
        name: str,
        color: TagColor = TagColor.GRAY,
        description: str = "",
        parent_tag_id: int | None = None,
    ) -> "Tag":
        """Create a new tag and persist to database."""
        Tag = self._tag_model()
        if not name or len(name) > 128:
            raise TagValidationError("Tag name must be 1-128 characters", field="name")

        if not re.match(r'^[\w\s\-]+$', name):
            raise TagValidationError("Tag name contains invalid characters", field="name")

        slug = normalize_slug(name)

        existing = await Tag.get_or_none(slug=slug)
        if existing is not None:
            raise TagCreationError(f"Tag already exists: {name}", tag_name=name)

        if parent_tag_id is not None:
            parent = await Tag.get_or_none(id=parent_tag_id)
            if parent is None:
                raise TagNotFoundError(str(parent_tag_id))

        tag = await Tag.create(
            name=name,
            slug=slug,
            color=color,
            description=description,
            parent_tag_id=parent_tag_id,
        )
        logger.info("Created tag: %s (slug: %s)", name, slug)
        return tag

    async def get_tag(self, tag_id: int) -> "Tag | None":
        """Get tag by ID."""
        Tag = self._tag_model()
        return await Tag.get_or_none(id=tag_id)

    async def get_tag_by_slug(self, slug: str) -> "Tag | None":
        """Get tag by slug."""
        Tag = self._tag_model()
        return await Tag.get_or_none(slug=slug)

    async def get_tag_or_fail(self, tag_id: int) -> "Tag":
        """Get tag by ID or raise error."""
        Tag = self._tag_model()
        tag = await Tag.get_or_none(id=tag_id)
        if tag is None:
            raise TagNotFoundError(str(tag_id))
        return tag

    async def list_tags(self, color: TagColor | None = None) -> list["Tag"]:
        """List tags with optional color filter."""
        Tag = self._tag_model()
        qs = Tag.all()
        if color is not None:
            qs = qs.filter(color=color)
        return await qs.order_by("name")

    async def search_tags(self, query: str) -> list["Tag"]:
        """Search tags by name or description."""
        Tag = self._tag_model()
        q = query.lower()
        return await Tag.filter(
            Q(name__icontains=q) | Q(description__icontains=q),
        ).order_by("name")

    async def suggest_tags(self, prefix: str, limit: int = 10) -> list[TagSuggestion]:
        """Suggest tags by prefix for autocomplete UX."""
        Tag = self._tag_model()
        needle = prefix.strip().lower()
        if not needle:
            return []

        tags = await Tag.filter(
            name__istartswith=needle,
        ).order_by("name").limit(limit)

        return [TagSuggestion(id=t.id, name=t.name, slug=t.slug) for t in tags]

    async def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag from the database."""
        Tag = self._tag_model()
        tag = await Tag.get_or_none(id=tag_id)
        if tag is None:
            return False

        await tag.delete()
        logger.info("Deleted tag: %s", tag.name)
        return True

    async def resolve_conflicts(self, tag_ids: set[int]) -> TagConflictResolution:
        """Remove redundant parent tags when child tags are present."""
        Tag = self._tag_model()
        tags = {t.id: t async for t in Tag.filter(id__in=list(tag_ids))}
        kept = set(tags.keys())
        removed: set[int] = set()

        for tag_id in list(kept):
            tag = tags[tag_id]
            parent_id = tag.parent_tag_id  # type: ignore[attr-defined]
            if parent_id in kept:
                kept.discard(parent_id)
                removed.add(parent_id)

        return TagConflictResolution(
            kept_tag_ids=sorted(kept),
            removed_tag_ids=sorted(removed),
        )

    async def get_stats(self) -> dict[str, int | dict[str, int]]:
        """Get tag statistics."""
        Tag = self._tag_model()
        total_tags = await Tag.all().count()

        by_color: dict[str, int] = {}
        for color in TagColor:
            count = await Tag.filter(color=color).count()
            if count:
                by_color[color.value] = count

        return {
            "total_tags": total_tags,
            "by_color": by_color,
        }
