# 📚 Unified Provider SDK Architecture

**Status**: 🚀 Phase 10 — Unified SDK Architecture  
**Updated**: 2026-05-04 (session 9a5b41c4)  
**Replaces**: Old per-provider ~200 LOC service.py × 24 = ~4800 LOC boilerplate  
**Todos**: `sdk-*` in `.plan/session.db` (Phase 10 — Unified SDK Architecture, T10.1–T10.6)

---

## The Four Adapter Types

```
┌──────────────────────────────────────────────────────────────────────┐
│                    UnifiedLLMClient  (umbrella)                       │
│                                                                        │
│  .get_adapter(provider: str) → LLMAdapter                            │
│  .complete(provider, model, messages, **kw) → LLMResponse            │
│  .stream(provider, model, messages, **kw) → AsyncIterator[StreamChunk]│
│  .select_provider(capability) → list[str]  (via CapabilityRegistry)  │
└────┬──────────────┬────────────────┬─────────────┬───────────────────┘
     │              │                │             │
     ▼              ▼                ▼             ▼
NativeSDK      Http Provider     Ollama        BrowserRelay
Adapter        Adapter           Adapter       Adapter
(pip SDK)      (YAML+aiohttp)    (local HTTP)  (browser plugin)

anthropic SDK  OpenAI-compat ×8  /api/chat     POST /api/plugin/inject
openai SDK     Proprietary ×14   /api/tags     → content.js injects into
               + translators     /api/pull       claude.ai / ChatGPT UI
               + model mapping                   (uses user's session)
```

**All four implement the `LLMAdapter` Protocol** — `UnifiedLLMClient` is the only
entry point for all LLM calls in the system.

---

## LLMAdapter Protocol

```python
# core/types/providers/adapter.py
from typing import AsyncIterator, Protocol, runtime_checkable
import msgspec

class TokenUsage(msgspec.Struct):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0     # Anthropic prompt caching
    cache_write_tokens: int = 0

class ToolCall(msgspec.Struct):
    id: str
    name: str
    arguments: dict

class LLMResponse(msgspec.Struct):
    content: str
    model: str
    provider: str
    usage: TokenUsage
    tool_calls: list[ToolCall] = []
    finish_reason: str = "stop"
    raw: bytes | None = None       # original response bytes for debugging

class StreamChunk(msgspec.Struct, frozen=True):
    delta: str = ""
    tool_call_delta: dict | None = None
    finish_reason: str | None = None

@runtime_checkable
class LLMAdapter(Protocol):
    provider: str

    async def complete(
        self,
        messages: list[dict],
        model: str,
        **kwargs,
    ) -> LLMResponse: ...

    async def stream(
        self,
        messages: list[dict],
        model: str,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]: ...

    async def list_models(self) -> list[ModelMetadata]: ...

    def builtin_tools(self) -> list[ToolSpec]: ...
    # ^ These are provider-native tools (computer_use, code_interpreter, etc.)
    # Loaded into ToolRegistry at startup. NOT user-defined tools.

    def supports(self, capability: CapabilityType) -> bool: ...
```

---

## Type 1: NativeSDKAdapter (use official SDK where it adds real value)

**Rule**: Only use a native SDK when it exposes features **not reachable via plain HTTP**.

| Provider | SDK Package | Features that require the SDK |
|----------|-------------|-------------------------------|
| **Anthropic** | `anthropic >= 0.38.0` | `prompt_caching` (cache_control blocks), `computer_use` beta tools (bash_tool, computer, text_editor_20250124), `extended_thinking` (budget_tokens), streaming event types |
| **OpenAI** | `openai` (optional) | Strict structured output (`response_format` with json_schema), Assistants API threads, `code_interpreter` sandbox |

