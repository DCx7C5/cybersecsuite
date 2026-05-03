# Groq SDK (`groq`)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Provider**: Groq (OpenAI-compatible)  
**SDK Package**: `groq>=0.4.0`  
**Documentation**: https://console.groq.com/docs/openai  
**OpenAPI Compatible**: ✅ Yes (OpenAI-Compatible API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time streaming |
| Vision | ❌ | Not available |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| Batch API | ❌ | Not available |
| Fine-tuning | ❌ | Not available |
| Embeddings | ❌ | Not available |
| Async/Await | ✅ | Native async |
| Token Counting | ✅ | Token counting |
| Speed Focus | ✅ | ⚡ Sub-second inference |

---

## Built-in Tools & Methods

### Core API (OpenAI-compatible)
- `client.chat.completions.create()` — Chat completion
- `client.chat.completions.create(stream=True)` — Streaming
- Fully OpenAI-compatible API

### Error Handling
- `RateLimitError` — Rate limited
- `APIConnectionError` — Connection failed
- `AuthenticationError` — Auth failed

---

## Model Support

- `mixtral-8x7b-32768` — Open-source large
- `llama2-70b-4096` — Meta Llama 2

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: Yes. Models: 2+ supported.
**Last Audited**: 2025-05-03

