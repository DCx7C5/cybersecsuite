# AI Proxy

Multi-provider AI routing with an OpenAI-compatible `/v1/*` API endpoint.

## Overview

The AI proxy provides a single OpenAI-compatible endpoint that routes requests across 9 AI providers using 13 configurable strategies. It includes a circuit breaker, per-provider rate limiting, token/cost tracking, and a CLI for direct interaction.

## Quick Start

```bash
# List all configured providers
make proxy-providers

# List all available models
make proxy-models

# Chat via CLI
make proxy-chat PROMPT="Explain ARP poisoning"

# Via curl (OpenAI-compatible)
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "hello"}]}'
```

## Providers

60 providers supported (9 core + 51 extended). Core providers:

| ID | Name | Free tier | Notes |
|----|------|-----------|-------|
| `anthropic` | Anthropic | No | Claude 3.5/3 Haiku, Sonnet, Opus |
| `openai` | OpenAI | No | GPT-4o, o1, o3-mini |
| `gemini` | Google Gemini | Yes (limited) | 1.5 Pro/Flash, 2.0 Flash |
| `deepseek` | DeepSeek | No | V3, R1 — cost-optimized |
| `groq` | Groq | Yes (limited) | Llama-3.3, Mixtral — ultra-low latency |
| `mistral` | Mistral | No | mistral-large, codestral |
| `xai` | xAI Grok | No | Grok-2, Grok-beta |
| `together` | Together AI | No | 60+ open models |
| `openrouter` | OpenRouter | No | 200+ models aggregator |

Extended providers include: AI21, AIML API, Alibaba, Baseten, Cerebras, Chutes, Cloudflare, Cohere, Databricks, DeepInfra, Featherless, Fireworks, FriendliAI, Galadriel, Heroku, HuggingFace, Hyperbolic, Kimi, Lambda, LM Studio, Lepton AI, Meta Llama, MiniMax, Moonshot, NanoGPT, Nebius, Novita, Nscale, NVIDIA, OVHcloud, Ollama, Perplexity, Perplexity Search, Pollinations, Qwen, Reka AI, Replicate, RunPod, SambaNova, Scaleway, SiliconFlow, StepFun, Upstage, Venice, Volcengine, W&B, Writer, Yi (01.AI), Zhipu AI, and browser-based Grok (x.com + grok.com).

A provider is active when its API key env var is set. See [configuration.md](../../docs/configuration.md) for key names.

## Routing Strategies

13 strategies available in `src/ai_proxy/routing/combo.py`:

| Strategy | Description |
|----------|-------------|
| `priority` | Ordered list — first success wins (default) |
| `round-robin` | Rotate through targets sequentially |
| `cost-optimized` | Cheapest model first |
| `weighted` | Probabilistic by assigned weight |
| `random` | Shuffle randomly before trying |
| `strict-random` | Pure random — no deduplication |
| `least-used` | Fewest past requests first |
| `fill-first` | Fill one provider's quota before moving on |
| `p2c` | Power of Two Choices — pick best of two random |
| `lkgp` | Last Known Good Provider — stick with what worked |
| `auto` | Auto-select based on request context |
| `context-optimized` | Best context window for message length |
| `context-relay` | Relay conversation context across provider accounts |

## Circuit Breaker

Each provider has an automatic circuit breaker:
- **Threshold**: 5 consecutive failures
- **Recovery**: 60 seconds cooldown
- **State**: `closed` (normal) → `open` (tripped) → `half-open` (testing)

Check circuit breaker status via MCP tool `cybersec.get_circuit_breakers` or the dashboard at `/dashboard/api/routing`.

## Rate Limiter

Per-provider limits enforced at startup from `ProviderConfig.rate_limit_rpm` and `rate_limit_tpm`. Configure in `src/ai_proxy/services/rate_limiter.py`.

## Architecture

```
/v1/chat/completions
        │
        ▼
  create_proxy_router()   (routes.py)
        │
        ▼
  ComboConfig resolution  (routing/combo.py)
  → strategy applied
  → targets ordered
        │
        ▼
  Provider executor       (executors/)
  → translator adapts request/response format
  → rate limiter checked
  → circuit breaker checked
        │
        ▼
  Provider API (HTTP)
        │
        ▼
  UsageTracker logs tokens + cost (services/usage_tracker.py)
```

## Files

| File | Purpose |
|------|---------|
| `routes.py` | Starlette router — `/v1/chat/completions`, `/v1/models` |
| `routing/combo.py` | 13 routing strategies, circuit breaker, budget guard |
| `providers/registry.py` | 9 provider definitions, `ProviderConfig` |
| `services/rate_limiter.py` | Per-provider RPM/TPM enforcement |
| `services/usage_tracker.py` | Token + cost tracking (DB-backed) |
| `translators/` | Request/response format adapters per provider |
| `executors/` | Async HTTP execution per provider |
| `cli.py` | CLI: providers, models, chat commands |

## MCP Tools

The MCP server exposes these proxy-related tools:

- `cybersec.proxy_chat` — send a chat request via the proxy
- `cybersec.proxy_providers` — list active providers
- `cybersec.proxy_models` — list available models
- `cybersec.proxy_usage` — token + cost usage stats
- `cybersec.proxy_cost` — cost breakdown by provider
- `cybersec.simulate_route` — simulate routing without sending
- `cybersec.explain_route` — explain how a request would be routed
- `cybersec.routing_strategies` — list all strategies
- `cybersec.set_budget_guard` — set a spend limit
- `cybersec.get_circuit_breakers` — circuit breaker states
- `cybersec.best_provider` — recommend best provider for a task
