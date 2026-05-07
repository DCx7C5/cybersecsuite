"""Bridge DomainEvent → OTEL spans for zero-effort observability.

Converts domain events into OpenTelemetry trace spans grouped by correlation_id.
Events sharing the same correlation_id are grouped into a single trace tree.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Optional

from .store import EventStore
from .types import DomainEvent

log = logging.getLogger(__name__)


class OtelBridge:
    """Bridge DomainEvents to OpenTelemetry spans.
    
    Groups events by correlation_id into single trace trees.
    Emits spans for each event with parent-child relationships.
    
    Usage::
        bridge = OtelBridge()
        event = event_team_spawned("team-1", "Red Team", ["alice", "bob"])
        span = bridge.event_to_span(event, parent_span_id=None)
    """
    
    def __init__(self, tracer_provider: Optional[Any] = None):
        """Initialize bridge with optional tracer provider.
        
        Args:
            tracer_provider: OpenTelemetry TracerProvider (uses global if None)
        """
        self.tracer_provider = tracer_provider
        self._traces: dict[str, list[dict[str, Any]]] = {}
    
    def event_to_span(
        self,
        event: DomainEvent,
        parent_span_id: str | None = None,
    ) -> dict[str, Any]:
        """Convert DomainEvent to OTEL span representation.
        
        Args:
            event: DomainEvent to convert
            parent_span_id: Optional parent span ID for linking
        
        Returns:
            Span dict with trace metadata
        """
        correlation_id = event.metadata.get("correlation_id", event.id)
        
        span = {
            "trace_id": correlation_id,
            "span_id": event.id,
            "parent_span_id": parent_span_id,
            "name": self._span_name(event),
            "kind": self._span_kind(event),
            "start_time": event.timestamp.isoformat(),
            "attributes": self._span_attributes(event),
            "status": "OK",
        }
        
        # Track span in trace tree
        if correlation_id not in self._traces:
            self._traces[correlation_id] = []
        self._traces[correlation_id].append(span)
        
        return span
    
    def _span_name(self, event: DomainEvent) -> str:
        """Generate span name from event kind."""
        # Convert "team.spawned" → "team/spawned"
        return event.kind.replace(".", "/")
    
    def _span_kind(self, event: DomainEvent) -> str:
        """Determine span kind based on event."""
        if "delegated" in event.kind or "created" in event.kind:
            return "PRODUCER"
        elif "completed" in event.kind or "spawned" in event.kind:
            return "CONSUMER"
        else:
            return "INTERNAL"
    
    def _span_attributes(self, event: DomainEvent) -> dict[str, Any]:
        """Extract OTEL span attributes from event."""
        return {
            "event.id": event.id,
            "event.kind": event.kind,
            "event.aggregate_type": event.aggregate_type,
            "event.aggregate_id": event.aggregate_id,
            "event.version": event.version,
            "principal_id": event.metadata.get("principal_id", "system"),
            "request_id": event.metadata.get("request_id", ""),
        }
    
    def build_trace_tree(self, correlation_id: str) -> dict[str, Any]:
        """Build complete trace tree for correlation_id.
        
        Args:
            correlation_id: Trace correlation ID
        
        Returns:
            Trace tree with root span and nested children
        """
        if correlation_id not in self._traces:
            return {}
        
        spans = self._traces[correlation_id]
        
        # Find root spans (no parent_span_id)
        root_spans = [s for s in spans if s["parent_span_id"] is None]
        
        # Build tree
        tree = {
            "trace_id": correlation_id,
            "span_count": len(spans),
            "roots": [self._build_span_node(s, spans) for s in root_spans],
        }
        
        return tree
    
    def _build_span_node(
        self,
        span: dict[str, Any],
        all_spans: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build span node with children."""
        children = [
            self._build_span_node(s, all_spans)
            for s in all_spans
            if s["parent_span_id"] == span["span_id"]
        ]
        
        return {
            "span_id": span["span_id"],
            "name": span["name"],
            "kind": span["kind"],
            "start_time": span["start_time"],
            "attributes": span["attributes"],
            "children": children,
        }
    
    def get_traces(self) -> dict[str, list[dict[str, Any]]]:
        """Get all recorded traces grouped by correlation_id."""
        return dict(self._traces)
    
    def clear_traces(self) -> None:
        """Clear all recorded traces."""
        self._traces.clear()


class EventStoreObserver:
    """Observes EventStore for new events and emits OTel spans.
    
    Integrates with ProjectionManager to build traces as events occur.
    """
    
    def __init__(self, event_store: EventStore, otel_bridge: OtelBridge):
        """Initialize observer.
        
        Args:
            event_store: EventStore to observe
            otel_bridge: OtelBridge for span emission
        """
        self.event_store = event_store
        self.otel_bridge = otel_bridge
        self._last_observed_count = 0
    
    def observe(self) -> list[dict[str, Any]]:
        """Poll EventStore for new events and emit spans.
        
        Returns:
            List of newly emitted spans
        """
        current_count = self.event_store.event_count()
        new_spans = []
        
        if current_count > self._last_observed_count:
            new_events = self.event_store.get_all()[self._last_observed_count:]
            for event in new_events:
                span = self.otel_bridge.event_to_span(event)
                new_spans.append(span)
        
        self._last_observed_count = current_count
        return new_spans


__all__ = [
    "OtelBridge",
    "EventStoreObserver",
]
