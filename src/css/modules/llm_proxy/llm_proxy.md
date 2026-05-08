# @llm_proxy — Local-Compatible LLM Proxy Facade

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/llm_proxy/`

**Responsibility**: Expose a local client-facing proxy surface that routes requests through the platform's internal LLM orchestration layer.

---

## Purpose

`llm_proxy` is the module that lets local clients such as **Claude Code** and other compatible tools send model requests through CyberSecSuite instead of talking directly to providers.

This module is:
- **in-process**
- **local-first**
- **mounted under the main ASGI runtime**
- **routed through the same cache, routing, memory, and observability layers as the app**

This module is **not**:
- a separate Docker service
- a generic internet reverse proxy
- the owner of provider SDKs

---

## Target Surface

Initial compatibility target:

```text
/v1/models
/v1/chat/completions
```

Future expansion can add other compatibility profiles if needed, but the first implementation should stay intentionally narrow and map cleanly onto the existing internal request pipeline.

Streaming should leave via SSE-compatible semantics so editor/CLI clients can consume token deltas without learning internal platform protocols.

---

## Internal Flow

```text
Client request
  -> modules/llm_proxy
  -> request normalization
  -> UnifiedLLMClient
  -> PromptCacheManager
  -> routing / resilience
  -> optional memory + retrieval context assembly
  -> provider adapter
  -> normalized response / SSE stream
```

The proxy facade must not bypass:
- prompt caching
- provider routing
- resilience / retries
- observability
- usage accounting

---

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.asgi` | ← mounted by | owns `/v1/*` route surface and transport shell |
| `css.core.models` | → consumes | `UnifiedLLMClient` request execution |
| `css.core.prompt_cache` | → consumes | request/stream caching and native cache stats |
| `css.modules.strategies` | → consumes | provider/model routing policy |
| `css.core.resilience` | → consumes | retry/circuit-breaker behavior |
| `css.core.memory` | → consumes | optional context assembly before provider call |
| `css.core.rag_vector` / `css.core.rag_graph` | → consumes | retrieval-backed context for proxy requests when enabled |
| `css.core.events` | ← instruments | `llm.call.*`, proxy request lifecycle, usage |
| frontend / external local clients | ← consumes | `/v1/*` compatibility surface |

---

## Local-Only Trust Model

Default assumptions:
- bind to localhost in development
- no public reverse-proxy deployment assumptions
- optional local bearer token or per-user API key later
- audit trail on proxied calls

The trust model is different from public SaaS gateways. The primary use case is **local tooling and local operator workflows**.

---

## Streaming Notes

`llm_proxy` should normalize provider streaming into one outward shape:
- assistant token deltas
- tool-call deltas
- finish reason
- usage summary / trailer
- cancellation semantics

The outward transport should be SSE-compatible. Internally, providers may still use:
- SDK async iterators
- HTTP chunked streams
- provider-specific event objects

---

## Planned Work

- `proxy-module-plan`
- `proxy-openai-surface`
- `proxy-routing-bridge`
- `proxy-streaming-normalization`
- `proxy-local-trust-boundary`

---

**Status**: 🟡 Planned | **Priority**: High | **Last Updated**: 2026-05-08
