# OpenAI SDK (`openai`)

**Provider**: OpenAI GPT  
**SDK Package**: `openai>=1.80.0`  
**Documentation**: https://github.com/openai/openai-python  
**OpenAPI Compatible**: ✅ Yes (OpenAI Standard - Reference Implementation)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Server-sent events streaming |
| Vision | ✅ | GPT-4 vision image analysis |
| Tool Use | ✅ | Function calling (tool_choice) |
| JSON Mode | ✅ | Structured output support |
| Batch API | ✅ | Cost-effective bulk processing |
| Fine-tuning | ✅ | Custom model training |
| Embeddings | ✅ | `text-embedding-3` models |
| Async/Await | ✅ | Native async support |
| Token Counting | ✅ | `tiktoken` integration |
| Files API | ✅ | File uploads for RAG |

---

## Built-in Tools & Methods

### Core API
- `client.chat.completions.create()` — Synchronous completion
- `client.chat.completions.create(stream=True)` — Streaming completion
- `client.embeddings.create()` — Generate embeddings
- `client.files.create()` — Upload files
- `client.fine_tuning.jobs.create()` — Create fine-tuning job
- `client.beta.batch.upload_batch()` — Submit batch requests

### Async Methods
- `AsyncOpenAI.chat.completions.create()` — Async completion
- `AsyncOpenAI.chat.completions.stream()` — Async streaming

### Models
- `client.models.list()` — List available models
- `client.models.retrieve()` — Get model info

### Vision
- Support for `image_url` in messages
- Vision-capable models: `gpt-4-vision-preview`, `gpt-4o`

### Tool Use
- `tools` parameter with function definitions
- `tool_choice="auto"` for automatic tool selection
- `parallel_tool_calls` for multiple simultaneous tool calls

### Error Handling
- `OpenAIError` — Base error
- `RateLimitError` — HTTP 429
- `APIConnectionError` — Connection failures
- `AuthenticationError` — Invalid credentials
- `APITimeoutError` — Request timeout

---

## Model Support

**Latest GPT Models**:
- `gpt-4o` — Latest, most capable
- `gpt-4-turbo` — Previous generation (long context)
- `gpt-4-vision-preview` — Vision support
- `gpt-3.5-turbo` — Fast, cheap alternative
- `gpt-4` — Original GPT-4

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
