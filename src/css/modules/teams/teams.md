# @teams — Team Management & Coordination

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable team-management specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.modules.agents` | → coordinates | Team membership and per-agent execution assignment. |
| `css.modules.a2a_internal` | → consumes | Internal task/result communication between team participants. |
| `css.core.redis` | → consumes | Dispatch/queue transport used by orchestration runtime. |
| `css.core.events` | → emits | Team lifecycle, task assignment, and result events. |

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

### Architecture Note (2026-05-09)

- `orchestrator.py` delegates through `css.modules.a2a_internal` and `css.core.redis.dispatcher`.
- The team orchestrator value object is `msgspec.Struct`, replacing the earlier dataclass-based stub.

---

## Purpose

- Create and manage team instances
- Assign members to teams
- Distribute tasks among team members
- Coordinate team activities
- Track team performance metrics

---

## Implementation Checklist

- [ ] Team definition and schema
- [ ] Team registry and lifecycle
- [ ] Member assignment and tracking
- [ ] Task distribution to members
- [ ] Team coordination engine
- [ ] Add logger initialization in `__init__.py`
- [x] Remove conflicting ORM stubs (`models.py`, `orchestrator.py`) and use `css.core.db.models` as canonical source

---

## Module Pattern

```python
# src/css/modules/teams/__init__.py
"""Team management and coordination."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import TeamManager

__all__ = ['TeamManager']
```

---

**Status**: 🔴 Priority (Critical) | **Last Updated**: 2026-05-04
## 🎭 FEATURE 2: TEAMSCOPE ARCHITECTURE

### Problem → Solution
```
PROBLEM:  All tasks in single queue → Monolithic, no isolation
SOLUTION: Teams with separate queues → Complete isolation
```

### TeamScope Hierarchy
```
SessionScope
│
├─ Team-1: Engineering (max 3 orch)
│  ├─ Team-specific config
│  ├─ Isolated task queue
│  ├─ Orchestrator-1, -2, -3 (independent)
│  ├─ Results (team-isolated)
│  └─ Resource quota: 3 concurrent orchestrators
│
├─ Team-2: Security (max 10 orch)
│  ├─ Team-specific config
│  ├─ Isolated task queue (separate DB)
│  ├─ Orchestrator-1 through -10 (independent)
│  ├─ Results (team-isolated)
│  └─ Resource quota: 10 concurrent orchestrators
│
└─ Team-3: Compliance (max 1 orch)
   ├─ Team-specific config
   ├─ Isolated task queue
   ├─ Orchestrator-1 (single)
   ├─ Results (team-isolated)
   └─ Resource quota: 1 concurrent orchestrator

ISOLATION BENEFITS:
✅ Team-1 crash → Teams 2 & 3 unaffected
✅ Team-1 exceeds quota → Teams 2 & 3 continue
✅ Team-1 paused → Teams 2 & 3 run normally
✅ Resource contention eliminated (static quotas)
```

### Team Data Model
```python
class Team(msgspec.Struct, frozen=True):
    id: int
    session_id: int
    name: str                          # "engineering", "security", etc.
    team_type: str = "general"
    max_concurrent_orchestrators: int = 3  # Resource quota
    orchestrator_timeout_sec: int = 300
    orchestrator_count: int = 0        # Current count
    status: str = "active"             # active | paused | completed
    priority: int = 1                  # 1-10 (higher = more resources)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
```

### Team Lifecycle & State Machine
```
States: active → paused → completed

Transitions:
┌─────────────────────────────────────────┐
│          ACTIVE (Running)               │
├─────────────────────────────────────────┤
│ ✅ Can spawn orchestrators              │
│ ✅ Can pull tasks from queue            │
│ ✅ Results are merged                   │
│ ✅ Transition: pause() or complete()    │
└─────────────────────────────────────────┘
         ↓ pause()                    ↓ complete()
         │                             │
┌─────────────────────────────────────────┐  ┌──────────────────────────┐
│        PAUSED (Frozen)                  │  │   COMPLETED (Done)       │
├─────────────────────────────────────────┤  ├──────────────────────────┤
│ ❌ Cannot spawn orchestrators           │  │ ❌ No new orchestrators  │
│ ❌ Queue frozen (tasks not pulled)      │  │ ❌ Queue frozen          │
│ ⚠️  Existing orch still running         │  │ ⚠️  Final results saved  │
│ ✅ Transition: resume()                 │  │ 🔒 FINAL STATE           │
└─────────────────────────────────────────┘  └──────────────────────────┘
         ↑                                      
         └──── resume()
```

---
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain team implementation detail in this local document.

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
