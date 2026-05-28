# @capabilities — Provider & Model Capability Discovery

> **MOVED TO CORE**: Originally `core/capabilities/`, now at `src/css/core/capabilities/`

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable capability specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.base` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.api_services.*` | → consumes | Provider metadata/endpoints queried during discovery. |
| `css.core.cache` | → consumes | Discovery-result TTL cache and invalidation. |
| `css.core.models` | ← consumed by | Model catalog enrichment with discovered capabilities. |
| `css.modules.chat` / `css.core.resilience` | ← consumed by | Capability-aware request and routing decisions. |

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

**Files**:
- `capability_registry.py` — DynamicCapabilityRegistry class

---

## Purpose

- Query provider capabilities (streaming, vision, tool_use, json_mode, long_context, etc.)
- Cache results for 24h to avoid repeated discovery calls
- Support four discovery sources (hardcoded → env vars → YAML → provider endpoints)
- Graceful fallback if any discovery step fails

---

## Discovery Sequence

1. **Load hardcoded defaults** (fast-path, no I/O)
   - Pre-configured capabilities for OpenAI, Anthropic, etc.

2. **Override with environment variables**
   - Example: `CAPABILITY_OPENAI_GPT4=streaming,vision,tool_use`

3. **Override with YAML config** (`config/capabilities.yaml`)
   - Persistent capability definitions

4. **Query provider `/models` endpoints** (authoritative)
   - Uses 12 LLM providers from `config.py` API_KEYS

---

## API

```python
registry = DynamicCapabilityRegistry()
await registry.discover()  # Called at startup

capabilities = registry.get_capabilities('openai', 'gpt-4')
is_streaming = registry.has_capability('openai', 'gpt-4', CapabilityType.STREAMING)
```

---

## Implementation Checklist

- [ ] Implement discovery methods
- [ ] Add support for API_KEYS from config.py (12 providers)
- [ ] Query provider endpoints
- [ ] Add metrics/telemetry
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/core/capabilities/__init__.py
"""Dynamic capability discovery for LLM providers."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .capability_registry import DynamicCapabilityRegistry

__all__ = ['DynamicCapabilityRegistry']
```

---

**Status**: 🟡 Medium | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain capability implementation detail in this local document.

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
