# Provider Type Mapping (26 Providers → 4 SDK Types)

**Date**: 2026-05-03 | **Source**: Web research + codebase analysis

---

## Type 1️⃣: Official SDK Libraries (13 providers)

Maintained Python SDKs with rich feature support, async capabilities, and comprehensive documentation.

| # | Provider | SDK Package | PyPI | Status | Features |
|---|----------|-------------|------|--------|----------|
| 1 | **Anthropic** | `anthropic` | ✅ | Production | Chat, Tool Use, Vision, Agent SDK, Streaming, Batch |
| 2 | **OpenAI** | `openai` | ✅ | Production | Chat, Completions, Fine-tuning, Batch (50% cost ↓), Embeddings, Vision, Assistants |
| 3 | **Google Gemini** | `google-genai` | ✅ | Production (v2) | Chat, Embeddings, Vision, Streaming, Pydantic types |
| 4 | **Mistral** | `mistralai[agents]` | ✅ | Production | Chat, Agents (Python exec), Code Execution, Batch, Fine-tuning, Image Gen |
| 5 | **Cohere** | `cohere` | ✅ | Production | Chat, Embeddings, Rerank, Classify, Batch, Multi-cloud (AWS/Azure/GCP/OCI) |
| 6 | **Together** | `togetherai` | ✅ | Production | Chat, Completions, Embeddings, 100+ model zoo |
| 7 | **AI21** | `ai21` | ✅ | Production | Completions, Summarize, Paraphrase, Jurassic-2 models |
| 8 | **Fireworks** | `fireworks-ai` | ✅ | Production | Chat, Completions, Embeddings, Llama/DeepSeek/Stable Diffusion |
| 9 | **HuggingFace** | `huggingface_hub` | ✅ | Production | Cloud Inference API, Hosted models, Embeddings |
| 10 | **Groq** | `openai` (compat) | ✅ | Production | OpenAI-compatible, speed-optimized |
| 11 | **DeepInfra** | `openai` (compat) | ✅ | Production | OpenAI-compatible, routing-optimized |
| 12 | **OpenRouter** | `openai` (compat) | ✅ | Production | Multi-provider proxy, OpenAI-compatible |
| 13 | **GitHub Copilot** | `github-copilot-sdk` | ✅ | Public Preview (2026) | Agentic workflows, tool invocation, streaming, sessions, JSON-RPC |
| 14 | **Microsoft 365 Copilot** | `microsoft-agents-m365copilot` | 🚧 | Preview (enterprise) | Chat, M365 data integration, enterprise-only |

**🆕 MAJOR UPDATE (May 2026)**: GitHub Copilot SDK now officially available!
- `github-copilot-sdk` released April 2026 (public preview)
- Requires: Copilot CLI + GitHub subscription
- Replaces unofficial wrappers (no longer needed)
- Deprecated: Copilot Extensions (Apps) sunsetting Nov 10, 2025

**Integration Pattern**:
```python
# Type 1 direct instantiation
from anthropic import Anthropic
from openai import OpenAI
from google import genai
from copilot import CopilotClient  # NEW: Copilot SDK

# Standard
client = Anthropic(api_key="...")
client = OpenAI(api_key="...")

# Copilot (requires CLI + GitHub auth)
async with CopilotClient() as client:
    async with await client.create_session(model="gpt-5") as session:
        await session.send("Your prompt here")
```

---

## Type 2️⃣: Local/Offline SDKs (5 providers)

Models execute on user's device (no internet required after download). Privacy-preserving, latency-dependent on hardware.

| # | Provider | Runtime | Installation | Execution | Local Storage |
|---|----------|---------|--------------|-----------|---------------|
| 1 | **Ollama** | Ollama Server | Download from ollama.com | REST API (port 11434) | ~/.ollama/models/ |
| 2 | **WebLLM** | Browser/WASM | npm or browser extension | Browser (WebGPU) | Browser cache |
| 3 | **Transformers (HF)** | Python process | `pip install transformers` | In-process (torch/tensorflow) | ~/.cache/huggingface/ |
| 4 | **LM Studio** | Desktop app | Download LM Studio | GUI + REST (port 1234) | ~/LM Studio/ |
| 5 | **Llamafile** | Single binary | Download llamafile | Executable + REST | ./models/ |

**Integration Pattern**:
```python
# Type 2 local bridge
class LocalSDKClient:
    async def ollama_generate(prompt: str) -> str:
        """REST to http://localhost:11434/api/generate"""
    
    async def transformers_generate(prompt: str, model_id: str) -> str:
        """Load from ~/.cache/huggingface/"""
    
    async def lm_studio_generate(prompt: str) -> str:
        """REST to http://localhost:1234/v1/completions"""
```

