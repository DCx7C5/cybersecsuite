# Observability & Events Architecture

**Status**: 🚀 Phase 6 — Proposals 3 + 5 (CQRS Event Store + OTEL Bridge)
**Updated**: 2026-05-04 (session 9a5b41c4)

> ⚠️ **ARCHITECTURE TRANSITION**: Target design is `DomainEvent` (immutable) → `EventStore`
> (PostgreSQL) → Redis Streams → `OtelBridge` → OpenObserve. Runtime compatibility surfaces
> (`EventBus`, `@on_event`) are still active until all Phase 14/6 wiring is complete.

---

## System Design

```
Application Layer (modules: chat, tasks, teams, agents, marketplace, permissions)
  │
  │  emit: await event_store.append(DomainEvent(...))
  │
  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    EventStore (core/events/store.py)                 │
│                                                                      │
│  1. Write DomainEvent to PostgreSQL (DomainEventRecord table)        │
│  2. XADD to Redis Streams  css:events  (fan-out)                     │
│  3. Return event_id                                                  │
└──────┬───────────────────────────────────────────────────────────────┘
       │  Redis Streams: css:events (fan-out to all consumers)
       │
   ┌───┴────────────────────────────────────┐
   │                                        │
   ▼                                        ▼
┌──────────────────────┐          ┌────────────────────────────┐
│   OtelBridge         │          │   Read Projections         │
│ (core/events/otel.py)│          │ (core/permissions/,     │
│                      │          │  core/events/)          │
│  DomainEvent         │          │                            │
│  → OTEL span         │          │  PermissionProjection:     │
│  (event_type→name,   │          │  rebuilds agent permissions│
│   correlation_id     │          │  from event stream         │
│   →trace_id,         │          │                            │
│   aggregate_id       │          │  AuditProjection:          │
│   →attributes)       │          │  materializes audit log    │
│                      │          │  for forensic replay       │
└──────┬───────────────┘          └────────────────────────────┘
       │
       ▼
┌──────────────────────┐
│   OTLP Exporter      │
│   (OpenTelemetry)    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   OpenObserve        │
│   :5080              │
│                      │
│  • Traces (spans)    │
│  • Metrics           │
│  • Structured logs   │
│  • Events timeline   │
└──────────────────────┘
```

---

## DomainEvent (msgspec.Struct)

```python
# core/events/domain_event.py
import msgspec
import uuid
import time

class DomainEvent(msgspec.Struct, frozen=True):
    """Immutable domain event. Every state change in the system emits one."""
    event_type: str          # "team.spawned", "task.delegated", "agent.action"
    aggregate_id: str        # ID of the entity this event is about
    aggregate_type: str      # "team", "task", "agent", "permission"
    payload: dict            # Event-specific data (arbitrary JSON)
    
    # Auto-populated
    event_id: str = msgspec.field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: float = msgspec.field(default_factory=time.time)
    
    # Correlation / tracing
    correlation_id: str | None = None   # links events in a single request
    session_id: str | None = None
    agent_id: str | None = None
    team_id: str | None = None

# Canonical event type constants
class EventType:
    # Teams
    TEAM_SPAWNED = "team.spawned"
    TEAM_SHUTDOWN = "team.shutdown"
    TEAM_CRASHED = "team.crashed"
    
    # Tasks
    TASK_DELEGATED = "task.delegated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_REASSIGNED = "task.reassigned"
    
    # Agents
    AGENT_ACTION = "agent.action"
    AGENT_ERROR = "agent.error"
    
    # Permissions
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_REVOKED = "permission.revoked"
    PERMISSION_DENIED = "permission.denied"
    
    # Marketplace
    MARKETPLACE_INSTALL = "marketplace.install"
    MARKETPLACE_UNINSTALL = "marketplace.uninstall"
    
    # LLM calls
    LLM_CALL_START = "llm.call.start"
    LLM_CALL_COMPLETE = "llm.call.complete"
    LLM_CALL_ERROR = "llm.call.error"
    LLM_CACHE_HIT = "llm.cache.hit"
```

---

## EventStore

```python
# core/events/store.py
class EventStore:
    """Write-once event log. PostgreSQL + Redis Streams fan-out."""

    def __init__(self, redis: Redis, tortoise_conn):
        self._redis = redis
        self._db = tortoise_conn

    async def append(self, event: DomainEvent) -> str:
        # 1. Persist to PostgreSQL
        await DomainEventRecord.create(
            event_id=event.event_id,
            event_type=event.event_type,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            payload=event.payload,
            correlation_id=event.correlation_id,
            session_id=event.session_id,
            agent_id=event.agent_id,
            occurred_at=event.occurred_at,
        )
        
        # 2. Fan-out to Redis Streams (all consumers)
        await self._redis.xadd(
            "css:events",
            msgspec.json.encode(event),
            maxlen=100_000  # rolling window
        )
        
        return event.event_id

    async def replay(
        self,
        aggregate_id: str,
        until: float | None = None,
    ) -> list[DomainEvent]:
        """Replay all events for an aggregate. Core forensic tool."""
        qs = DomainEventRecord.filter(aggregate_id=aggregate_id)
        if until:
            qs = qs.filter(occurred_at__lte=until)
        records = await qs.order_by("occurred_at").values()
        return [DomainEvent(**r) for r in records]

    async def replay_session(self, session_id: str) -> list[DomainEvent]:
        """Replay every event in a session — full forensic audit."""
        records = await DomainEventRecord.filter(
            session_id=session_id
        ).order_by("occurred_at").values()
        return [DomainEvent(**r) for r in records]
```

