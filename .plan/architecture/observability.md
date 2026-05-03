# PLAN: Observability & Events Architecture

**Objective**: Design and implement BaseEvent system + OpenTelemetry integration for comprehensive observability

**Status**: 📋 Planning Phase

---

## Problem Statement

CyberSecSuite requires comprehensive observability across:
- **Events** — First-class events for all significant operations (task execution, permission checks, role changes, etc.)
- **Tracing** — Distributed tracing with correlation IDs across services
- **Metrics** — Performance metrics (latency, throughput, error rates)
- **Logging** — Structured logging with context propagation
- **Backends** — OpenObserve (open-source observability platform) for centralized collection

Currently:
- Hooks exist (`HookContext`, `HookErrorStrategy`) but no unified event system
- Logger exists but not integrated with OpenTelemetry
- No tracing infrastructure
- No OpenObserve backend integration
- No metrics collection

---

## Proposed Architecture (Unified Approach)

### System Design

```
┌──────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│  (Modules: chat, capabilities, marketplace, permissions, etc.)   │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ├─ Emit: event = BaseEvent(...)
           │ 
           └─→ ┌────────────────────────────────────────────────┐
               │      Unified Event & Hook System               │
               │         (@modules:events)                      │
               │                                                │
               ├─ BaseEvent (event model)                       │
               ├─ EventType (20+ event types)                   │
               ├─ EventContext (metadata)                       │
               ├─ EventBus (pub/sub emitter)                    │
               ├─ EventDispatcher (route to handlers)           │
               ├─ Hook registry (pre/post hooks)                │
               ├─ @on_event decorator (subscribe to events)     │
               ├─ @on_hook decorator (register hooks)           │
               └─ Hook execution logic (error handling)         │
               │                                                │
               ├─→ Event Handlers Execute                       │
               │   ├─ Hook functions                           │
               │   ├─ Event listeners (@on_event subscribers)   │
               │   └─ Observability middleware                  │
               │                                                │
               └─→ ┌────────────────────────────────────────────┐
                   │ OpenTelemetry Integration                  │
                   │    (@core:opentelemetry)                   │
                   │                                            │
                   ├─ Convert BaseEvent → OTel span             │
                   ├─ Track metrics (counters, histograms)      │
                   ├─ OTLP exporter                             │
                   └─ Tracer/Meter initialization               │
                   │                                            │
                   └─→ ┌─────────────────────────────┐         │
                       │   OpenObserve Backend       │         │
                       │   (HTTP/OTLP Collector)    │         │
                       │                             │         │
                       ├─ Traces (spans)            │         │
                       ├─ Metrics (gauges, counters)│         │
                       ├─ Logs (structured)         │         │
                       └─ Events (custom)           │         │
                       └─────────────────────────────┘         │
```

### Key Decision: Unified @modules:events
- **Events and hooks are integrated** (hooks are event handlers)
- **Single BaseEvent model** used for all event types
- **Single EventBus** handles both pub/sub and hook registration
- **Single dispatcher** routes events to hooks, listeners, and observability
- **Clear data flow**: action → BaseEvent → handler execution → OTel export

---

## Phase 1: BaseEvent System in @modules:events

### Unified Events Module Location
**Location**: `src/css/modules/events/` (NOT @core:events)

This is the user-facing event system where all event types, hook registration, and pub/sub happens.

### BaseEvent Model

**Location**: `src/css/modules/events/base.py` (NEW)

```python
@dataclass
class BaseEvent:
    """Base event for all observability events.
    
    Events are immutable records of significant operations.
    Can be consumed by hooks, emitted to tracing, exported to observability backend.
    """
    
    # Identity
    event_id: str  # UUID
    event_type: EventType  # e.g., TASK_EXECUTED, PERMISSION_CHECKED
    source: str  # Module name (e.g., "marketplace", "chat", "capabilities")
    timestamp: float  # Seconds since epoch
    
    # Tracing
    correlation_id: str  # Links related events across services
    parent_span_id: Optional[str] = None  # Parent trace context
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: Optional[str] = None
    
    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    scope_id: Optional[str] = None
    role_id: Optional[str] = None
    
    # Data
    data: dict[str, Any] = field(default_factory=dict)  # Event-specific data
    metadata: dict[str, str] = field(default_factory=dict)  # Tags, labels
    
    # Status
    status: EventStatus = EventStatus.COMPLETED  # COMPLETED, FAILED, PENDING
    duration_ms: Optional[int] = None  # For completed events
    error: Optional[str] = None  # Error message if failed
    
    # Severity
    severity: EventSeverity = EventSeverity.INFO  # DEBUG, INFO, WARN, ERROR, CRITICAL
```