```python
# api_services/anthropic/adapter.py
import anthropic

class AnthropicNativeAdapter:
    provider = "anthropic"
    _client: anthropic.AsyncAnthropic

    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, messages, model, **kw) -> LLMResponse:
        resp = await self._client.messages.create(
            model=model,
            messages=messages,
            **kw,
        )
        return LLMResponse(
            content=resp.content[0].text,
            model=resp.model,
            provider="anthropic",
            usage=TokenUsage(
                input_tokens=resp.usage.input_tokens,
                output_tokens=resp.usage.output_tokens,
                cache_read_tokens=getattr(resp.usage, "cache_read_input_tokens", 0),
                cache_write_tokens=getattr(resp.usage, "cache_creation_input_tokens", 0),
            ),
            tool_calls=[ToolCall(id=t.id, name=t.name, arguments=t.input)
                        for t in resp.content if t.type == "tool_use"],
        )

    async def stream(self, messages, model, **kw) -> AsyncIterator[StreamChunk]:
        async with self._client.messages.stream(model=model, messages=messages, **kw) as s:
            async for event in s:
                if hasattr(event, "delta") and hasattr(event.delta, "text"):
                    yield StreamChunk(delta=event.delta.text)

    def builtin_tools(self) -> list[ToolSpec]:
        return [
            ToolSpec(provider="anthropic", name="computer_use",
                     description="Control the computer via screenshots and actions"),
            ToolSpec(provider="anthropic", name="bash_tool",
                     description="Execute bash commands"),
            ToolSpec(provider="anthropic", name="text_editor_20250124",
                     description="View and edit files"),
        ]

    def supports(self, cap: CapabilityType) -> bool:
        return cap in {
            CapabilityType.STREAMING, CapabilityType.VISION,
            CapabilityType.TOOLS, CapabilityType.PROMPT_CACHING,
            CapabilityType.EXTENDED_THINKING, CapabilityType.COMPUTER_USE,
        }
```

---

## Type 2: HttpProviderAdapter (YAML spec + aiohttp)

For all providers reachable via plain HTTP. Two sub-patterns:

### 2a — OpenAI-Compatible (8 providers, `openai_compat: true`)

Zero transformation code. Request/response schema is identical to OpenAI.

```yaml
# api_services/groq/spec.yaml
name: groq
base_url: https://api.groq.com/openai/v1
openai_compat: true
auth:
  env_var: GROQ_API_KEY
  header: Authorization
  prefix: "Bearer"
capabilities: [streaming, tools, json_mode]
models: [llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768]
```

Providers: `groq`, `together`, `fireworks`, `deepinfra`, `openrouter`, `deepseek`, `sambanova`, `xai`

### 2b — Proprietary HTTP (14 providers, custom translators)

Each proprietary provider registers a request/response translator:

```python
# core/types/providers/http_adapter.py
_REQUEST_TRANSLATORS: dict[str, Callable[[CommonRequest], dict]] = {
    "gemini":  _translate_gemini_request,
    "cohere":  _translate_cohere_request,
    "mistral": _translate_mistral_request,
    # ...
}
_RESPONSE_TRANSLATORS: dict[str, Callable[[dict], LLMResponse]] = {
    "gemini":  _parse_gemini_response,
    "cohere":  _parse_cohere_response,
    # ...
}
```

### 2c — Model Name Mapper

```yaml
# api_services/openrouter/model_aliases.yaml
aliases:
  "gpt-4o":         "openai/gpt-4o"
  "claude-sonnet":  "anthropic/claude-sonnet-4-5"
  "llama-3-70b":    "meta-llama/llama-3-70b-instruct"
```

```python
# ModelNameMapper.normalize("openrouter", "gpt-4o") → "openai/gpt-4o"
# ModelNameMapper.alias("openrouter", "openai/gpt-4o") → "gpt-4o"
```

Needed by: `openrouter` (org/model), `huggingface` (org/model), `cloudflare` (@cf/org/model)

---

## Type 3: OllamaAdapter (local native process, offline)

