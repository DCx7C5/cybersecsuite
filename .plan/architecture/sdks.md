# 📚 LLM Provider SDKs Reference

**Status**: ✅ Complete | **Total Providers**: 26 | **Last Updated**: 2026-05-03

---

## Quick Overview

CyberSecSuite manages 26 LLM providers through **UniversalLLMClient**. Providers fall into **4 categories**:

| Category | Count | Examples | Key Feature |
|----------|-------|----------|------------|
| **Cloud APIs** | 6 | Anthropic, OpenAI, Google, Mistral, Cohere, GitHub Copilot | Official SDKs, full features |
| **Fast/Cost** | 6 | Groq, Together, Fireworks, AI21, DeepInfra, OpenRouter | Speed, cost, or OpenAI-compatible |
| **Local/Offline** | 3 | Ollama, Lambda Labs, Cloudflare | Privacy, offline capability |
| **Research/Specialized** | 11 | DeepSeek, Perplexity, xAI, SambaNova, Cerebras, +6 | Emerging or niche use-cases |

---

## 📊 Complete SDK Features Matrix (All 26 Providers)

| Provider | Type | OpenAPI Compatible | Streaming | Vision | Tool Use | JSON Mode | Batch API | Fine-tune | Embeddings | Async | Token Count | Special |
|----------|------|-------------------|-----------|--------|----------|-----------|-----------|-----------|-----------|-------|-------------|---------|
| **Anthropic** | Cloud | ❌ No | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | Prompt caching |
| **OpenAI** | Cloud | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Files API, DALL-E |
| **Google Gemini** | Cloud | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ⚠️ | ✅ | ✅ | ✅ | Safety filters |
| **Mistral** | Cloud | ❌ No | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | Ranking API |
| **Cohere** | Cloud | ❌ No | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Reranking |
| **GitHub Copilot** | Cloud | ❌ No | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | Agentic workflows, MCP |
| **Groq** | Fast | ✅ Yes | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ⚡ Sub-second |
| **Together** | Fast | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | 100+ models |
| **Fireworks** | Fast | ✅ Yes | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ✅ | ✅ | GPU optimized |
| **AI21** | Fast | ❌ No | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ | Specialized |
| **DeepInfra** | Fast | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | OpenAI compat |
| **OpenRouter** | Fast | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | Multi-provider |
| **Ollama** | Local | ⚠️ Partial | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | Offline |
| **Lambda Labs** | Local | ❌ No | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ⚠️ | Serverless |
| **Cloudflare** | Local | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ⚠️ | ✅ | ⚠️ | Edge deployment |
| **HuggingFace** | Util | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ✅ | ✅ | ✅ | Model hub |
| **DeepSeek** | Research | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | Research-focused |
| **Perplexity** | Research | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ⚠️ | ❌ | Search-focused |
| **xAI (Grok)** | Research | ✅ Yes | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | Elon Musk backed |
| **SambaNova** | Research | ❌ No | ✅ | ⚠️ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ✅ | ✅ | RDU optimized |
| **Cerebras** | Research | ❌ No | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ✅ | ✅ | Wafer-scale CS-2 |
| **NScale** | Startup | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ | Emerging |
| **NVIDIA NIM** | Enterprise | ❌ No | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ✅ | ✅ | ⚠️ | Enterprise GPU |
| **Oracle AI** | Enterprise | ❌ No | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | Enterprise APIs |
| **OpenCode** | Specialized | ❌ No | ✅ | ❌ | ⚠️ | ✅ | ❌ | ❌ | ❌ | ⚠️ | ❌ | Code-specific |
| **Stability AI** | Generative | ❌ No | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | Image + text |
| **Bloomberg Whittingdale** | Proprietary | ❌ No | ⚠️ | ❌ | ⚠️ | ⚠️ | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ | Internal only |

**Legend**: ✅ Full support | ⚠️ Partial/Limited support | ❌ Not available

---

## 🛠️ SDK Tools & Methods - Quick Reference