**Key**: No API key required, full privacy, offline-capable.

---

## Type 3️⃣: Browser Plugin / WebLLM Protocol (3 providers)

Model execution in browser sandbox (WebGPU, WASM). Communication via extension/iframe API.

| # | Provider | Execution | Communication | Status | Privacy |
|---|----------|-----------|----------------|--------|---------|
| 1 | **WebLLM** | Browser (WebGPU) | window.__webllm_api__ or postMessage | ✅ Production | Local only |
| 2 | **Firefox AI** | Browser (on-device) | Firefox native API | 🚧 Beta/Experimental | Local only |
| 3 | **Chrome AI** | Browser (proposed) | Browser AI API (tentative) | 🚧 Experimental | Local only |

**Copilot Browser Extensions**: Technically available via VS Code/IDE plugins, but:
- No standalone browser extension (only IDE plugins)
- No official REST API or Python SDK
- Uses OpenAI backend (proprietary integration)
- **Recommendation**: Use OpenAI SDK directly instead

**Integration Pattern**:
```python
# Type 3 browser bridge
class BrowserPluginSDKClient:
    async def communicate_with_webllm(prompt: str, ws_url: str) -> str:
        """
        Bridge: Python → WebSocket → Browser ServiceWorker → WebLLM
        OR: Python → HTTP proxy → Browser iframe → WebLLM
        """
```

**Key**: Sandboxed browser execution, full user privacy, latency depends on browser.

---

## Type 4️⃣: Custom REST Wrappers (5 confirmed + 8 emerging)

Emerging providers, niche services, or enterprises with non-standard APIs. Custom HTTP wrapper required.

### Confirmed Type 4 Providers (5)

| # | Provider | API Style | Status | Use Case |
|---|----------|-----------|--------|----------|
| 1 | **Lambda Labs** | Compute API | ✅ Production | GPU provisioning (not LLM API) |
| 2 | **Cloudflare Workers AI** | REST (edge) | ✅ Production | Edge compute, limited models |
| 3 | **NScale** | Enterprise REST | ⚠️ Limited | Research/enterprise partnerships |
| 4 | **SambaNova** | Enterprise REST | ⚠️ Limited | Specialized hardware (CoAttn processor) |
| 5 | **Cerebras** | Specialized REST | ⚠️ Limited | Inference speed focus |

### Emerging Type 4 Providers (8) — Require Research

| # | Provider | API Style | Research Status | Notes |
|---|----------|-----------|-----------------|-------|
| 1 | **DeepSeek** | REST (emerging) | 🔍 Pending | Chinese LLM, rising adoption |
| 2 | **Perplexity** | REST or OpenAI-compat? | 🔍 Pending | Web search integrated |
| 3 | **Xai/Grok** | REST (emerging) | 🔍 Pending | Elon's LLM initiative |
| 4 | **OpenCode** | Community REST | 🔍 Pending | Community-driven, lower priority |
| 5 | **Stability AI** | REST (image focus) | 🔍 Pending | Stable Diffusion, image gen |
| 6 | **NVIDIA NIM** | Container REST | 🔍 Pending | Enterprise inference |
| 7 | **Oracle AI** | Cloud API | 🔍 Pending | OCI-native models |
| 8 | **Bloomberg Whittingdale** | Proprietary | 🔍 Pending | Finance-specific (low priority) |

**Integration Pattern**:
```python
# Type 4 custom wrapper
class CustomRestWrapper:
    """Base class for Type 4 providers"""
    async def call_api(prompt: str, **kwargs) -> str:
        """HTTP POST to provider endpoint, translate response"""
        # - Custom JSON schema translation
        # - Auth handling (bearer, custom headers, etc.)
        # - Error code mapping
        # - Rate limit management

class DeepSeekWrapper(CustomRestWrapper):
    """Implement per-provider quirks"""
    api_base = "https://api.deepseek.com/v1"
    auth_type = "bearer_token"  # or custom
```

**Key**: Most are REST, some may be OpenAI-compatible, others need custom translation.

---

## Summary Table (All 28 - Updated with Copilot SDKs)