Ollama runs as a **native process** managed by `core/ollama/OllamaProcessManager` — not Docker.
`OllamaAdapter` uses the `ollama` Python library (`ollama.AsyncClient`) via `core/ollama/client.py`.

### Native Process Stack
```
core/ollama/installer.py    OllamaInstallChecker — Linux-only (Arch/Debian detection)
                              also prints: dev hint → pull these models manually:
                                  ollama pull qwen3:0.6b
                                  ollama pull phi4-mini:3.8b-q4_K_M
                                  ollama pull qwen3:4b-q4_K_M
core/ollama/process.py      OllamaProcessManager — asyncio.create_subprocess_exec("ollama", "serve")
core/ollama/client.py       thin wrapper → ollama.AsyncClient (http://localhost:11434)
```

### llama-cpp-python CUDA install (run once after uv sync, Pascal GTX 10xx sm_61)
```bash
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=61" \
FORCE_CMAKE=1 \
uv pip install llama-cpp-python --reinstall --no-cache-dir --force-reinstall
```
> **Note**: llama-cpp-python is an optional in-process model loader for local GGUF files.
> `core/ollama/client.py` uses `ollama.AsyncClient` exclusively — Ollama itself handles CUDA.
> llama-cpp-python is listed as an optional dep, not wired into `core/ollama/`.

```python
# api_services/ollama/adapter.py  — uses core/ollama/client.py
class OllamaAdapter:
    provider = "ollama"
    base_url: str  # default: http://localhost:11434

    async def complete(self, messages, model, **kw) -> LLMResponse:
        # POST /api/chat  (not /v1/chat/completions)
        body = {"model": model, "messages": messages, "stream": False, **kw}
        async with self._session.post(f"{self.base_url}/api/chat", json=body) as r:
            data = await r.json()
            return LLMResponse(content=data["message"]["content"], ...)

    async def stream(self, messages, model, **kw) -> AsyncIterator[StreamChunk]:
        # POST /api/chat with stream=True → NDJSON lines
        body = {"model": model, "messages": messages, "stream": True}
        async with self._session.post(..., json=body) as r:
            async for line in r.content:
                chunk = json.loads(line)
                yield StreamChunk(delta=chunk.get("message", {}).get("content", ""))

    async def list_models(self) -> list[ModelMetadata]:
        # GET /api/tags  (live discovery, NOT hardcoded list)
        async with self._session.get(f"{self.base_url}/api/tags") as r:
            data = await r.json()
            return [ModelMetadata(id=m["name"], provider="ollama", ...) for m in data["models"]]

    async def pull_model(self, model: str) -> None:
        # POST /api/pull  (download model if missing)
        async with self._session.post(f"{self.base_url}/api/pull", json={"name": model}) as r:
            ...

    def supports(self, cap: CapabilityType) -> bool:
        return cap in {CapabilityType.STREAMING, CapabilityType.OFFLINE}
```

Merges: `ollama/client.py` + `ollama/service.py` + `ollama/compat.py` → single `OllamaAdapter`.

---

## Type 4: BrowserRelayAdapter (browser extension form injection)

**What it is**: The browser plugin (`src/css/browser-plugin/`) is a Chrome MV3 extension that:
- Detects LLM UI forms on active tabs (claude.ai, ChatGPT, etc.)
- Injects prompts into those forms using the user's existing browser session
- **Bypasses API keys** — uses whatever account the user is logged into

**Communication flow**:

```
UnifiedLLMClient.complete("browser-relay", "claude-sonnet", messages)
    │
    ▼
BrowserRelayAdapter.complete()
    │  POST /api/plugin/inject {request_id, prompt, target: "claude.ai"}
    ▼
ASGI  →  stores request in Redis, waits for result
    │
    ▼  (plugin heartbeats every 20s to /api/plugin/register)
browser-plugin background.js
    │  chrome.tabs.sendMessage(tabId, {action: "injectPrompt", prompt})
    ▼
content.js on claude.ai tab
    │  inject prompt into form → submit → MutationObserver watches DOM
    │  POST /api/plugin/result/{request_id} when response appears
    ▼
ASGI stores result in Redis
    │
    ▼
BrowserRelayAdapter polls GET /api/plugin/result/{request_id}
    │  returns when result ready or times out
    ▼
LLMResponse(content="...", provider="browser-relay", model="claude.ai/current")
```