---

## CommandBus + CQRS

```python
# core/events/commands.py
class CommandBus:
    """Dispatch commands → handlers → list[DomainEvent] → EventStore.append."""

    def __init__(self, event_store: EventStore):
        self._store = event_store
        self._handlers: dict[type, Callable] = {}

    def register(self, command_type: type, handler: Callable):
        self._handlers[command_type] = handler

    async def dispatch(self, command) -> list[DomainEvent]:
        handler = self._handlers[type(command)]
        events = await handler(command)        # handler returns list[DomainEvent]
        for event in events:
            await self._store.append(event)
        return events

# Example command + handler
@dataclass
class SpawnTeamCommand:
    team_name: str
    session_id: str
    roles: list[str]

async def handle_spawn_team(cmd: SpawnTeamCommand) -> list[DomainEvent]:
    team_id = str(uuid.uuid4())
    return [
        DomainEvent(
            event_type=EventType.TEAM_SPAWNED,
            aggregate_id=team_id,
            aggregate_type="team",
            payload={"name": cmd.team_name, "roles": cmd.roles},
            session_id=cmd.session_id,
        )
    ]
```

---

## OTEL Bridge (implements the otel stub)

```python
# core/events/otel_bridge.py
# ~50 LOC — implements entire @otel module via event stream
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

class OtelBridge:
    """Subscribe to Redis Streams css:events → emit OTEL spans.
    
    Replaces the empty @otel stub with zero-effort observability:
    every DomainEvent automatically becomes a trace span.
    """

    def __init__(self, redis: Redis, otlp_endpoint: str):
        provider = TracerProvider()
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
        )
        self._tracer = trace.get_tracer("css.events")
        self._redis = redis

    async def run(self):
        """Consume css:events stream and emit OTEL spans continuously."""
        last_id = "0"
        while True:
            entries = await self._redis.xread({"css:events": last_id}, count=100, block=1000)
            for _, messages in entries:
                for msg_id, data in messages:
                    event = msgspec.json.decode(data[b"data"], type=DomainEvent)
                    self._emit_span(event)
                    last_id = msg_id

    def _emit_span(self, event: DomainEvent):
        ctx = self._make_trace_context(event.correlation_id)
        with self._tracer.start_as_current_span(
            event.event_type,
            context=ctx,
            attributes={
                "aggregate.id": event.aggregate_id,
                "aggregate.type": event.aggregate_type,
                "session.id": event.session_id or "",
                "agent.id": event.agent_id or "",
                "team.id": event.team_id or "",
            }
        ):
            pass  # span ends on context exit, duration = 0 for discrete events
```

---

## Read Projections

```python
# core/permissions/projections.py
class PermissionProjection:
    """Rebuild permission state from event stream. Replaces static RBAC tables."""

    def __init__(self, event_store: EventStore):
        self._store = event_store
        self._cache: dict[str, set[str]] = {}  # agent_id → set of granted permissions

    async def get_permissions(self, agent_id: str) -> set[str]:
        if agent_id in self._cache:
            return self._cache[agent_id]
        
        events = await self._store.replay(aggregate_id=agent_id)
        permissions = set()
        for event in events:
            if event.event_type == EventType.PERMISSION_GRANTED:
                permissions.add(event.payload["permission"])
            elif event.event_type == EventType.PERMISSION_REVOKED:
                permissions.discard(event.payload["permission"])
        
        self._cache[agent_id] = permissions
        return permissions
```

---

## PostgreSQL Schema

```sql
-- core/db/models/events.py (Tortoise ORM model)
CREATE TABLE domain_events (
    event_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type    TEXT NOT NULL,
    aggregate_id  TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    payload       JSONB NOT NULL DEFAULT '{}',
    correlation_id TEXT,
    session_id    TEXT,
    agent_id      TEXT,
    team_id       TEXT,
    occurred_at   DOUBLE PRECISION NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())
);

CREATE INDEX idx_events_aggregate ON domain_events (aggregate_id, occurred_at);
CREATE INDEX idx_events_session   ON domain_events (session_id, occurred_at);
CREATE INDEX idx_events_type      ON domain_events (event_type, occurred_at);
CREATE INDEX idx_events_team      ON domain_events (team_id, occurred_at);
```

---

## OpenObserve Backend

**Service**: `cybersec-openobserve` on port `5080`

