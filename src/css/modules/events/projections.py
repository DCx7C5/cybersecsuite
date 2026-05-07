"""Read projections from domain event stream.

Projections build read models (denormalized views) from event streams.
Each projection subscribes to specific event kinds and maintains a cache
that can be queried for fast lookups (permissions, audit trail, etc.).

Pattern:
    1. Load events from EventStore by kind
    2. Apply each event to update read model state
    3. Cache result for fast queries
    4. Support rebuild via replay
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar

from .store import EventStore
from .types import DomainEvent

log = logging.getLogger(__name__)

T = TypeVar("T")


class Projection(ABC, Generic[T]):
    """Base class for building read models from event stream.
    
    Subclasses implement _apply() to handle specific event kinds
    and maintain domain-specific read model state.
    """

    def __init__(self, event_store: EventStore):
        """Initialize projection with event store reference.
        
        Args:
            event_store: EventStore to read events from
        """
        self.event_store = event_store
        self._state: T | None = None
    
    @property
    def state(self) -> T:
        """Get current read model state (rebuilds if needed)."""
        if self._state is None:
            self._rebuild()
        return self._state
    
    def _rebuild(self) -> None:
        """Rebuild read model from event stream."""
        self._state = self._initial_state()
        
        for event in self.event_store.get_all():
            if self._handles(event.kind):
                self._apply(event)
    
    @abstractmethod
    def _initial_state(self) -> T:
        """Create initial read model state."""
        pass
    
    @abstractmethod
    def _handles(self, event_kind: str) -> bool:
        """Check if this projection handles an event kind."""
        pass
    
    @abstractmethod
    def _apply(self, event: DomainEvent) -> None:
        """Apply event to read model state."""
        pass
    
    def invalidate(self) -> None:
        """Invalidate cache to force rebuild on next access."""
        self._state = None


class PermissionsProjection(Projection[dict[str, dict[str, bool]]]):
    """Builds current permissions state from permission events.
    
    Read model structure:
        {
            "resource_id:principal_id": {
                "action_name": True/False,
                ...
            },
            ...
        }
    """
    
    def _initial_state(self) -> dict[str, dict[str, bool]]:
        """Start with empty permissions."""
        return {}
    
    def _handles(self, event_kind: str) -> bool:
        """Handle permission events."""
        return event_kind.startswith("permission.")
    
    def _apply(self, event: DomainEvent) -> None:
        """Update permissions based on event."""
        if self._state is None:
            self._state = self._initial_state()
        
        principal_resource = f"{event.data.get('resource_id')}:{event.data.get('principal_id')}"
        action = event.data.get('action', '')
        
        if event.kind == "permission.granted":
            if principal_resource not in self._state:
                self._state[principal_resource] = {}
            self._state[principal_resource][action] = True
        
        elif event.kind == "permission.revoked":
            if principal_resource in self._state:
                self._state[principal_resource][action] = False
    
    def has_permission(self, resource_id: str, principal_id: str, action: str) -> bool:
        """Check if principal has permission for action on resource."""
        key = f"{resource_id}:{principal_id}"
        perms = self.state.get(key, {})
        return perms.get(action, False)
    
    def get_principal_permissions(self, principal_id: str) -> dict[str, dict[str, bool]]:
        """Get all permissions for a principal (across resources)."""
        result = {}
        for key, actions in self.state.items():
            if principal_id in key:
                result[key] = actions
        return result
    
    def get_resource_permissions(self, resource_id: str) -> dict[str, dict[str, bool]]:
        """Get all permissions on a resource (from all principals)."""
        result = {}
        for key, actions in self.state.items():
            if resource_id in key:
                result[key] = actions
        return result


class AuditTrailProjection(Projection[list[dict[str, Any]]]):
    """Builds searchable audit trail from all events.
    
    Read model structure:
        [
            {
                "timestamp": ISO8601,
                "kind": "team.spawned",
                "aggregate_type": "team",
                "aggregate_id": "team-123",
                "data": {...},
                "principal_id": "user-456" (if in metadata),
            },
            ...
        ]
    """
    
    def _initial_state(self) -> list[dict[str, Any]]:
        """Start with empty audit trail."""
        return []
    
    def _handles(self, event_kind: str) -> bool:
        """Handle all events."""
        return True
    
    def _apply(self, event: DomainEvent) -> None:
        """Append event to audit trail."""
        if self._state is None:
            self._state = self._initial_state()
        
        audit_entry = {
            "timestamp": event.timestamp.isoformat(),
            "kind": event.kind,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": event.aggregate_id,
            "data": event.data,
            "principal_id": event.metadata.get("principal_id", "system"),
            "request_id": event.metadata.get("request_id"),
        }
        self._state.append(audit_entry)
    
    def get_events_for_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: str,
    ) -> list[dict[str, Any]]:
        """Get audit trail for specific aggregate."""
        return [
            entry
            for entry in self.state
            if entry["aggregate_type"] == aggregate_type and entry["aggregate_id"] == aggregate_id
        ]
    
    def get_events_since(self, timestamp: datetime) -> list[dict[str, Any]]:
        """Get audit trail since timestamp."""
        timestamp_str = timestamp.isoformat()
        return [entry for entry in self.state if entry["timestamp"] >= timestamp_str]
    
    def get_events_by_principal(self, principal_id: str) -> list[dict[str, Any]]:
        """Get audit trail for specific principal."""
        return [entry for entry in self.state if entry["principal_id"] == principal_id]
    
    def get_events_by_kind(self, kind: str) -> list[dict[str, Any]]:
        """Get audit trail filtered by event kind."""
        return [entry for entry in self.state if entry["kind"] == kind]


class ProjectionManager:
    """Manages multiple projections for coordinated reads.
    
    Usage::
        event_store = EventStore()
        mgr = ProjectionManager(event_store)
        
        # Access projections
        mgr.permissions.has_permission("res-1", "usr-1", "read")
        mgr.audit_trail.get_events_by_principal("usr-1")
        
        # Rebuild after events
        mgr.rebuild()
    """
    
    def __init__(self, event_store: EventStore):
        """Initialize manager with event store."""
        self.event_store = event_store
        self.permissions = PermissionsProjection(event_store)
        self.audit_trail = AuditTrailProjection(event_store)
    
    def rebuild(self) -> None:
        """Rebuild all projections from event stream."""
        self.permissions.invalidate()
        self.audit_trail.invalidate()
        
        # Trigger rebuild by accessing state
        _ = self.permissions.state
        _ = self.audit_trail.state
        
        log.info(f"Rebuilt projections with {self.event_store.event_count()} events")


__all__ = [
    "Projection",
    "PermissionsProjection",
    "AuditTrailProjection",
    "ProjectionManager",
]