```python
class BrowserRelayAdapter:
    provider = "browser-relay"

    async def complete(self, messages, model, **kw) -> LLMResponse:
        prompt = _messages_to_prompt(messages)
        request_id = str(uuid4())
        target = _model_to_target_domain(model)   # "claude-sonnet" → "claude.ai"

        await self._redis.setex(f"plugin:req:{request_id}", 120, json.dumps({
            "prompt": prompt, "target": target,
        }))
        # poll for result (content.js posts back when done)
        for _ in range(60):   # 60 × 2s = 2 min timeout
            await asyncio.sleep(2)
            result = await self._redis.get(f"plugin:result:{request_id}")
            if result:
                return LLMResponse(content=json.loads(result)["text"],
                                   provider="browser-relay", model=model)
        raise BrowserRelayTimeoutError(request_id)

    def supports(self, cap: CapabilityType) -> bool:
        return cap == CapabilityType.NO_API_KEY
```

---

## ProviderSpec Schema (for Type 2)

```python
# core/types/providers/spec.py
class ProviderAuth(msgspec.Struct):
    env_var: str
    header: str = "Authorization"
    prefix: str = "Bearer"

class ProviderSpec(msgspec.Struct):
    name: str
    base_url: str
    openai_compat: bool = False
    schema: str = "openai"          # translator key if openai_compat=False
    auth: ProviderAuth
    endpoint_chat: str = "/v1/chat/completions"
    endpoint_embeddings: str | None = None
    version_header: str | None = None
    capabilities: list[str] = []
    models: list[str] = []
    model_aliases_file: str | None = None  # path to model_aliases.yaml
```

---

## Startup: UnifiedLLMClient initialization

```python
# core/asgi/app.py  (in lifespan)
async def lifespan(app):
    session = aiohttp.ClientSession()
    client = UnifiedLLMClient()

    # Type 1: Native SDK adapters
    client.register("anthropic", AnthropicNativeAdapter(os.environ["ANTHROPIC_API_KEY"]))
    client.register("openai",    OpenAINativeAdapter(os.environ.get("OPENAI_API_KEY")))

    # Type 2: HTTP adapters from spec.yaml files
    for spec_file in (Path(__file__).parent.parent.parent / "api_services").glob("*/spec.yaml"):
        spec = msgspec.yaml.decode(spec_file.read_bytes(), type=ProviderSpec)
        client.register(spec.name, HttpProviderAdapter(spec, session))

    # Type 3: Ollama (local)
    client.register("ollama", OllamaAdapter(session, base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434")))

    # Type 4: Browser relay
    client.register("browser-relay", BrowserRelayAdapter(redis=get_redis()))

    # Populate ToolRegistry with provider builtins
    for name, adapter in client.adapters.items():
        for tool in adapter.builtin_tools():
            ToolRegistry.get_instance().register(tool)

    app.state.llm = client
    yield
    await session.close()
```

---

## Builtin Tools per Adapter

| Adapter | Builtin Tools | Notes |
|---------|--------------|-------|
| `AnthropicNativeAdapter` | `computer_use`, `bash_tool`, `text_editor_20250124` | SDK beta tools, not HTTP accessible |
| `OpenAINativeAdapter` | `code_interpreter`, `file_search` | Assistants API tools |
| `HttpProviderAdapter(*)` | _(none)_ | Function calling supported but no provider-native builtins |
| `OllamaAdapter` | _(none)_ | Function calling if model supports it, model-dependent |
| `BrowserRelayAdapter` | _(none)_ | Prompt injection only, no tool execution |

