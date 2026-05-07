"""Tag management and assignment."""

import logging
import re
from typing import Any
from datetime import datetime

from .models import Tag
from .enums import TagColor
from .exceptions import TagNotFoundError, TagCreationError, TagValidationError
from .types import TagConflictResolution, TagSuggestion

logger = logging.getLogger(__name__)


def normalize_slug(text: str) -> str:
    """Normalize text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\-_]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


class TagManager:
    """Manages tags and tag assignments."""
    
    def __init__(self):
        """Initialize tag manager."""
        self._tags: dict[int, Tag] = {}
        self._slug_index: dict[str, int] = {}
        self._assignments: dict[str, set[int]] = {}  # resource_type:resource_id -> set of tag IDs
    
    async def create_tag(
        self,
        name: str,
        color: TagColor = TagColor.GRAY,
        description: str = "",
        parent_tag_id: int | None = None,
    ) -> Tag:
        """Create a new tag."""
        # Validation
        if not name or len(name) > 128:
            raise TagValidationError("Tag name must be 1-128 characters", field="name")
        
        if not re.match(r'^[\w\s\-]+$', name):
            raise TagValidationError("Tag name contains invalid characters", field="name")
        
        slug = normalize_slug(name)
        
        if slug in self._slug_index:
            raise TagCreationError(f"Tag already exists: {name}", tag_name=name)
        
        parent_tag = self._tags.get(parent_tag_id) if parent_tag_id else None
        if parent_tag_id and parent_tag is None:
            raise TagNotFoundError(str(parent_tag_id))

        # Create tag (simulated - in production would use DB)
        tag_id = len(self._tags) + 1
        tag = Tag(
            id=tag_id,
            name=name,
            slug=slug,
            color=color,
            parent_tag=parent_tag,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self._tags[tag_id] = tag
        self._slug_index[slug] = tag_id
        
        logger.info(f"Created tag: {name} (slug: {slug})")
        return tag
    
    async def get_tag(self, tag_id: int) -> Tag | None:
        """Get tag by ID."""
        return self._tags.get(tag_id)
    
    async def get_tag_by_slug(self, slug: str) -> Tag | None:
        """Get tag by slug."""
        tag_id = self._slug_index.get(slug)
        if tag_id:
            return self._tags.get(tag_id)
        return None
    
    async def get_tag_or_fail(self, tag_id: int) -> Tag:
        """Get tag by ID or raise error."""
        tag = self._tags.get(tag_id)
        if not tag:
            raise TagNotFoundError(tag_id)
        return tag
    
    async def list_tags(self, color: TagColor = None) -> list[Tag]:
        """List tags with optional filtering."""
        tags = list(self._tags.values())
        
        if color:
            tags = [t for t in tags if t.color == color]
        
        return sorted(tags, key=lambda t: t.name)
    
    async def search_tags(self, query: str) -> list[Tag]:
        """Search tags by name or description."""
        query_lower = query.lower()
        matches = []
        
        for tag in self._tags.values():
            if query_lower in tag.name.lower() or query_lower in tag.description.lower():
                matches.append(tag)
        
        return sorted(matches, key=lambda t: t.name)

    async def suggest_tags(self, prefix: str, limit: int = 10) -> list[TagSuggestion]:
        """Suggest tags by prefix for autocomplete UX."""
        needle = prefix.strip().lower()
        if not needle:
            return []

        suggestions: list[TagSuggestion] = []
        for tag in sorted(self._tags.values(), key=lambda t: t.name):
            if tag.name.lower().startswith(needle) or tag.slug.startswith(needle):
                suggestions.append(TagSuggestion(id=tag.id, name=tag.name, slug=tag.slug))
            if len(suggestions) >= limit:
                break

        return suggestions
    
    async def assign_tag(self, tag_id: int, resource_key: str) -> None:
        """Assign tag to a resource."""
        tag = await self.get_tag_or_fail(tag_id)
        
        if resource_key not in self._assignments:
            self._assignments[resource_key] = set()
        
        self._assignments[resource_key].add(tag_id)
        logger.debug(f"Assigned tag {tag.name} to {resource_key}")
    
    async def unassign_tag(self, tag_id: int, resource_key: str) -> None:
        """Unassign tag from a resource."""
        tag = await self.get_tag_or_fail(tag_id)
        
        if resource_key in self._assignments:
            self._assignments[resource_key].discard(tag_id)
            logger.debug(f"Unassigned tag {tag.name} from {resource_key}")
    
    async def get_resource_tags(self, resource_key: str) -> list[Tag]:
        """Get all tags assigned to a resource."""
        tag_ids = self._assignments.get(resource_key, set())
        return [self._tags[tid] for tid in sorted(tag_ids) if tid in self._tags]
    
    async def find_resources_by_tag(self, tag_id: int) -> list[str]:
        """Find all resources with a specific tag."""
        await self.get_tag_or_fail(tag_id)
        
        resources = []
        for resource_key, tag_ids in self._assignments.items():
            if tag_id in tag_ids:
                resources.append(resource_key)
        
        return sorted(resources)
    
    async def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        if tag_id not in self._tags:
            return False
        
        tag = self._tags[tag_id]
        
        # Remove from assignments
        keys_to_clean = []
        for resource_key, tag_ids in self._assignments.items():
            tag_ids.discard(tag_id)
            if not tag_ids:
                keys_to_clean.append(resource_key)
        
        for key in keys_to_clean:
            del self._assignments[key]
        
        # Remove from indices
        del self._tags[tag_id]
        del self._slug_index[tag.slug]
        
        logger.info(f"Deleted tag: {tag.name}")
        return True

    async def resolve_conflicts(self, tag_ids: set[int]) -> TagConflictResolution:
        """Remove redundant parent tags when child tags are present."""
        kept = {tid for tid in tag_ids if tid in self._tags}
        removed: set[int] = set()

        for tag_id in list(kept):
            tag = self._tags[tag_id]
            parent = getattr(tag, "parent_tag", None)
            parent_id = getattr(parent, "id", None)
            if parent_id in kept:
                kept.discard(parent_id)
                removed.add(parent_id)

        return TagConflictResolution(
            kept_tag_ids=sorted(kept),
            removed_tag_ids=sorted(removed),
        )
    
    async def get_stats(self) -> dict[str, Any]:
        """Get tag statistics."""
        total_tags = len(self._tags)
        
        # Count by color
        by_color = {}
        for tag in self._tags.values():
            color_key = tag.color.value
            by_color[color_key] = by_color.get(color_key, 0) + 1
        
        # Count assignments
        total_assignments = sum(len(tag_ids) for tag_ids in self._assignments.values())
        
        return {
            "total_tags": total_tags,
            "by_color": by_color,
            "total_assignments": total_assignments,
            "avg_tags_per_resource": (total_assignments / len(self._assignments)) if self._assignments else 0,
        }
