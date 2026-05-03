# AI21 Labs SDK (`ai21`)

**Provider**: AI21 Labs  
**SDK Package**: `ai21>=2.0.0`  
**Documentation**: https://github.com/AI21Labs/ai21-python  
**OpenAPI Compatible**: ❌ No (Proprietary AI21 API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Streaming support |
| Vision | ❌ | Not available |
| Tool Use | ✅ | Function calling |
| JSON Mode | ✅ | Structured output |
| Batch API | ✅ | Batch processing |
| Fine-tuning | ✅ | Custom models |
| Embeddings | ❌ | Not available |
| Async/Await | ✅ | Native async |
| Specialized | ✅ | Research-focused |

---

## Built-in Tools & Methods

### Core API
- `client.completion.create()` — Text completion
- `client.summarize()` — Summarization
- `client.library()` — Pre-built modules

### Batch API
- `client.batch()` — Bulk operations

---

## Model Support

- `j2-ultra` — Largest model
- `j2-mid` — Balanced
- `j2-light` — Fast

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
---
## Audit (2025-05-03)
**Status**: Complete | **Files**: 2/5 | **Pattern**: ✅
**Findings**: Complete. OpenAI-compatible: No. Models: 3+ supported.
**Last Audited**: 2025-05-03

