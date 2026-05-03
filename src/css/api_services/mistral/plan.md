# Mistral AI SDK (`mistralai`)

**Provider**: Mistral AI  
**SDK Package**: `mistralai>=0.0.19`  
**Documentation**: https://github.com/mistralai/client-python  
**OpenAPI Compatible**: ❌ No (Proprietary Mistral API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time token streaming |
| Vision | ✅ | Image understanding |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| Batch API | ❌ | Not available |
| Fine-tuning | ❌ | Not available |
| Embeddings | ✅ | Embedding models |
| Async/Await | ✅ | Native async |
| Token Counting | ✅ | Token counter |
| Ranking | ✅ | Re-ranking API |

---

## Built-in Tools & Methods

### Core API
- `client.chat.complete()` — Synchronous chat
- `client.chat.stream()` — Streaming chat
- `client.embeddings.create()` — Generate embeddings
- `client.rerank()` — Re-rank documents

### Tool Use
- `tools` parameter
- Tool definitions with descriptions

### Error Handling
- `MistralAPIException`
- `MistralConnectionError`

---

## Model Support

- `mistral-large-latest` — Most capable
- `mistral-medium-latest` — Balanced
- `mistral-small-latest` — Fast

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: No. Models: 3+ supported.
**Last Audited**: 2025-05-03

