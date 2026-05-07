"""Lightweight value types for tag APIs and manager operations."""
import msgspec

@msgspec.struct(frozen=True)
class TagSuggestion:
    """Autocomplete suggestion for a tag."""

    id: int
    name: str
    slug: str

@msgspec.struct(frozen=True)
class TagConflictResolution:
    """Result payload after conflict normalization."""

    kept_tag_ids: list[int] = msgspec.field(default_factory=list)
    removed_tag_ids: list[int] = msgspec.field(default_factory=list)
