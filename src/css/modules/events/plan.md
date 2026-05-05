# @events — UniversalSDK Event & Hook System

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | `DomainEventRecord` Tortoise ORM model |
| `css.core.events.store` | → consumes | `EventStore.append()` + `replay()` |
| `css.core.events.otel_bridge` | → consumes | `OtelBridge.run()` background task |
| `css.core.events.otel_context` | → consumes | `TraceContextExtractor`, `OtelSpanInstrumentor` |
| `css.core.asgi.middleware` | ← provides | `EventInstrumentationMiddleware` |
| `css.modules.llm_proxy` | ← instruments | `UnifiedLLMClient.complete()` |
| `css.modules.agents` | ← instruments | `Agent.run()` |
| `css.modules.tools` | ← instruments | `ToolExecutor.execute()` |

---

## Current State

❌ **Missing** (needs creation) — Phase 6 T6.3 creates the storage layer; Phase 14 wires entry/exit points.

---

## Architecture (Updated — Phase 6 + Phase 14)

> ⚠️ Old `EventBus.emit()` / `@on_event` decorator design is **superseded** by the CQRS event store.
> See `.plan/architecture/observability.md` for full architecture diagram.

### Phase 6 T6.3 (storage plumbing):
- `DomainEvent` — immutable msgspec.Struct
- `EventStore` — PostgreSQL write + Redis Streams fan-out
- `CommandBus` — command → events pattern
- `OtelBridge` — stream consumer → OTEL spans
- `PermissionProjection` / `AuditProjection`

### Phase 14 (entry/exit wiring):
- `@instrument(namespace)` — wraps any async fn; emits started/completed/failed DomainEvents
- `EventInstrumentationMiddleware` — HTTP entry/exit for all FastAPI routes
- Applied at: `CommandBus.dispatch()`, `UnifiedLLMClient.complete()`, `Agent.run()`, `ToolExecutor.execute()`
- `TraceContextExtractor` — W3C traceparent → `correlation_id` in ContextVar
- `OtelSpanInstrumentor` — child OTEL span per instrumented call
- `HookRegistry` / `@on_event` — optional hook compatibility layer

---

## Files to Create

```
src/css/modules/events/
├── __init__.py              # Public API: EventStore, OtelBridge, instrument, on_event
├── instrument.py            # @instrument(namespace) decorator + ContextVar
├── hooks.py                 # HookRegistry, @on_event, HookExecutor (_safe_call)
├── types.py                 # EventType constants (mirrors core/events/domain_event.py)
├── exceptions.py            # HookTimeout, HookRegistrationError
└── models.py                # (none needed — DomainEventRecord lives in core/db)
```

Core layer (Phase 6 T6.3, lives in `core/events/`):
```
core/events/
├── domain_event.py          # DomainEvent msgspec.Struct + EventType class
├── store.py                 # EventStore (PostgreSQL + Redis Streams)
├── commands.py              # CommandBus
├── projections.py           # PermissionProjection + AuditProjection
├── otel_bridge.py           # OtelBridge (Redis Streams → OTEL spans)
└── otel_context.py          # TraceContextExtractor + OtelSpanInstrumentor (Phase 14)
```

---

## Planned Events

### Phase 6 (storage layer)
- `team.spawned` / `team.shutdown` / `team.crashed`
- `task.delegated` / `task.completed` / `task.failed` / `task.reassigned`
- `agent.action` / `agent.error`
- `permission.granted` / `permission.revoked` / `permission.denied`
- `marketplace.install` / `marketplace.uninstall`
- `llm.call.start` / `llm.call.complete` / `llm.call.error` / `llm.cache.hit`

### Phase 14 (entry/exit instrumentation)
- `http.request.started` / `http.request.completed` / `http.request.failed`
- `command.dispatched` / `command.handled` / `command.failed`
- `agent.run.started` / `agent.run.completed` / `agent.run.failed`
- `tool.call.start` / `tool.call.complete` / `tool.call.error`

---

## API (Phase 14)