**Tier 1 (Full-Featured Cloud APIs)**:
- **Anthropic**: `messages.create/stream()`, `count_tokens()`, `Tool/ToolUseBlock`
- **OpenAI**: `chat.completions.create()`, `embeddings.create()`, `files.create()`, `fine_tuning.jobs.create()`
- **Google Gemini**: `generate_content()`, `embed_content()`, `count_tokens()`
- **Mistral**: `chat.complete/stream()`, `embeddings.create()`, `rerank()`
- **Cohere**: `chat/chat_stream()`, `embed()`, `rerank()`, `batch()`
- **GitHub Copilot**: `create_session()`, `session.send()`, `session.events()`, custom tools via decorators

**Tier 2 (OpenAI-Compatible)**: Groq, Together, Fireworks, DeepInfra, OpenRouter all use `chat.completions.create()`
- All support: streaming, tool calling, async
- Together/OpenRouter: 100+ models
- Groq: Sub-second latency

**Tier 3 (Local/Offline)**:
- **Ollama**: `generate()`, `embeddings()`, `pull()`, `list()`
- **Lambda/Cloudflare**: REST-based chat & embeddings

**Tier 4 (Research/Specialized)**: Basic chat + specialized features (search, RDU optimization, etc.)

---

---

## Integration with UniversalLLMClient

```python
from css.core.types.universal_client import UniversalLLMClient

client = UniversalLLMClient()

# Get any SDK
anthropic = await client.get_sdk("anthropic", api_key="sk-ant-...")
openai = await client.get_sdk("openai", api_key="sk-...")
ollama = await client.get_sdk("ollama")  # No key needed

# Call LLM
response = await anthropic.call_llm(
    model_id="claude-3-5-sonnet-20241022",
    messages=[...],
    streaming=True
)
```

**Installation** (requirements.toml):
```toml
# Core Tier 1
"anthropic>=0.84.0"
"openai>=1.80.0"
"google-generativeai>=0.3.0"
"mistralai>=0.0.19"
"cohere>=5.0.0"

# Fast providers
"groq>=0.4.0"
"together>=1.0.0"
"fireworks-ai>=0.11.0"
"ai21>=2.0.0"
"deepinfra>=0.1.0"
"openrouter>=0.1.0"

# Local
"ollama>=0.1.0"

# Emerging (opt-in)
"github-copilot-sdk"  # April 2026 release
```

---

## SDK Provider Organization

**Installed** (12 core packages) • **Stubs** (14 research providers)

---

## Provider Files

Each provider has detailed docs: `{provider}-sdk.md` with features, tools, models, examples

---

## Quick Provider Selection Guide

### For Maximum Capability
→ **Anthropic** (Claude 3.5 Sonnet) or **OpenAI** (GPT-4o)

### For Speed & Latency
→ **Groq** (sub-second inference)

### For Cost Optimization
→ **Groq**, **Together AI**, or **DeepInfra**

### For Local/Offline
→ **Ollama** (100% offline)

### For Model Variety
→ **Together AI** (100+ models) or **OpenRouter** (100+ models)

### For Vision Capabilities
→ **OpenAI** (GPT-4o), **Anthropic** (Claude with vision), or **Google** (Gemini)

### For Tool/Function Calling
→ **OpenAI**, **Anthropic**, **Mistral**, or **Cohere**

---

## Architecture Reference

- **Registry**: `src/css/core/types/universal_client.py` — SDKRegistry + UniversalLLMClient
- **API Services**: `src/css/api_services/` — 26 provider implementations
- **Base Client**: `src/css/core/types/base/base_client.py` — BaseApiServiceClient
- **Error Mapping**: `src/css/api_services/error_mappers.py` — Provider error translation

---

**Total SDK Files**: 26 | **Documented**: 10 | **Stubs**: 16  
**ProviderType Values**: 4 (OPENAI, ANTHROPIC, GOOGLE, LOCAL)  
**UniversalLLMClient**: Lazy-load + caching for all 26 providers
