# Browser Plugin Module

**Status**: 🟡 Planned with backend-priority contract | **Primary Phase**: 10 (Unified SDK Architecture)

## Purpose

Browser extension/backend relay surface for provider calls when direct API-key routes are unavailable or intentionally bypassed.

## Active Tracker Mapping (session.db)

- `sdk-browser-relay-adapter`
- `sdk-browser-relay-polling`
- `sdk-deepseek-adapter`
- `sdk-browser-relay-provider-priority`
- `sdk-browser-relay-web-llm-relay`

## Provider Priority Contract

Browser-plugin backend provider order is explicitly tracked as:

1. `github`
2. `codex`
3. `openai`
4. `deepseek`
5. `nvidia`
6. web-LLM relay path (`grok.com` / `docs.claude.com` strategy)

## Planned Files

- `manifest.json` — extension manifest
- `popup.*` — operator controls and status
- `background.js` — relay orchestration service worker
- `content.js` — page integration and result relay callbacks

## Dependencies

- `src/css/core/sdks/adapters/` (browser relay + deepseek adapter)
- `src/css/modules/llm_proxy/` (stream/result normalization path)
- `src/css/core/settings/` (relay provider preferences/config)

## Acceptance Contract

- Provider fallback follows the declared priority order and reports the chosen
  relay/provider in normalized metadata.
- Authentication or browser-session material is not logged or exposed to
  frontend callers.
- Failed relay attempts degrade to the next configured provider with typed
  failure reporting.