### EventType Enum

```python
class EventType(str, Enum):
    # Task/Execution events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_RETRIED = "task.retried"
    
    # Permission events
    PERMISSION_CHECKED = "permission.checked"
    PERMISSION_DENIED = "permission.denied"
    PERMISSION_GRANTED = "permission.granted"
    ROLE_ASSIGNED = "role.assigned"
    
    # Tool/Agent events
    TOOL_EXECUTED = "tool.executed"
    AGENT_SPAWNED = "agent.spawned"
    AGENT_TERMINATED = "agent.terminated"
    
    # Communication events
    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"
    A2A_REQUEST = "a2a.request"
    A2A_RESPONSE = "a2a.response"
    
    # Marketplace events
    PACKAGE_INSTALLED = "package.installed"
    PACKAGE_REMOVED = "package.removed"
    INDEX_UPDATED = "index.updated"
    
    # System events
    APP_STARTED = "app.started"
    APP_STOPPED = "app.stopped"
    DB_CONNECTED = "db.connected"
    DB_ERROR = "db.error"
```

### EventContext

```python
@dataclass
class EventContext:
    """Metadata for event emission."""
    correlation_id: str  # From request header or generate
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
```

### EventStatus & EventSeverity Enums

```python
class EventStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"

class EventSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"
```

---

### Phase 2: OpenTelemetry Integration in @core

### OpenTelemetry Setup

**Location**: `src/css/core/opentelemetry/` (NEW PACKAGE)

#### `__init__.py`

```python
"""OpenTelemetry initialization and utilities."""

from .config import init_otel, get_tracer, get_meter, get_logger_provider
from .exporters import setup_otlp_exporter
from .instrumentation import setup_auto_instrumentation

__all__ = [
    "init_otel",
    "get_tracer",
    "get_meter",
    "get_logger_provider",
    "setup_otlp_exporter",
    "setup_auto_instrumentation",
]
```

#### `config.py`

```python
"""OpenTelemetry configuration."""

from opentelemetry import trace, metrics, logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
import os


def init_otel(service_name: str = "cybersecsuite"):
    """Initialize OpenTelemetry with OTLP exporter."""
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("ENV", "development"),
    })
    
    # Tracer setup
    tracer_provider = TracerProvider(resource=resource)
    otlp_span_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
        insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Meter setup
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
    ))
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    
    # Logger setup
    logger_provider = LoggerProvider(resource=resource)
    otlp_log_exporter = OTLPLogExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
    logs.set_logger_provider(logger_provider)


def get_tracer(name: str) -> trace.Tracer:
    """Get tracer for a module."""
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """Get meter for a module."""
    return metrics.get_meter(name)


def get_logger_provider() -> LoggerProvider:
    """Get logger provider."""
    return logs.get_logger_provider()
```

#### `instrumentation.py`

```python
"""Auto-instrumentation setup."""

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def setup_auto_instrumentation():
    """Setup automatic instrumentation for frameworks."""
    
    # FastAPI instrumentation
    FastAPIInstrumentor().instrument()
    
    # HTTP client instrumentation
    HTTPXClientInstrumentor().instrument()
    
    # SQLAlchemy instrumentation
    SQLAlchemyInstrumentor().instrument()
```

---

## Phase 3: Event System Integration

### Event System in @modules:events

**Location**: `src/css/modules/events/` (already exists, will be enhanced)

#### `emitter.py`