| Type | Category | Count | Examples | SDK Status |
|------|----------|-------|----------|-----------|
| **1️⃣** | Official SDKs | 15 | Anthropic, OpenAI, Gemini, Groq, **GitHub Copilot**, M365 Copilot, ... | ✅ Production / 🚧 Preview |
| **2️⃣** | Local/Offline | 5 | Ollama, WebLLM, Transformers, LM Studio, Llamafile | ✅ Production |
| **3️⃣** | Browser Plugin | 3 | WebLLM (browser), Firefox AI, Chrome AI (future) | ✅/🚧 Mixed |
| **4️⃣** | Custom Wrappers | 5 | Lambda Labs, Cloudflare, NScale, SambaNova, Cerebras | ⚠️ Limited |
| **4️⃣ (Emerging)** | Custom Wrappers | 8 | DeepSeek, Perplexity, Xai, OpenCode, Stability, NVIDIA, Oracle, Bloomberg | 🔍 Pending Research |

**Total**: 28 providers (+2 with Copilot SDKs)

---

## Integration Priorities

### Priority 1: Type 1 (Official SDKs) ✅ MOSTLY DONE
- [x] All 15 providers researched and documented
- [x] **NEW**: GitHub Copilot SDK (April 2026 release)
- [x] **NEW**: Microsoft 365 Copilot SDK (enterprise preview)
- [x] Code examples provided
- [x] `-sdk.md` files created

### Priority 2: Type 2 (Local Models) 🟡 IN PROGRESS
- [ ] LocalSDKClient wrapper implementation
- [ ] Ollama bridge (REST to port 11434)
- [ ] Transformers pipeline bridge (auto-download/cache)
- [ ] LM Studio bridge (REST to port 1234)
- [ ] WebLLM HTTP proxy (browser communication)

### Priority 3: Type 3 (Browser Plugins) 🟡 IN PROGRESS
- [ ] WebLLM HTTP bridge implementation
- [ ] Browser API communication pattern
- [ ] Sandbox security considerations

### Priority 4: Type 4 (Custom Wrappers) 🟠 PENDING
- [ ] Base CustomRestWrapper class
- [ ] Lambda Labs wrapper
- [ ] Cloudflare wrapper
- [ ] Research remaining 8 providers

---

## Configuration by Type

### Type 1: Official SDK Config
```python
ProviderConfig(
    type=SDKType.OFFICIAL_SDK,
    provider="anthropic",
    sdk_package="anthropic",
    auth_method="api_key",
    api_key_env="ANTHROPIC_API_KEY",
)
```

### Type 2: Local SDK Config
```python
ProviderConfig(
    type=SDKType.LOCAL_SDK,
    provider="ollama",
    local_runtime="ollama",
    endpoint="http://localhost:11434",
    model_cache_dir="~/.ollama/models/",
)
```

### Type 3: Browser Plugin Config
```python
ProviderConfig(
    type=SDKType.BROWSER_PLUGIN,
    provider="webllm",
    bridge_url="http://localhost:8765/ws/webllm",  # Python proxy
    # OR
    browser_ext_port=5555,  # Direct browser extension port
)
```

### Type 4: Custom Wrapper Config
```python
ProviderConfig(
    type=SDKType.CUSTOM_WRAPPER,
    provider="deepseek",
    api_base="https://api.deepseek.com/v1",
    auth_method="bearer_token",
    api_key_env="DEEPSEEK_API_KEY",
    wrapper_class="src.css.core.api_clients.provider_wrappers.deepseek_wrapper.DeepSeekWrapper",
)
```

---

## Research Status

| Type | Researched | Documented | Integrated | Test Coverage |
|------|-----------|-----------|-----------|---|
| **Type 1 (Official)** | ✅ Complete | ✅ 13 files | ❌ Partial | ⏳ Pending |
| **Type 2 (Local)** | ✅ Complete | ✅ Started | ❌ Not started | ⏳ Pending |
| **Type 3 (Browser)** | ⚠️ Partial | ⚠️ Partial | ❌ Not started | ⏳ Pending |
| **Type 4 (Custom)** | 🔍 5/13 | 🔍 5/13 | ❌ Not started | ⏳ Pending |

---

## Next Actions

1. **Complete Type 4 Research**: Web search each of the 8 emerging providers (DeepSeek, Perplexity, etc.)
2. **Update sdks.md**: Add "SDK Type" column to main feature matrix
3. **Implement LocalSDKClient**: Bridge Ollama, Transformers, LM Studio
4. **Implement CustomRestWrapper**: Base class + Lambda Labs example
5. **Refactor SDKRegistry**: Route by type in UniversalLLMClient
6. **Create Provider Selection Guide**: Decision tree based on use case
