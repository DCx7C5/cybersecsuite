# @chat — Backend Layer for Frontend Chat

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable chat-backend specification.

---

**Location**: `src/css/modules/chat/`

**Responsibility**: Handle frontend chat requests with QoL (quality-of-life) injections.

---

## Current State

🟡 **Partial runtime**: message endpoints/models and the async execution
pipeline exist, while realtime frontend/activity integration remains planned.

**Files**:
- `enums.py` — Chat-related enums
- `pipeline_endpoint.py` — async classify/route/execute/observe pipeline
- `endpoints.py`, `models.py` — current CRUD/storage surfaces

### Architecture Note (2026-05-25)

- `pipeline_endpoint.py` consumes the canonical public APIs:
  `css.modules.triage.classify`, `css.modules.strategies.route`, and
  `css.modules.agents.AgentExecutor`.
- Thin root-level `core` facades for module-owned triage/routing behavior have
  been removed; those modules own their runtime contracts.
- Frontend colocation scaffold now exists at:
  - `src/css/modules/chat/templates/index.tsx`
  - `src/css/modules/chat/templates/hooks.ts`
  - `src/css/modules/chat/templates/types.ts`
  This is scaffold-only; full chat transport/state wiring is still tracked by `frontend-chat-hooks` and `frontend-chat-panel`.
- Rich runtime chat activity UX is now explicitly tracked:
  - `frontend-chat-activity-stream`
  - `frontend-chat-thinking-task-visuals`
  These cover thinking spinners, active agent/task activity, and tool lifecycle visuals.

---

## Purpose

- Backend service for React frontend chat interface
- Inject QoL transformations (prompt beautification, context enrichment)
- Route to appropriate LLM provider
- Stream responses via WebSocket
- Session management

---

## Expected Features

- Chat message handling (create, list, update)
- Prompt injection & preprocessing
- Provider selection (based on @capabilities module)
- Response streaming (via @streaming module)
- Conversation history management & retrieval

---

## Integration Points

- **Frontend**: React chat component (port 8000)
- **Backend**: FastAPI route handlers
- **Streaming**: `@streaming` module (WebSocket)
- **LLM APIs**: via `api_services/` (anthropic, openai, groq, etc.)
- **Cache**: for storing chat history & responses
- **Capabilities**: provider selection based on model capabilities
- **Events** (`@events`): HTTP middleware fires `@instrument("http.{method}.{path}")` per request; CommandBus fires `@instrument("command.ChatCommand")` per dispatch
- **Permissions** (`@permissions`): chat requests carry `agent_id`; permissions are checked at tool level (not at chat level)

---

## Implementation Checklist

- [ ] Harden existing async message/session/WebSocket handlers and persistence boundaries
- [ ] Add prompt injection layer
- [ ] Integrate with chat endpoint handlers
- [ ] Implement chat activity event stream shape for frontend (thinking/agent/task/tool)
- [ ] Expose live activity metadata needed by rich chat visuals
- [ ] Add test coverage
- [ ] Add logger initialization in `__init__.py`

## Executable Chat Contract (2026-05-26)

### Exact Files And Symbols

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/modules/chat/endpoints.py` | Existing `create_session()`, `get_session_messages()`, `websocket_chat_endpoint()` at `/api/chat/ws/{session_id}`. |
| `src/css/modules/chat/models.py`, `src/css/modules/chat/persistence_models.py` | Existing message/session values and persistence records requiring reconciliation. |
| `src/css/modules/chat/pipeline_endpoint.py` | Existing `chat_pipeline()` and `process_chat_message()` execution bridge. |
| `src/css/modules/chat/templates/index.tsx` | Existing `ChatPanel` scaffold to replace/complete, not a file to create anew. |
| `src/css/modules/chat/templates/hooks.ts`, `src/css/modules/chat/templates/types.ts` | Existing frontend hook/type scaffolds. |

### Live Todo Map And Work Order

| Todo ID | Status | Required result |
|---------|--------|-----------------|
| `frontend-chat-hooks` | pending | Build chat state/history/stream hooks against current REST/WebSocket-first backend contract. |
| `frontend-chat-panel` | pending | Replace existing `templates/index.tsx` scaffold with panel UI; do not describe it as newly created and do not assume SSE. |
| `frontend-chat-activity-stream`, `frontend-chat-thinking-task-visuals` | pending | Add structured thinking/agent/task/tool activity after core chat transport works. |

1. Reconcile duplicate/current message persistence surfaces and test the
   existing REST plus `/api/chat/ws/{session_id}` behavior.
2. Implement frontend hooks and replace the existing panel scaffold using
   WebSocket-first streaming/error/disconnect semantics.
3. Layer rich activity event visualization after message/session transport is
   stable; do not invent an SSE MVP contract for chat.
4. Validate REST history, WebSocket lifecycle, pipeline routing,
   markdown/tool-result rendering, panel build/check, disconnect/error paths,
   and later activity-event rendering.

---

## Module Pattern

```python
# src/css/modules/chat/__init__.py
"""Backend layer for frontend chat with QoL injections."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .handlers import ChatMessageHandler

__all__ = ['ChatMessageHandler']
```

---

**Status**: 🟡 Medium | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain chat implementation detail in this local document.

---

## Phase 14 — Dual Entry Points

Chat traffic passes through **two** of the 5 `@instrument` entry points:

### Entry Point 1 — FastAPI HTTP Middleware
- `@instrument("http.{method}.{path}")` applied per-request in `core/asgi/middleware.py`
- Extracts W3C `traceparent` header → sets `correlation_id` ContextVar
- All downstream calls inherit `correlation_id` automatically

### Entry Point 2 — CommandBus
- Chat requests dispatch a `ChatCommand` through the `CommandBus`
- `@instrument("command.ChatCommand")` wraps the command handler
- Events: `command.ChatCommand.started`, `.completed`, `.failed`

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