```python
"""Event emission system."""

from typing import Callable, List
from css.core.types.events import BaseEvent


class EventEmitter:
    """Centralized event emission."""
    
    def __init__(self):
        self._listeners: dict[str, List[Callable]] = {}
    
    def on(self, event_type: str, callback: Callable) -> None:
        """Register listener for event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def emit(self, event: BaseEvent) -> None:
        """Emit event to all registered listeners."""
        listeners = self._listeners.get(event.event_type, [])
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                log.error(f"Event listener failed: {e}", exc_info=True)
```

### Event to OpenTelemetry Converter

#### `converter.py`

```python
"""Convert BaseEvent to OpenTelemetry spans/metrics."""

from opentelemetry import trace, metrics
from css.core.types.events import BaseEvent, EventType, EventStatus


def event_to_span(event: BaseEvent, tracer):
    """Convert BaseEvent to OTel span."""
    
    with tracer.start_as_current_span(
        f"{event.source}.{event.event_type}",
        attributes={
            "event.id": event.event_id,
            "event.type": event.event_type,
            "event.source": event.source,
            "event.status": event.status,
            "event.severity": event.severity,
            "user.id": event.user_id,
            "session.id": event.session_id,
            "role.id": event.role_id,
            **event.metadata,
        }
    ) as span:
        if event.duration_ms:
            span.set_attribute("event.duration_ms", event.duration_ms)
        if event.error:
            span.set_attribute("event.error", event.error)
        return span


def event_to_metric(event: BaseEvent, meter):
    """Convert BaseEvent to OTel metric (counter/histogram)."""
    
    counter = meter.create_counter(
        f"event.{event.event_type.replace('.', '_')}.total",
        description=f"Count of {event.event_type} events",
    )
    counter.add(1, {"source": event.source, "status": event.status})
    
    if event.duration_ms:
        histogram = meter.create_histogram(
            f"event.{event.event_type.replace('.', '_')}.duration_ms",
            description=f"Duration of {event.event_type} events",
        )
        histogram.record(event.duration_ms, {"source": event.source})
```

---

## Phase 4: Hook + Event Integration

### Enhanced Hooks with Events

**Location**: `src/css/core/hooks/` (ENHANCED)

```python
"""Hooks that emit events."""

from css.core.types.events import BaseEvent, EventType, EventContext
from css.core.events import EventEmitter


class HookWithEvents:
    """Hook system integrated with event emission."""
    
    def __init__(self, event_emitter: EventEmitter):
        self.emitter = event_emitter
    
    async def execute_hook(self, hook_name: str, *args, **kwargs):
        """Execute hook and emit event."""
        
        context = EventContext(
            correlation_id=kwargs.get("correlation_id"),
            session_id=kwargs.get("session_id"),
            user_id=kwargs.get("user_id"),
        )
        
        event = BaseEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.HOOK_EXECUTED,
            source="hooks",
            timestamp=time.time(),
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            user_id=context.user_id,
            data={"hook_name": hook_name},
        )
        
        try:
            result = await hook_name(*args, **kwargs)
            event.status = EventStatus.COMPLETED
            self.emitter.emit(event)
            return result
        except Exception as e:
            event.status = EventStatus.FAILED
            event.error = str(e)
            self.emitter.emit(event)
            raise
```

---

## Phase 5: OpenObserve Integration

### Docker Compose Entry

**docker-compose.yml**:

```yaml
  openobserve:
    image: public.ecr.aws/zinclabs/openobserve:latest
    container_name: openobserve
    ports:
      - "5080:5080"  # Web UI
      - "4318:4318"  # OTLP HTTP
    environment:
      ZO_ROOT_USER_EMAIL: admin@example.com
      ZO_ROOT_USER_PASSWORD: Changeme@123
      ZO_DATA_DIR: ./data/openobserve
    volumes:
      - openobserve_data:/data
    networks:
      - cybersec

volumes:
  openobserve_data:
```

### Configuration

