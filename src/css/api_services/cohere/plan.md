# Cohere SDK (`cohere`)

**Provider**: Cohere  
**SDK Package**: `cohere>=5.0.0`  
**Documentation**: https://github.com/cohere-ai/cohere-python  
**OpenAPI Compatible**: ❌ No (Proprietary Cohere API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Token streaming |
| Vision | ❌ | Not available |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| Batch API | ✅ | Batch processing |
| Fine-tuning | ✅ | Custom models |
| Embeddings | ✅ | Dense embeddings |
| Async/Await | ✅ | Native async |
| Reranking | ✅ | Re-ranking API |
| Multilingual | ✅ | Multi-language support |

---

## Built-in Tools & Methods

### Core API
- `client.chat()` — Chat completions
- `client.chat_stream()` — Streaming chat
- `client.embed()` — Generate embeddings
- `client.rerank()` — Document re-ranking
- `client.batch()` — Batch requests

### Tool Use
- `tools` parameter
- Tool calling

---

## Model Support

- `command-r-plus` — Most capable
- `command-r` — Balanced
- `command-light` — Fast

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: No. Models: 3+ supported.
**Last Audited**: 2025-05-03

