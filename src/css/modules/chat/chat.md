# @chat — Backend Layer for Frontend Chat

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/chat/`

**Responsibility**: Handle frontend chat requests with QoL (quality-of-life) injections.

---

## Current State

🟡 **Minimal** (only `enums.py` exists)

**Files**:
- `enums.py` — Chat-related enums
- `pipeline_endpoint.py` — async classify/route/execute/observe pipeline wired through core access surfaces

### Architecture Note (2026-05-09)

- `pipeline_endpoint.py` now imports routing, triage, and agent execution through `css.core.routing`, `css.core.intelligence`, and `css.core.agent_runtime`.
- This keeps `@chat` off direct module-to-module imports while preserving the existing pipeline behavior.
- Frontend colocation scaffold now exists at:
  - `src/css/modules/chat/templates/index.tsx`
  - `src/css/modules/chat/templates/hooks.ts`
  - `src/css/modules/chat/templates/types.ts`
  This is scaffold-only; full chat transport/state wiring is still tracked by `frontend-chat-hooks` and `frontend-chat-panel`.

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

- [ ] Implement message handlers (async)
- [ ] Add prompt injection layer
- [ ] Integrate with chat endpoint handlers
- [ ] Add test coverage
- [ ] Add logger initialization in `__init__.py`

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
**Details**: See .plan/plan.md for current audit and phase status.

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
