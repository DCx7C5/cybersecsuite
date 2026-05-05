# Deprecation Audit: `src/ai_proxy/`

**Date:** 2025-07-26  
**Verdict:** ✅ ACTIVE — no action taken

## Evidence

| Signal | Detail |
|--------|--------|
| **Imports in `src/`** | 90+ import sites across `src/proxy/asgi.py`, `src/csmcp/`, `src/accounts/`, `src/db/` |
| **CLI entrypoint** | `cybersec-proxy = "ai_proxy.cli:main"` in `pyproject.toml` |
| **`pyproject.toml` packages** | Listed under `[tool.hatch.build.targets.wheel]` |
| **Test coverage** | 7 test files: `test_ai_proxy.py`, `test_qol.py`, `test_phase0_infrastructure.py`, `test_phase8a.py`, `test_autopilot.py`, `test_scope_middleware.py`, `test_provider_auth_api.py` |
| **ASGI mounting** | `create_proxy_router()` mounted at `/v1` in `src/proxy/asgi.py` |

## Rationale

`src/ai_proxy/` is the core AI provider routing layer for the entire suite. It exposes the
OpenAI-compatible proxy API (`/v1/chat/completions`, `/v1/models`, etc.), manages provider
rate limiting, usage tracking, multi-provider routing, QoL controls, and autopilot execution.
No code was deleted or modified.
