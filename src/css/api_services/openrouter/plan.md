# OpenRouter SDK (`openrouter`)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Provider**: OpenRouter (Multi-provider proxy)  
**SDK Package**: `openrouter>=0.1.0`  
**Documentation**: https://openrouter.ai/docs  
**OpenAPI Compatible**: ✅ Yes (OpenAI-Compatible Multi-Provider Proxy)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time streaming |
| Vision | ✅ | Image understanding |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| 100+ Models | ✅ | Unified access |
| Async/Await | ✅ | Native async |
| Routing | ✅ | Provider routing |
| Fallback | ✅ | Model fallback |

---

## Built-in Tools & Methods

### Core API (OpenAI-compatible)
- `client.chat.completions.create()` — Chat
- `client.embeddings.create()` — Embeddings

### Features
- 100+ model support
- Provider routing and fallback

---

## Model Support

- DeepSeek, Perplexity, SambaNova, Cerebras, etc.
- 100+ models unified

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: Yes.
**Last Audited**: 2025-05-03

