# @events — UniversalSDK Event & Hook System

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/events/` ❌ **NOT YET CREATED**

**Responsibility**: Provide event registration & hook system for agents to emit events to UniversalSDK.

---

## Current State

❌ **Missing** (needs creation)

---

## Design

Inspired by Anthropic SDK event system:
- `@on_event('event_name')` decorator for handlers
- Support async/sync handlers
- Typed event payloads (Pydantic dataclasses)
- Thread-safe event bus
- Emit events from agents → forward to UniversalSDK

---

## Files to Create

```
src/css/modules/events/
├── __init__.py              # Public API
├── hooks.py                 # @on_event decorator system
├── emitter.py               # Event bus (emit/listen)
├── types.py                 # Event type enums
├── exceptions.py            # Custom exceptions (e.g., HandlerAlreadyRegistered)
├── models.py                # Event payload dataclasses
└── README.md                # Module documentation
```

---

## Planned Events

- `task.started` — Agent starts task
- `task.completed` — Agent completes task
- `task.failed` — Agent encounters error
- `message.sent` — Agent sends message
- `message.received` — Agent receives message
- `cache.hit` — Cache hit event
- `cache.miss` — Cache miss event
- `provider.used` — LLM provider used
- `agent.error` — Agent error event
- `orchestrator.heartbeat` — Orchestrator alive signal

---

## API (Planned)

```python
from css.modules.events import EventBus, on_event

event_bus = EventBus()

@on_event('task.started')
async def handle_task_started(payload):
    print(f"Task {payload['task_id']} started")
    await event_bus.emit('custom.event', data={'status': 'acknowledged'})

# Listen to events
await event_bus.on('task.started', handle_task_started)

# Emit events
await event_bus.emit('task.started', task_id='t1', agent_id='orchestrator')
```

---

## Implementation Checklist

- [ ] Define event types (enums)
- [ ] Implement EventBus class (thread-safe, async)
- [ ] Create @on_event decorator
- [ ] Add event middleware for UniversalSDK forwarding
- [ ] Create tests
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/events/__init__.py
"""Event & hook system for UniversalSDK integration."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .emitter import EventBus
from .hooks import on_event
from .types import EventType

__all__ = ['EventBus', 'on_event', 'EventType']
```

---

**Status**: 🔴 High Priority (Missing) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
