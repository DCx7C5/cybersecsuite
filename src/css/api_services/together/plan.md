# Together AI SDK (`together`)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Provider**: Together AI  
**SDK Package**: `together>=1.0.0`  
**Documentation**: https://docs.together.ai/reference  
**OpenAPI Compatible**: ✅ Yes (OpenAI-Compatible API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time streaming |
| Vision | ✅ | Image understanding |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| Batch API | ✅ | Batch processing |
| Fine-tuning | ❌ | Not available |
| Embeddings | ✅ | Embedding models |
| Async/Await | ✅ | Native async |
| 100+ Models | ✅ | Multi-provider access |

---

## Built-in Tools & Methods

### Core API (OpenAI-compatible)
- `client.chat.completions.create()` — Chat
- `client.embeddings.create()` — Embeddings
- `client.fine_tuning.jobs.create()` — Fine-tuning
- `client.batch()` — Batch API

### Model Access
- 100+ open-source models
- Multi-provider routing

---

## Model Support

- 100+ models including Llama, Mixtral, Code Llama

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: Yes.
**Last Audited**: 2025-05-03

