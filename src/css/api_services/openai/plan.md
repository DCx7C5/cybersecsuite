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

---

## Builtin Tools

### Available Tools (3)

1. **code_interpreter** — Execute Python code and get results (in Code Interpreter mode)
   - Parameters: `code` (string, required) — Python code to execute
   - Returns: object with stdout, stderr, and artifacts
   - Timeout: 60 seconds
   - Tags: code, execution, python

2. **file_search** — Search through files and retrieve relevant content
   - Parameters: `query` (string, required) — Search query
   - Returns: array of matching files and excerpts
   - Timeout: 30 seconds
   - Tags: search, retrieval

3. **retrieval** — Retrieve documents from uploaded files
   - Parameters: `query` (string, required) — Retrieval query
   - Returns: array of document chunks
   - Timeout: 30 seconds
   - Tags: retrieval, knowledge_base

### Tool Schema Format (ToolSchema)

All tools are normalized to:

```python
@dataclass
class ToolSchema:
    provider: str = "openai"
    name: str  # e.g., "code_interpreter"
    description: str
    parameters: list[ToolParameter]
    returns: ToolReturnType
    version: str = "1.0"
    enabled: bool = True
    tags: list[str]
    requires_auth: bool = False
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
```

### Registration

Tools are auto-registered with @tools registry on startup:
- See: `src/css/modules/tools/registry.py`
- Access: `from css.modules.tools.registry import get_tool_registry`

### How to Add Provider Tools

For new providers in `src/css/api_services/{provider}/`:

1. Create `tools.py` with `BUILTIN_TOOLS` constant
2. Follow ToolSchema format in `src/css/modules/tools/models.py`
3. Registry auto-discovers on startup (add to `ToolRegistry._load_builtin_tools()`)
