# @events — UniversalSDK Event & Hook System

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable event/hook specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | `DomainEventRecord` Tortoise ORM model |
| `css.core.events.store` | → consumes | `EventStore.append()` + `replay()` |
| `css.core.events.otel_bridge` | → consumes | `OtelBridge.run()` background task |
| `css.core.events.otel_context` | → consumes | `TraceContextExtractor`, `OtelSpanInstrumentor` |
| `css.modules.hooks` | ← consumes | EventBus stream for `@on_event` hook chains |
| `css.core.asgi.middleware` | ← provides | `EventInstrumentationMiddleware` |
| `css.modules.llm_proxy` | ← instruments | `UnifiedLLMClient.complete()` |
| `css.modules.agents` | ← instruments | `Agent.run()` |
| `css.modules.tools` | ← instruments | `ToolExecutor.execute()` |

---

## Current State

✅ **Canonical ownership** — `core/events/` owns both the legacy event-bus surface and the CQRS/domain-event implementation. Legacy module package removed.
✅ **Hook ownership split** — hook registry implementation now lives in `src/css/modules/hooks/`; `core/events/hooks.py` is compatibility re-export only.

## Verification Result — 2026-05-09

**Result**: Not yet verified as universal. The architecture target is correct, but implementation coverage is incomplete.

Current verified coverage:
- `DomainEvent`, `EventStore`, `CommandBus`, projections, and `DomainEventRecord` exist.
- `core/tools/executor.py` is the only verified runtime user of `core.events.instrument`.
- Phase 6 event-store todos are done in `.plan/session.db`.

Current verified gaps:
- `EventStore` is in-memory only; `DomainEventRecord` exists, but `EventStore.append()` does not persist to PostgreSQL or fan out through Redis Streams.
- `event_bus` and `EventStore` are still parallel surfaces; hooks currently attach to the legacy bus, not the domain-event stream.
- `instrument()` still emits through `event_bus` and is not yet the planned `DomainEvent`/`EventStore` decorator surface.
- HTTP middleware, `CommandBus.execute()`, agent execution, and LLM adapter/client completion paths are not yet wired through the planned instrumentation surface.
- OTEL is placeholder-level: no `OtelBridge.run()` background task, no real SDK/exporter setup, no W3C trace context extraction, and no child span lifecycle.
- Observer hooks and interceptor hooks now coexist: observers are fire-and-forget; interceptors are synchronous, mutable, and blocking-aware via `HookBlockedError`.

Universal acceptance gates:
- Every ingress, domain command, agent run, tool call, LLM call, stream lifecycle step, marketplace mutation, permission decision, cache decision, and background task emits `DomainEvent` entry/exit/failure events through one instrumentation API.
- Hooks and interceptors bind to the same event namespaces as emitted events, with glob matching and priority-sorted chains.
- Observer hooks are fire-and-forget and non-mutating; interceptor hooks are explicit pre/post chains and can mutate or block only through documented strategy types.
- Every emitted event is persisted, replayable, correlated, and convertible into OTEL spans without module-specific glue.

Implementation guardrail:
- When introducing new event-emitting classes, inherit `BaseEmitterClass` where possible to keep namespace qualification and event registration consistent.

---

## Architecture (Updated — Phase 6 + Phase 14)

> ⚠️ Long-term target is CQRS/EventStore-only, but runtime compatibility is still active:
> `EventBus.emit()` + `@on_event` stay in place while migration to full EventStore wiring is completed.

### Phase 6 T6.3 (storage plumbing):
- `DomainEvent` — immutable msgspec.Struct
- `EventStore` — PostgreSQL write + Redis Streams fan-out
- `CommandBus` — command → events pattern
- `OtelBridge` — stream consumer → OTEL spans
- `PermissionProjection` / `AuditProjection`

### Phase 14 (entry/exit wiring):
- `instrument(namespace)` async context manager — emits `{namespace}.start/.complete/.error` bus events
- `event.pre/post/past/on_completed/on_failed/all` decorators — lifecycle event emission on async callables
- `EventInstrumentationMiddleware` — HTTP entry/exit for all FastAPI routes
- Applied at: `CommandBus.execute()`, `UnifiedLLMClient.complete()`, `Agent.run()`, `ToolExecutor.execute()`
- `TraceContextExtractor` — W3C traceparent → `correlation_id` in ContextVar
- `OtelSpanInstrumentor` — child OTEL span per instrumented call
- `HookRegistry` / `@on_event` — optional hook compatibility layer

