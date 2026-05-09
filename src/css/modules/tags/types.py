"""Lightweight value types for tag APIs and manager operations."""
import msgspec


class TagSuggestion(msgspec.Struct, frozen=True):
    """Autocomplete suggestion for a tag."""

    id: int
    name: str
    slug: str

class TagConflictResolution(msgspec.Struct, frozen=True):
    """Result payload after conflict normalization."""

    kept_tag_ids: list[int] = msgspec.field(default_factory=list)
    removed_tag_ids: list[int] = msgspec.field(default_factory=list)