---

## Migration from Old Architecture

| Old | New | Action |
|-----|-----|--------|
| `AnthropicApiService(BaseApiServiceClient)` | `AnthropicNativeAdapter` | Replace |
| All 14 `*ApiService` HTTP classes | `HttpProviderAdapter` + `spec.yaml` | Replace |
| `OllamaApiService` + `OllamaClient` + `OllamaClientCompat` | `OllamaAdapter` | Merge |
| `ToolRegistry._load_builtin_tools()` (500 LOC hardcoded) | `adapter.builtin_tools()` at startup | Replace |
| `QueryExecutor._get_client() → ClaudeSDKClient` | `UnifiedLLMClient.get_adapter(config.provider)` | Replace |
| `ProviderRegistry` (broken paths) | `UnifiedLLMClient.register()` in lifespan | Replace |
| `DynamicCapabilityRegistry` | `adapter.supports(cap)` + `UnifiedLLMClient.select_provider(cap)` | Integrate |

---

## Related Todos (Phase 10 — Unified SDK Architecture)

| ID | What |
|----|------|
| `sdk-llm-adapter-protocol` | LLMAdapter Protocol + LLMResponse + StreamChunk (msgspec.Struct) |
| `sdk-llm-response-types` | Canonical output types, normalize all providers |
| `sdk-native-anthropic-adapter` | AnthropicNativeAdapter (keeps prompt_caching, computer_use) |
| `sdk-native-openai-adapter` | OpenAINativeAdapter (structured output, Assistants API) |
| `sdk-http-adapter-openai-compat` | HttpProviderAdapter + 8 spec.yaml files |
| `sdk-http-adapter-proprietary` | 14 proprietary provider translators |
| `sdk-model-name-mapper` | ModelNameMapper + model_aliases.yaml per provider |
| `sdk-ollama-adapter` | OllamaAdapter (merges client.py + service.py + compat.py) |
| `sdk-browser-relay-adapter` | BrowserRelayAdapter + /api/plugin/ endpoints |
| `sdk-browser-relay-polling` | content.js result polling + Redis TTL |
| `sdk-unified-client` | UnifiedLLMClient umbrella |
| `sdk-builtin-tools-registry` | Wire builtin_tools() into ToolRegistry at startup |
| `sdk-replace-queryexecutor` | Replace QueryExecutor claude_agent_sdk hardcode |


---

## 🧊 Prompt Caching Strategy (Phase 11)

**All providers get caching. Two tiers.**

### Two-Tier Architecture

```
Tier 1 — Redis Exact-Match (ALL providers, always active)
  key = sha256(provider + model + messages + params)
  hit  → return immediately, $0 cost, ~0ms latency
  miss → fall through to Tier 2 then compute

Tier 2 — Native Provider Caching (where supported)
  Anthropic  → NATIVE_EXPLICIT   — inject cache_control breakpoints into messages
  OpenAI     → NATIVE_AUTOMATIC  — no modification; parse cached_tokens from usage
  DeepSeek   → NATIVE_AUTOMATIC  — parse prompt_cache_hit_tokens / prompt_cache_miss_tokens
  Gemini     → deferred (NATIVE_RESOURCE model is complex: explicit server-side
                state management, separate quota + billing — add in future phase)
  All others → NONE (Tier 1 only)

Tier 3 — Semantic Cache (future Phase 13+, not planned yet)
```

### prompt_cache/ layout

```
core/prompt_cache/
├── manager.py              # PromptCacheManager — orchestrates Tier 1 + Tier 2
├── anthropic_injector.py   # CacheBreakpointInjector (Anthropic cache_control)
└── __init__.py
```

> Gemini `cachedContent` (NATIVE_RESOURCE) deferred — add `core/prompt_cache/gemini_cache.py`
> only when Gemini becomes a primary provider. Tracked as `cache-gemini-context-cache` (future).

