"""Lightweight value types for tag APIs and manager operations."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TagSuggestion:
    """Autocomplete suggestion for a tag."""

    id: int
    name: str
    slug: str


@dataclass(frozen=True)
class TagConflictResolution:
    """Result payload after conflict normalization."""

    kept_tag_ids: list[int] = field(default_factory=list)
    removed_tag_ids: list[int] = field(default_factory=list)
