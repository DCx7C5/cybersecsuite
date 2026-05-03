# Google Generative AI SDK (`google-generativeai`)

**Provider**: Google Gemini  
**SDK Package**: `google-generativeai>=0.3.0`  
**Documentation**: https://github.com/google/generative-ai-python  
**OpenAPI Compatible**: ❌ No (Proprietary Google API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time token generation |
| Vision | ✅ | Image understanding |
| Tool Use | ⚠️ | Function calling (limited) |
| JSON Mode | ⚠️ | Structured output (basic) |
| Batch API | ❌ | Not available |
| Fine-tuning | ⚠️ | Limited support |
| Embeddings | ✅ | Embedding generation |
| Async/Await | ✅ | Native async support |
| Token Counting | ✅ | `count_tokens()` |
| Safety Filters | ✅ | Content filtering |

---

## Built-in Tools & Methods

### Core API
- `client.generate_content()` — Generate text
- `client.generate_content(stream=True)` — Streaming
- `client.count_tokens()` — Token counting
- `client.embed_content()` — Generate embeddings
- `client.batch_embed_contents()` — Batch embeddings

### Vision
- `PIL.Image` support
- `from_uri()` for URL-based images
- Inline image data

### Function Calling
- `GenerativeModel(tools=...)` — Define tools
- Limited function calling capabilities

### Error Handling
- `google.api_core.exceptions.GoogleAPICallError`
- `google.api_core.exceptions.InvalidArgument`
- `TypeError`, `ValueError` — Validation errors

---

## Model Support

**Latest Gemini Models**:
- `gemini-2.0-flash` — Latest
- `gemini-1.5-pro` — Previous generation
- `gemini-1.5-flash` — Fast variant

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