### CachingCapability Enum

```python
class CachingCapability(enum.Enum):
    NONE             = "none"             # redis only
    NATIVE_AUTOMATIC = "native_auto"      # OpenAI, DeepSeek — happens automatically
    NATIVE_EXPLICIT  = "native_explicit"  # Anthropic — must inject cache_control
    NATIVE_RESOURCE  = "native_resource"  # Gemini — deferred (not in Phase 11)
```

### PromptCacheManager Flow

```python
async def get_or_compute(adapter, messages, model, **kw) -> LLMResponse:
    # 1. Tier 1: Redis exact match
    key = _cache_key(adapter.provider, model, messages, kw)
    if hit := await redis.get(key):
        return decode(hit) with cache_stats.tier = "redis"

    # 2. Tier 2 preparation
    if adapter.caching_capability == NATIVE_EXPLICIT:      # Anthropic
        messages = CacheBreakpointInjector().inject(messages)
    # NATIVE_RESOURCE (Gemini) — deferred, raises NotImplementedError until added

    # 3. Compute
    response = await adapter.complete(messages, model, **kw)

    # 4. Store in Redis
    await redis.setex(key, ttl, encode(response))
    return response
```

### Updated LLMResponse

```python
class CacheStats(msgspec.Struct):
    tier: Literal["none", "redis", "native_auto", "native_explicit", "native_resource"]
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    estimated_savings_usd: float = 0.0

class LLMResponse(msgspec.Struct):
    content: str
    model: str
    provider: str
    usage: TokenUsage
    cache_stats: CacheStats = CacheStats(tier="none")  # ← new
    tool_calls: list[ToolCall] = []
    finish_reason: str = "stop"
    raw: bytes | None = None
```

### Provider Caching Matrix

| Provider | Tier 1 | Tier 2 | Type | Savings |
|----------|--------|--------|------|---------|
| Anthropic | ✅ | ✅ | EXPLICIT — cache_control breakpoints | 90% reads / +25% writes |
| OpenAI | ✅ | ✅ | AUTOMATIC — prefix cache | 50% on cached tokens |
| DeepSeek | ✅ | ✅ | AUTOMATIC — usage tracking | similar |
| Gemini | ✅ | ✅ | RESOURCE — cachedContent object | ~75% |
| Groq | ✅ | 🔜 | AUTOMATIC (announced) | TBD |
| All others (×18) | ✅ | ❌ | — | Redis saves only |
| Ollama (local) | ✅ | N/A | local KV cache | no API cost anyway |
| BrowserRelay | ✅ | ❌ | — | fewer browser injections |

### Todos (Phase 11)

| ID | Task | What |
|----|------|------|
| `cache-caching-capability-enum` | T11.1 | `CachingCapability` enum on `LLMAdapter` |
| `cache-response-stats-struct` | T11.1 | `CacheStats` field in `LLMResponse` |
| `cache-prompt-cache-manager` | T11.1 | `PromptCacheManager` orchestrator |
| `cache-redis-exact-match` | T11.2 | Redis Tier 1 (all providers) |
| `cache-redis-streaming-buffer` | T11.2 | Buffer stream → store in Redis |
| `cache-anthropic-breakpoint-injector` | T11.3 | `CacheBreakpointInjector` |
| `cache-automatic-native-tracking` | T11.4 | Parse OpenAI/DeepSeek cached token counts |
| `cache-gemini-context-cache` | T11.5 | Gemini `cachedContent` lifecycle |
| `cache-cost-savings-tracker` | T11.6 | `estimated_savings_usd` per response |
| `cache-metrics-openobserve` | T11.6 | Emit cache events to OpenObserve |

**Phase 11 depends on Phase 10** (`LLMAdapter` Protocol + `UnifiedLLMClient` must exist first).