```yaml
# docker-compose.yml
cybersec-openobserve:
  image: public.ecr.aws/zinclabs/openobserve:latest
  ports:
    - "5080:5080"
  environment:
    ZO_ROOT_USER_EMAIL: admin@cybersec.local
    ZO_ROOT_USER_PASSWORD: ${OPENOBSERVE_PASSWORD}
  volumes:
    - openobserve_data:/data
```

**OTLP endpoint**: `http://cybersec-openobserve:5080/api/default/v1/traces`

**What gets collected automatically** (via OtelBridge):
- Every `DomainEvent` → trace span (group by `correlation_id`)
- Session forensic timelines (group by `session_id`)
- Team activity (group by `team_id`)
- LLM call latency (EventType.LLM_CALL_START → LLM_CALL_COMPLETE duration)
- Permission audit log (EventType.PERMISSION_*)
- Error rates (EventType.*.error count per minute)

---

## Migration from Old Architecture

| Old | New | Notes |
|-----|-----|-------|
| `HookContext` | `HookContext` + `DomainEvent` | Keep mutating interceptor context at runtime; persist immutable domain events |
| `EventBus.emit()` | `event_store.append()` | Persistent, replayable |
| `@on_event decorator` | Redis Streams consumer | Decoupled fan-out |
| Manual OTel spans | `OtelBridge.run()` | Automatic from events |
| Separate RBAC tables | `PermissionProjection` | Derived from event stream |
| `HookErrorStrategy` | Retry at CommandBus level | Cleaner separation |

---

## Related Todos (Phase 6 T6.3)
- `p6-events-store-model` — DomainEventRecord Tortoise model
- `p6-events-domain-event` — DomainEvent struct + EventStore
- `p6-events-command-bus` — CommandBus + domain handlers
- `p6-events-projections` — PermissionProjection + AuditProjection
- `p6-events-otel-bridge` — OtelBridge (implements @otel stub)

---

## Phase 14 — Entry/Exit Instrumentation

### New EventType Constants

Add to `EventType` class in `core/events/domain_event.py`:

```python
# HTTP (T14.2)
HTTP_REQUEST_STARTED   = "http.request.started"
HTTP_REQUEST_COMPLETED = "http.request.completed"
HTTP_REQUEST_FAILED    = "http.request.failed"

# Commands (T14.2)
COMMAND_DISPATCHED = "command.dispatched"
COMMAND_HANDLED    = "command.handled"
COMMAND_FAILED     = "command.failed"

# Agents (T14.2)
AGENT_RUN_STARTED   = "agent.run.started"
AGENT_RUN_COMPLETED = "agent.run.completed"
AGENT_RUN_FAILED    = "agent.run.failed"

# Tools (T14.2)
TOOL_CALL_START    = "tool.call.start"
TOOL_CALL_COMPLETE = "tool.call.complete"
TOOL_CALL_ERROR    = "tool.call.error"
```

### Instrumentation Map

| Entry Point | Event on Entry | Event on Exit (ok) | Event on Exit (err) |
|---|---|---|---|
| `FastAPI route` | `http.request.started` | `http.request.completed` | `http.request.failed` |
| `CommandBus.dispatch()` | `command.dispatched` | `command.handled` | `command.failed` |
| `UnifiedLLMClient.complete()` | `llm.call.start` | `llm.call.complete` | `llm.call.error` |
| `Agent.run()` | `agent.run.started` | `agent.run.completed` | `agent.run.failed` |
| `ToolExecutor.execute()` | `tool.call.start` | `tool.call.complete` | `tool.call.error` |

All events share the same `correlation_id` (set from W3C `traceparent` or auto-generated per request).

### OTEL Context Flow

```
Incoming HTTP request
  → EventInstrumentationMiddleware
      → extract traceparent header
      → map trace_id → correlation_id
      → set ContextVar
      → all downstream @instrument calls inherit correlation_id
  → OtelBridge groups all events with same correlation_id into one trace tree
  → OpenObserve renders full request timeline
```

### Related Todos (Phase 14)
- `events-instrument-decorator` — T14.1
- `events-event-bus-module` — T14.1
- `events-middleware-fastapi` — T14.2
- `events-instrument-command-bus` — T14.2
- `events-instrument-llm-client` — T14.2 (dep: Phase 10)
- `events-instrument-agent` — T14.2
- `events-instrument-tool` — T14.2
- `events-otel-trace-context` — T14.3
- `events-otel-child-spans` — T14.3
- `events-otel-auto-deps` — T14.3
- `events-hook-registry` — T14.4
- `events-on-event-decorator` — T14.4
- `events-hook-executor` — T14.4
- `events-interceptor-context` — T14.5
- `events-interceptor-registry` — T14.5
- `events-pre-hook-decorator` — T14.5
- `events-post-hook-decorator` — T14.5
- `events-instrument-interceptor-wire` — T14.5

### Implementation guardrail

- Classes that emit runtime or lifecycle events should inherit
  `css.core.base.emitter.BaseEmitterClass` where practical.
