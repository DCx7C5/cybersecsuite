# Frontend E2E Testing Guide

## Setup

```bash
cd src/frontend
npm install --save-dev @playwright/test
```

## Running Tests

```bash
# All tests
npm run test:e2e

# Single file
npm run test:e2e tests/e2e/bootstrap.spec.ts

# Watch mode
npm run test:e2e --watch

# Debug
npm run test:e2e --debug
```

## Test Structure

- `bootstrap.spec.ts` — Page load, sidebar render, lazy-loading of 33 panels
- `chat.spec.ts` — Chat SSE streaming, token parsing, error handling
- `tables.spec.ts` — Table sort, filter, pagination
- `theme.spec.ts` — Theme switching (blue/purple/red), localStorage persistence
- `errors.spec.ts` — Error boundaries, malformed API responses

## Attributes for Testing

Add `data-test` attributes to components:

```tsx
<div data-test="nav-item" data-tab="chat">Chat</div>
<button data-test="chat-send">Send</button>
<div data-test="chat-input">...</div>
```

## CI Integration

Tests run on every PR (`.github/workflows/e2e.yml`):
- Chrome browser
- Backend must be running (or mocked)
- Artifacts: HTML report, screenshots on failure

## Performance Targets

- Initial load: < 3s
- Panel lazy-load: < 1s
- SSE token arrival: < 500ms
- Theme switch: < 300ms
