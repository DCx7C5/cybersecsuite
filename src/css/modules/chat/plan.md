# @chat — Backend Layer for Frontend Chat

**Location**: `src/css/modules/chat/`

**Responsibility**: Handle frontend chat requests with QoL (quality-of-life) injections.

---

## Current State

🟡 **Minimal** (only `enums.py` exists)

**Files**:
- `enums.py` — Chat-related enums

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
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
