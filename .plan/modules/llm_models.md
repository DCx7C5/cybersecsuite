# @llm_models — LLM Model Registry & Management

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

- [ ] Define model metadata schema
- [ ] Implement registry interface
- [ ] Add cost calculator
- [ ] Add prompt template system
- [ ] Create model validation layer
- [ ] Add logger initialization in `__init__.py`

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
