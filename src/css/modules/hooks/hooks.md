# @hooks — Event Hook Runtime Module

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable hook-runtime specification.

---

## Responsibility

`src/css/modules/hooks/` owns hook registration and execution behavior.

- Consumes event emissions from `css.core.events.event_bus`
- Implements `@on_event("pattern")` registration surface
- Executes handlers as priority-sorted chains per event type
- Keeps hook runtime non-blocking for event emitters

`css.core.events` remains the canonical source for event emission and event-store architecture.

---

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.events.event_bus` | → consumes | Subscribes one wildcard dispatcher; pattern matching happens inside registry |
| `css.core.events` | ← provides to | Compatibility exports (`HookRegistry`, `on_event`) |

---

## Phase 14 Mapping

This module implements the runtime surface for:
- `events-hook-registry`
- `events-on-event-decorator`
- `events-hook-executor`
- `events-interceptor-context`
- `events-interceptor-registry`
- `events-pre-hook-decorator`
- `events-post-hook-decorator`
- `events-instrument-interceptor-wire`

These remain status-tracked in `.plan/session.db`; this local document owns the
hook implementation detail.

---

## Implementation Notes

- Base hook contract: `BaseHookClass` in `modules/hooks/base.py` (`msgspec.Struct`, frozen)
- Registry base contract: `BaseRegistry[HookRegistration]`
- Singleton pattern: `@singleton(auto_instantiate=True)` from `css.core.base.meta`
- Hook execution: timeout-bounded chain, `priority` ascending
- Error isolation: handler failures are logged and do not break event emission
- Wildcards are runtime-global: `@on_event("*")` sees all emitted events (not only predefined constants)
- Interceptor registry: synchronous pre/post chain via `HookContext`, `pre_hook`, `post_hook`
- Blocking semantics: `HookBlockedError` cancels the wrapped execution path

---

## Checklist

- [x] `modules-hooks-registry-base` — `HookRegistry` follows `BaseRegistry` contract
- [x] `modules-hooks-singleton-pattern` — singleton pattern from `core/base/meta.py`
- [x] `modules-hooks-event-consumer` — consumes `core/events/event_bus`
- [x] `modules-hooks-on-event-decorator` — decorator registration in module scope
- [x] `modules-hooks-interceptor-chain` — pre/post mutating interceptors (Phase 14 T14.5)

## Executable Hook Contract (2026-05-26)

### Exact Files And Symbols

| Path | Live symbols |
|------|--------------|
| `src/css/modules/hooks/base.py` | `BaseHookClass`. |
| `src/css/modules/hooks/registry.py` | `HookRegistry`, `on_event()`. |
| `src/css/modules/hooks/interceptors.py` | `HookContext`, `HookBlockedError`, `InterceptorRegistry`, `pre_hook()`, `post_hook()`. |
| `src/css/core/events/emitter.py` | Existing event emission owner consumed by hook registration. |
| `src/css/core/events/instrument.py` | Planned/retained instrumentation wrapper owner consumed by interception work. |

### Live Todo Map And Validation

| Todo IDs | Status | Boundary |
|----------|--------|----------|
| `events-hook-registry`, `events-on-event-decorator`, `events-hook-executor`, `events-interceptor-context`, `events-interceptor-registry`, `events-pre-hook-decorator`, `events-post-hook-decorator`, `events-instrument-interceptor-wire` | done | Preserve current hook/interceptor runtime behavior and exports. |
| `events-instrument-decorator`, `events-event-bus-module`, `events-instrument-*`, `events-otel-*` | pending | Complete in `core/events` and consumer entry points; do not move event ownership into hooks. |

1. Verify existing registry/interceptor behavior and public imports before
   connecting new instrumented entry points.
2. Add consumer instrumentation in its owning files while invoking hook
   pre/post semantics through the current interceptor contract.
3. Validate wildcard/priority/timeout/error isolation, blocking behavior,
   instrumentation success/failure events, and event-to-hook dependency
   direction.

---

**Status**: 🟡 Active | **Last Updated**: 2026-05-09