**Environment Variables**:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://openobserve:4318
OTEL_SERVICE_NAME=cybersecsuite
OTEL_ENABLED=true
```

---

## Todos (10 Tasks)

### Phase 1: BaseEvent System

- [ ] **event-types-enum** — Create EventType enum with all event types
- [ ] **event-model** — Create BaseEvent dataclass with all fields
- [ ] **event-status-severity** — Create EventStatus, EventSeverity enums
- [ ] **event-context** — Create EventContext class
- [ ] **event-exports** — Update types/__init__.py to export events

### Phase 2: OpenTelemetry Core

- [ ] **otel-config** — Create opentelemetry/config.py (init_otel, get_tracer, get_meter)
- [ ] **otel-exporter** — Create opentelemetry/exporters.py (OTLP setup)
- [ ] **otel-instrumentation** — Create opentelemetry/instrumentation.py (FastAPI, HTTPx, SQLAlchemy)
- [ ] **otel-init** — Call init_otel from app startup

### Phase 3: Event System

- [ ] **event-emitter** — Create events/emitter.py (EventEmitter class)
- [ ] **event-converter** — Create events/converter.py (BaseEvent → OTel conversion)
- [ ] **event-dispatcher** — Create events/dispatcher.py (route events to handlers)

### Phase 4: Integration

- [ ] **hooks-events** — Integrate hooks with BaseEvent emission
- [ ] **permission-events** — Emit events for permission checks/denials
- [ ] **task-events** — Emit events for task execution
- [ ] **openobserve-docker** — Add OpenObserve to docker-compose.yml

---

## Key Integration Points

| Component | Emits Events | Consumes Events | Notes |
|-----------|-------------|-----------------|-------|
| @core:hooks | Yes | Yes | Hook callbacks emit events |
| @core:permissions | Yes | No | Permission checks → events |
| @core:tasks | Yes | No | Task execution → events |
| @core:events | Yes (dispatcher) | Yes | Central event hub |
| @core:opentelemetry | No | Yes | Events → OTel spans/metrics |
| All modules | Yes | No | Module actions → events |

---

## Success Criteria

✅ BaseEvent model fully defined with all fields
✅ EventType enum covers all major operations
✅ OpenTelemetry initialized on app startup
✅ OTLP exporter sending to OpenObserve
✅ Events emitted from hooks, permissions, tasks
✅ Events converted to OTel spans and metrics
✅ OpenObserve dashboard shows events/traces
✅ Correlation IDs propagate across requests
✅ Duration tracking for events
✅ Error tracking and reporting

---

## Architecture Diagram

```
Application
    ↓
BaseEvent emission
    ↓
EventEmitter
    ├→ Hooks (consume)
    ├→ Database (store)
    └→ Converter
         ↓
    OpenTelemetry
    ├─ Tracer (spans)
    ├─ Meter (metrics)
    └─ Logger
         ↓
    OTLP Exporter
         ↓
    OpenObserve Collector
         ↓
    OpenObserve Backend
    ├─ Dashboard
    ├─ Traces
    ├─ Metrics
    └─ Logs
```

---

## DECISION: Unified @modules:events Architecture

See: `.plan/hooks-vs-events-analysis.md` for full analysis.

**Conclusion**: Use unified @modules:events for all event + hook management.

**Key Points**:
- BaseEvent and hooks are integrated (hooks ARE event handlers)
- Single EventBus handles pub/sub and hook registration  
- Single dispatcher routes events to hooks, listeners, and observability
- Clear data flow: action → BaseEvent → handler → OTel export

**Module Structure**:
```
@modules:events/
├─ base.py          (BaseEvent, EventType, EventStatus)
├─ emitter.py       (EventBus, hook registry)
├─ hooks.py         (hook execution)
├─ dispatcher.py    (route events)
├─ decorators.py    (@on_event, @on_hook)
├─ registry.py      (global registry)
└─ __init__.py      (exports)

@core:opentelemetry/  (OTel infrastructure)
├─ config.py         (init_otel)
├─ exporters.py      (OTLP)
└─ instrumentation.py (auto-instrumentation)

@core:events/         (Thin middleware for OTel)
├─ converter.py      (BaseEvent → OTel)
└─ middleware.py     (auto-convert + export)
```
