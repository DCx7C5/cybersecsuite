# @models — LLM Model Registry & Management

> **MOVED TO CORE**: Originally `modules/llm_models/`, now at `src/css/core/models/`
> Renamed from `llm_models` to `models` for clarity.

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.api_services.*` | ← consumed by | All 22 provider SDKs registered in this registry |
| `css.modules.events` | → consumes | `@instrument("llm.call.{provider}.{model}")` — Phase 14 |
| `UnifiedLLMClient` (Phase 10) | ← provides to | Registry drives provider SDK selection |
| `css.core.triage` | ← provides to | Triage module reads routing tier metadata |

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
# src/css/core/models/__init__.py
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

---

## SDK Architecture

This module is the **model registry**. `UnifiedLLMClient` (Phase 10) uses this registry to select the correct provider SDK and routing tier.

### Three SDK Tiers

| Tier | Providers | Pattern |
|------|-----------|---------|
| **A — Native SDK** | anthropic, openai, gemini, mistral, cohere | Use provider's own Python SDK (best feature access, prompt caching, etc.) |
| **B — OpenAI-compatible** | groq, together, deepinfra, fireworks, perplexity, sambanova, deepseek, openrouter, lambda_api, nscale, cerebras, cloudflare, ai21, xai | openai SDK with `base_url` override OR custom `aiohttp` client |
| **C — Local/Custom** | ollama (custom in-house SDK), opencode (custom CLI integration) | Bespoke aiohttp clients; NOT the pip `ollama` package |

---

## 10-Tier Routing

Models are assigned a routing tier (S+ = best/most expensive, T10 = cheapest/local):

| Tier | Example Models | Notes |
|------|---------------|-------|
| S+ | claude-opus-4.7, gpt-5, gemini-ultra | Best quality, highest cost |
| S | claude-sonnet-4.x, gpt-4.1, gemini-pro | Production default |
| A+ | claude-haiku, gpt-4.1-mini | Fast + capable |
| A | mistral-large, llama-3.3-70b, qwen3-72b | Open-weight large |
| B+ | mistral-small, llama-3.1-8b | Open-weight balanced |
| B | deepseek-v3, qwen3-32b | Cost-effective capable |
| C+ | gemma-3-27b, phi-4 | Small capable |
| C | qwen3-14b, phi-3.5 | Lightweight |
| D | qwen3-7b, llama-3.2-3b | Minimal resources |
| T10 | qwen3-0.6B (Ollama) | Local only — runs on dev PC |

---

## Phase 14 — @instrument Integration

`UnifiedLLMClient.complete()` is **entry point 3 of 5** for the `@events` system.

- Namespace: `@instrument("llm.call.{provider}.{model}")`
- Examples: `"llm.call.anthropic.claude-sonnet-4"`, `"llm.call.ollama.qwen3-0.6b"`
- Events fired: `llm.call.started`, `llm.call.completed`, `llm.call.failed`
- All provider SDK wrappers in `api_services/` are instrumented via this namespace

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
