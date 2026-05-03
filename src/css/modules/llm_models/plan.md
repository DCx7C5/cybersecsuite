# @llm_models — LLM Model Registry & Management

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/llm_models/`

**Responsibility**: Model metadata, validation, and fine-tuning support (TBD).

---

## Current State

🟡 **Minimal** (`registry.py` only)

**Files**:
- `registry.py` — Model registry

---

## Purpose

- Store model metadata (context window, cost, latency, etc.)
- Validate model parameters before API calls
- Support model-specific prompt templates
- Track fine-tuned models
- Cost estimation

---

## Expected Features

- Model registry (in-memory or database-backed)
- Model parameter validation (temperature, max_tokens, etc.)
- Cost calculation (tokens × price)
- Context window awareness
- Fine-tuning support

---

## Integration

- **Capabilities**: Check model capabilities from @capabilities module
- **Cache**: Store model metadata with TTL
- **Chat**: Use for provider/model selection
- **API_KEYS**: Reference 12 providers from config.py

---

## Implementation Checklist

- [x] Define model metadata schema — ModelMetadata with all fields
- [x] Implement registry interface — ModelRegistry with register/get/list
- [x] Add cost calculator — estimate_cost() method
- [x] Add prompt template system — Via custom_params field
- [x] Create model validation layer — validate_parameters() method
- [x] Add logger initialization in `__init__.py` — Full logging setup

**Completed (Phase 2 Foundation)**:
✅ ModelProvider enum (8 providers: Anthropic, OpenAI, Google, Ollama, etc.)
✅ ModelFamily enum (Claude, GPT, Gemini, Llama, etc.)
✅ ModelCapability enum (Vision, ToolUse, Streaming, FunctionCalling, etc.)
✅ ModelPricing dataclass with token-based cost calculation
✅ ModelMetadata with context window, latency, capabilities, pricing
✅ 8 pre-defined models (Claude 3 variants, GPT-4o/Turbo/3.5, Gemini)
✅ ModelRegistry: register, get, list, filter by provider/capability/context/latency
✅ Parameter validation: temperature, top_p, top_k, max_tokens
✅ Cost estimation: input_tokens × input_price + output_tokens × output_price
✅ Full module exports and logging

---

## Module Pattern

```python
# src/css/modules/llm_models/__init__.py
"""LLM model registry, validation, and management."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .registry import ModelRegistry

__all__ = ['ModelRegistry']
```

---

**Status**: 🟢 Low Priority (TBD) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
