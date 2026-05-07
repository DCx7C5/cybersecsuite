"""In-memory EventStore for domain event persistence and replay."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from .types import DomainEvent

log = logging.getLogger(__name__)


class EventStore:
    """In-memory event store with append-only semantics.

    Used for:
    1. Persisting all domain events atomically
    2. Replay for read model construction
    3. Audit trail and forensic reconstruction
    4. Idempotency (via event deduplication)
    """

    def __init__(self) -> None:
        """Initialize empty event stream."""
        self._events: list[DomainEvent] = []
        self._by_aggregate: dict[str, list[DomainEvent]] = defaultdict(list)
        self._by_kind: dict[str, list[DomainEvent]] = defaultdict(list)
        self._event_keys: set[str] = set()

    def append(self, event: DomainEvent) -> bool:
        """Append event to store (idempotent).

        Args:
            event: DomainEvent to append

        Returns:
            True if appended, False if duplicate
        """
        key = event.event_key
        if key in self._event_keys:
            log.debug(f"Ignoring duplicate event: {key}")
            return False

        self._events.append(event)
        agg_key = f"{event.aggregate_type}:{event.aggregate_id}"
        self._by_aggregate[agg_key].append(event)
        self._by_kind[event.kind].append(event)
        self._event_keys.add(key)

        log.debug(f"Appended event: {event.kind} (aggregate={agg_key})")
        return True

    def get_all(self) -> list[DomainEvent]:
        """Get all events in order."""
        return list(self._events)

    def get_by_aggregate(self, aggregate_type: str, aggregate_id: str) -> list[DomainEvent]:
        """Get all events for a specific aggregate."""
        key = f"{aggregate_type}:{aggregate_id}"
        return list(self._by_aggregate.get(key, []))

    def get_by_kind(self, kind: str) -> list[DomainEvent]:
        """Get all events of a specific kind."""
        return list(self._by_kind.get(kind, []))

    def get_since(self, timestamp: datetime) -> list[DomainEvent]:
        """Get all events since a timestamp."""
        return [e for e in self._events if e.timestamp >= timestamp]

    def event_count(self) -> int:
        """Get total event count."""
        return len(self._events)

    def clear(self) -> None:
        """Clear all events (for testing)."""
        self._events.clear()
        self._by_aggregate.clear()
        self._by_kind.clear()
        self._event_keys.clear()


__all__ = ["EventStore"]
