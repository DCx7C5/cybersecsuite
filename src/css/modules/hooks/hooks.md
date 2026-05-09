# @hooks — Event Hook Runtime Module

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly.

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

These remain phase-tracked in `.plan/session.db` and `.plan/plan.md`.

---

## Implementation Notes

- Base hook contract: `BaseHookClass` in `modules/hooks/base.py` (`msgspec.Struct`, frozen)
- Registry base contract: `BaseRegistry[HookRegistration]`
- Singleton pattern: `@singleton(auto_instantiate=True)` from `css.core.types.meta`
- Hook execution: timeout-bounded chain, `priority` ascending
- Error isolation: handler failures are logged and do not break event emission
- Wildcards are runtime-global: `@on_event("*")` sees all emitted events (not only predefined constants)
- Interceptor registry: synchronous pre/post chain via `HookContext`, `pre_hook`, `post_hook`
- Blocking semantics: `HookBlockedError` cancels the wrapped execution path

---

## Checklist

- [x] `modules-hooks-registry-base` — `HookRegistry` follows `BaseRegistry` contract
- [x] `modules-hooks-singleton-pattern` — singleton pattern from `core/types/meta.py`
- [x] `modules-hooks-event-consumer` — consumes `core/events/event_bus`
- [x] `modules-hooks-on-event-decorator` — decorator registration in module scope
- [x] `modules-hooks-interceptor-chain` — pre/post mutating interceptors (Phase 14 T14.5)

---

**Status**: 🟡 Active | **Last Updated**: 2026-05-09
