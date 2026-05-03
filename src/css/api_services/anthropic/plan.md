# Anthropic SDK (`anthropic`)

**Provider**: Anthropic Claude  
**SDK Package**: `anthropic>=0.84.0` with `anthropic[aiohttp]`  
**Documentation**: https://github.com/anthropics/anthropic-sdk-python  
**OpenAPI Compatible**: ❌ No (Proprietary API)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time token streaming |
| Vision | ✅ | Image understanding via base64 or URL |
| Tool Use | ✅ | Function calling and tool integration |
| JSON Mode | ✅ | Structured output support |
| Batch API | ❌ | Not available |
| Fine-tuning | ❌ | Not available |
| Embeddings | ✅ | `text-embedding-3` models |
| Async/Await | ✅ | Native async support |
| Token Counting | ✅ | `count_tokens()` method |
| Prompt Caching | ✅ | Cache frequently used prompts |

---

## Built-in Tools & Methods

### Core Message API
- `client.messages.create()` — Synchronous completion
- `client.messages.stream()` — Streaming with context manager
- `client.messages.create_with_overrides()` — Overridable parameters

### Async Methods
- `AsyncAnthropic.messages.create()` — Async completion
- `AsyncAnthropic.messages.stream()` — Async streaming

### Helper Methods
- `client.get_model_info()` — Get model capabilities
- `client.count_tokens()` — Count tokens in request

### System Features
- `Tooluse` — Built-in tool use handler
- `Vision` — Image input support
- `TextBlock`, `ToolUseBlock` — Message content types
- `Tool`, `ToolChoice` — Tool definitions

### Error Handling
- `APIError` — Base API error
- `RateLimitError` — HTTP 429
- `APIConnectionError` — Connection issues
- `Timeout` — Request timeout
- `APIStatusError` — HTTP errors

---

## Model Support

**Latest Claude Models**:
- `claude-3-5-sonnet-20241022` — Latest, most capable
- `claude-3-opus-20250219` — Extended thinking support
- `claude-3-sonnet-20240229` — Previous generation
- `claude-3-haiku-20240307` — Fastest, cheapest

---

## Usage Examples

### Basic Completion
```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Streaming
```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[...]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Tool Use
```python
tools = [{
    "name": "get_weather",
    "description": "Get weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"]
    }
}]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[...]
)
```

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03

---

## Builtin Tools

### Available Tools (1)

1. **computer_use** — Use computer vision and interaction tools to accomplish tasks
   - Parameters:
     - `action` (string, required, enum) — Screenshot, click, type, scroll, key_press
     - `coordinates` (array, optional) — [x, y] for mouse actions
     - `text` (string, optional) — Text to type
   - Returns: object with action result (screenshot data, click result, etc.)
   - Timeout: 30 seconds
   - Tags: computer_vision, interaction
   - Requires Auth: False

### Tool Schema Format (ToolSchema)

All tools are normalized to canonical format in `src/css/modules/tools/models.py`:

```python
@dataclass
class ToolSchema:
    provider: str = "anthropic"
    name: str  # e.g., "computer_use"
    description: str
    parameters: list[ToolParameter]
    returns: ToolReturnType
    version: str = "1.0"
    enabled: bool = True
    tags: list[str]
    requires_auth: bool = False
    timeout_seconds: int = 30
```

### Registration

Auto-registered with @tools registry:
- Location: `src/css/modules/tools/registry.py`
- Usage: `from css.modules.tools.registry import get_tool_registry; registry = get_tool_registry()`

### Extending Tool Support

To add more Anthropic tools:
1. Define in `src/css/api_services/anthropic/tools.py`
2. Follow ToolSchema in `src/css/modules/tools/models.py`
3. Update `ToolRegistry._load_builtin_tools()` to include