```python
from css.modules.events import instrument, on_event, hook_registry, event_store

# 1. Decorate entry/exit points
@instrument("agent.run", extract_aggregate_id=lambda self, *a, **k: self.agent_id)
async def run(self, task: Task) -> Result: ...

# 2. Subscribe to event patterns (hook compatibility)
@on_event("llm.call.*")
async def log_llm_calls(event: DomainEvent):
    print(f"LLM {event.event_type}: {event.payload}")

# 3. Direct emit (for custom events)
await event_store.append(DomainEvent(
    event_type="custom.event",
    aggregate_id="my-id",
    aggregate_type="custom",
    payload={"data": "..."},
))

# 4. Replay for forensics
events = await event_store.replay_session(session_id="abc-123")
```

---

## Implementation Checklist

### Phase 6 T6.3 (core storage)
- [ ] `p6-events-store-model` — DomainEventRecord Tortoise ORM model
- [ ] `p6-events-domain-event` — DomainEvent + EventStore + EventType
- [ ] `p6-events-command-bus` — CommandBus + handlers
- [ ] `p6-events-projections` — PermissionProjection + AuditProjection
- [ ] `p6-events-otel-bridge` — OtelBridge (Redis → OTEL spans)

### Phase 14 T14.1–T14.5 (instrumentation + interceptors)
- [ ] `events-instrument-decorator` — @instrument(namespace) + ContextVar
- [ ] `events-event-bus-module` — Wire singletons in __init__.py + lifespan
- [ ] `events-middleware-fastapi` — EventInstrumentationMiddleware
- [ ] `events-instrument-command-bus` — CommandBus.dispatch wired
- [ ] `events-instrument-llm-client` — UnifiedLLMClient.complete wired
- [ ] `events-instrument-agent` — Agent.run wired
- [ ] `events-instrument-tool` — ToolExecutor.execute wired
- [ ] `events-otel-trace-context` — TraceContextExtractor + ContextVar
- [ ] `events-otel-child-spans` — OtelSpanInstrumentor
- [ ] `events-otel-auto-deps` — pyproject.toml OTEL packages
- [ ] `events-hook-registry` — HookRegistry (glob pattern) — **observers only, telemetry**
- [ ] `events-on-event-decorator` — @on_event shortcut
- [ ] `events-hook-executor` — _safe_call fire-and-forget
- [ ] `events-interceptor-context` — HookContext[Input, Output] + HookBlockedError
- [ ] `events-interceptor-registry` — InterceptorRegistry (priority + glob)
- [ ] `events-pre-hook-decorator` — @pre_hook(pattern, priority)
- [ ] `events-post-hook-decorator` — @post_hook(pattern, priority)
- [ ] `events-instrument-interceptor-wire` — wire interceptor chain into @instrument

---

## Module Pattern

```python
# src/css/modules/events/__init__.py
"""Event & hook system — entry/exit instrumentation + OTEL bridge."""

from css.core.events.domain_event import DomainEvent, EventType
from css.core.events.store import EventStore
from css.core.events.otel_bridge import OtelBridge

from .instrument import instrument, _correlation_ctx
from .hooks import HookRegistry, on_event, hook_registry

# Module-level singletons (wired on app startup)
event_store: EventStore
otel_bridge: OtelBridge

__all__ = [
    "DomainEvent", "EventType",
    "EventStore", "OtelBridge",
    "instrument", "on_event", "hook_registry",
    "event_store", "otel_bridge",
]
```

---

## Related Todos

### Phase 6 T6.3 (prerequisite)
- `p6-events-store-model`, `p6-events-domain-event`, `p6-events-command-bus`, `p6-events-projections`, `p6-events-otel-bridge`

### Phase 14 T14.1–T14.2 (instrumentation)
- `events-instrument-decorator`, `events-event-bus-module`
- `events-middleware-fastapi`, `events-instrument-command-bus`, `events-instrument-llm-client`, `events-instrument-agent`, `events-instrument-tool`

### Phase 14 T14.3 (OTEL)
- `events-otel-trace-context`, `events-otel-child-spans`, `events-otel-auto-deps`

### Phase 14 T14.4 (observers — telemetry only, never mutates)
- `events-hook-registry`, `events-on-event-decorator`, `events-hook-executor`

### Phase 14 T14.5 (interceptor chain — mutating pre/post hooks)
- `events-interceptor-context`, `events-interceptor-registry`
- `events-pre-hook-decorator`, `events-post-hook-decorator`
- `events-instrument-interceptor-wire`

**Status**: 🔴 High Priority (Missing) | **Last Updated**: 2026-05-04

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
