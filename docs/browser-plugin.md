# Browser Plugin

The CyberSecSuite browser extension (`src/browser-plugin/`) connects your browser to the local dashboard, enabling AI-assisted injection, AJAX capture, and response relay for web-based LLM interfaces.

---

## Installation

1. Open Chrome/Brave → `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select `src/browser-plugin/`

The extension requires:
- Dashboard running at `http://localhost:8000` (or configured URL)
- `host_permissions` for target domains (see `manifest.json`)

---

## Features

### Form Detection (T023)
Shadow DOM traversal with multi-candidate scoring detects chat input fields on:
- `claude.ai`, `chat.openai.com`, `console.anthropic.com`
- `github.com`, `platform.openai.com`, and any configured domain

Scoring prefers `contenteditable` divs with `role="textbox"` or matching placeholders over plain textareas.

### Idle Detection (T024)
Keystroke + mouse tracking suppresses injection when the user is active. Idle threshold is configurable. The dashboard activity endpoint (`GET /api/activity`) is checked before each stream injection to avoid conflicts.

### Multi-Tab Targeting (T025)
Background service worker tracks detected forms across **all** open tabs (not just the active one). The Inject panel shows a **Target tab** selector populated with every tab that has a detected form. Selecting a specific tab routes inject/abort/detect messages to that tab via `chrome.tabs.sendMessage`, regardless of focus state.

Message flow for non-active tab injection:
```
popup.js → chrome.runtime.sendMessage({ action: "injectToTab", tabId, msg })
         → background.js → chrome.tabs.sendMessage(tabId, msg)
         → content.js (target tab) → injectStreamPrompt / injectText
```

### Streaming Injection (T027 / T028)
Prompts are sent to `POST /api/proxy/memory-chat` on the dashboard, which routes through the AI proxy with memory tools. The response streams as SSE and is typed character-by-character into the detected form field using realistic `keydown/input/keyup` sequences.

Options:
- **Typing speed** (ms/char) — default 28 ms
- **Auto-submit** — click submit button or press Enter after typing

### Response Relay (T027)
XHR/fetch interception captures API calls matching configured patterns (`/v1/messages`, `api.anthropic.com`, etc.) and relays them to the dashboard AJAX log. Captured request/response bodies appear in the **AJAX** tab.

### WebLLM Routing (T026)
Requests tagged with `X-WebLLM: true` (header) or `"webllm": true` (body) in the AI proxy are routed to `AuthType.BROWSER` providers (Playwright executor) before falling back to API providers. This allows the dashboard to inject prompts into browser sessions and relay responses back.

---

## API Endpoints Used

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/proxy/memory-chat` | POST | Stream AI response with memory context |
| `/api/activity` | GET | Check if dashboard is in use (idle guard) |
| `/api/plugin/register` | POST | Register plugin instance + heartbeat |

---

## Configuration

In the **Settings** tab:

| Setting | Default | Notes |
|---|---|---|
| Dashboard URL | `http://localhost:8000` | Local dashboard address |
| Active domains | (list) | Domains where AI features activate |
| AJAX patterns | (list) | URL substrings to intercept |
| Typing speed | 28 ms/char | Human-like input simulation |
| Auto-submit | Off | Submit after injection |

---

## Background Service Worker

`background.js` (Manifest V3 service worker) handles:
- Config persistence via `chrome.storage.local`
- Domain activation checks
- Form auto-detection on all active domain tabs (on create, update, activate)
- Message routing: `getTabInfo`, `listTargetTabs`, `injectToTab`, `injectPromptManual`
- Dashboard registration + 20 s heartbeat

---

## Popup Tabs

| Tab | Purpose |
|---|---|
| Status | Active tab info, form detection badge, stream/ajax/form counters, event log |
| Inject | Target tab selector, prompt textarea, stream/text inject, abort, form detect |
| AJAX | Intercepted API calls with request/response bodies |
| Settings | Dashboard URL, domains, patterns, typing speed, enable toggle |

---

## Security

- Content scripts only activate on domains in `activeDomains`
- No credentials are stored in the extension; all auth is handled by the dashboard
- AJAX capture is opt-in via `ajaxPatterns` list
- Idle detection prevents injection when user is actively typing

---

## Changelog

- **v4.0** (T023–T028): Shadow DOM form detection, idle detection, multi-tab targeting, streaming injection via dashboard, response relay
- **v3.0**: WebSocket removed, streaming via Anthropic SDK + dashboard endpoints
