# @capabilities — Provider & Model Capability Discovery

**Location**: `src/css/modules/capabilities/`

**Responsibility**: Dynamic capability discovery and caching for all LLM providers.

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
# src/css/modules/capabilities/__init__.py
"""Dynamic capability discovery for LLM providers."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .capability_registry import DynamicCapabilityRegistry

__all__ = ['DynamicCapabilityRegistry']
```

---

**Status**: 🟡 Medium | **Last Updated**: 2026-05-03