---

## Package Layout

```
src/css/core/events/
├── __init__.py              # Public API for bus, CQRS, projections, and OTEL bridge
├── domain_event.py          # DomainEvent msgspec.Struct + event factories
├── store.py                 # EventStore
├── command_bus.py           # CommandBus + command types
├── projections.py           # PermissionProjection + AuditProjection
├── otel_bridge.py           # DomainEvent → OTEL span bridge
├── event_bus.py             # Legacy event-bus singleton
├── hooks.py                 # Compatibility bridge to modules/hooks
├── instrument.py            # Async event instrumentation helper
├── types.py                 # Event-type constants
└── exceptions.py            # Event-system exceptions
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
from css.core.events import HookBlockedError, HookContext, event, instrument, on_event, pre_hook
from css.core.types.base_emitter import BaseEmitterClass

# 1. Namespaced lifecycle decorators on event-emitting classes
class QueryService(BaseEmitterClass):
    event_namespace = "query"

QueryService.register_events("execute")

@event.all("execute")
async def execute(self, sql: str) -> dict[str, object]:
    return {"ok": True}

# 2. Runtime observer hook (fire-and-forget)
@on_event("query.*")
async def log_query_events(event_type: str, payload: object) -> None:
    print(event_type, payload)

# 3. Mutating/blocking pre-hook interceptor
@pre_hook("query.execute", priority=10)
async def enforce_query_budget(ctx: HookContext) -> HookContext:
    if ctx.metadata.get("budget_exceeded"):
        raise HookBlockedError("query budget exceeded")
    return ctx

# 4. Instrument one block manually
async with instrument("tool.call", tool_id="nmap"):
    ...
```

---

## Implementation Checklist

### Phase 6 T6.3 (core storage)
- [x] `p6-events-store-model` — DomainEventRecord Tortoise ORM model
- [x] `p6-events-domain-event` — DomainEvent + EventStore + EventType
- [x] `p6-events-command-bus` — CommandBus + handlers
- [x] `p6-events-projections` — PermissionProjection + AuditProjection
- [x] `p6-events-otel-bridge` — OtelBridge (Redis → OTEL spans)

### Phase 14 T14.1–T14.5 (instrumentation + interceptors)
- [ ] `events-instrument-decorator` — @instrument(namespace) + ContextVar
- [ ] `events-event-bus-module` — Wire singletons in __init__.py + lifespan
- [ ] `events-middleware-fastapi` — EventInstrumentationMiddleware
- [ ] `events-instrument-command-bus` — CommandBus.execute wired
- [ ] `events-instrument-llm-client` — UnifiedLLMClient.complete wired
- [ ] `events-instrument-agent` — Agent.run wired
- [ ] `events-instrument-tool` — ToolExecutor.execute wired
- [ ] `events-otel-trace-context` — TraceContextExtractor + ContextVar
- [ ] `events-otel-child-spans` — OtelSpanInstrumentor
- [ ] `events-otel-auto-deps` — pyproject.toml OTEL packages
- [x] `events-hook-registry` — HookRegistry (glob pattern) — **observers only, telemetry**
- [x] `events-on-event-decorator` — @on_event shortcut
- [x] `events-hook-executor` — _safe_call fire-and-forget
- [x] `events-interceptor-context` — HookContext + HookBlockedError
- [x] `events-interceptor-registry` — InterceptorRegistry (priority + glob)
- [x] `events-pre-hook-decorator` — @pre_hook(pattern, priority)
- [x] `events-post-hook-decorator` — @post_hook(pattern, priority)
- [x] `events-instrument-interceptor-wire` — wire interceptor chain into @instrument and event lifecycle decorators

---

## Module Pattern

```python
# src/css/core/events/__init__.py
"""Event & hook system — entry/exit instrumentation + OTEL bridge."""

from css.core.events.domain_event import DomainEvent, EventType
from css.core.events.store import EventStore
from css.core.events.otel_bridge import OtelBridge

from .instrument import instrument, _correlation_ctx
from css.modules.hooks import HookRegistry, on_event, hook_registry

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

**Status**: 🟡 Active | **Last Updated**: 2026-05-09

---

## 🔄 Sync Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
>
> - This file defines the implementation contract, not completion state.
> - Update tracker state as required by `.plan/rules.md`.
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
