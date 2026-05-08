# Frontend Architecture

**Last Updated**: 2026-05-04T21:26 (session ffed87aa)  
**Phase**: 18 — Frontend Foundation  
**Status**: 🟡 Planned — 19 todos, 0 done

---

## Guiding Principle

> Code that belongs together stays.

Each Python module owns its own React panel in a colocated `templates/` subdirectory. The frontend shell (`src/frontend/`) is infrastructure — it discovers panels via a central registry, not filesystem scanning.

---

## Directory Layout

```
src/frontend/                              ← Vite shell (infrastructure only)
├── package.json                           ← bun workspaces; react19, vite, TS, tailwindv4, shadcn
├── vite.config.ts                         ← Path aliases + dev proxy
├── tsconfig.json                          ← strict mode
└── src/
    ├── main.tsx                           ← ReactDOM + RouterProvider + QueryClientProvider
    ├── App.tsx                            ← AppShell (sidebar + outlet)
    ├── router.tsx                         ← TanStack Router: routes from MODULE_PANELS
    ├── module-registry.ts                 ← MODULE_PANELS[] — add entry → appears in nav
    ├── store.ts                           ← Zustand: wsStatus, activeAgents, recentEvents, metricsSlice
    ├── core/
    │   ├── layout/
    │   │   ├── AppShell.tsx               ← Dark shell wrapper
    │   │   ├── Sidebar.tsx                ← Nav from MODULE_PANELS (ref: ahs-admin-panel/Sidebar)
    │   │   ├── TopBar.tsx                 ← Breadcrumb + WS badge + API badge
    │   │   └── PanelContainer.tsx         ← Suspense skeleton + ErrorBoundary per panel
    │   ├── api/
    │   │   ├── client.ts                  ← Typed fetch (apiGet/apiPost/apiPut/apiDelete) + ApiError
    │   │   ├── ws-manager.ts              ← PORT ahs-admin-panel/useSocket.ts — singleton, typed subscribe
    │   │   └── sse-client.ts              ← AsyncGenerator<T> over HTTP SSE
    │   ├── hooks/                         ← PORTED from ahs-admin-panel
    │   │   ├── useWebSocket.ts
    │   │   ├── useSSE.ts                  ← Consumes sse-client → React state
    │   │   ├── useApi.ts                  ← TanStack Query wrapper + toast errors
    │   │   ├── useStorage.ts
    │   │   ├── useEventListener.ts
    │   │   ├── useBreakPoint.ts
    │   │   ├── useClientWidth.ts
    │   │   ├── useDragResizeHeight.ts
    │   │   ├── useDraggable.ts            ← Grid-snap free-drag with localStorage pos
    │   │   ├── useList.ts
    │   │   ├── useAsync.ts
    │   │   └── useIntersectionObserver.ts ← Virtual scroll trigger
    │   ├── charts/                        ← Recharts, dark zinc palette, WS-fed
    │   │   ├── TokenUsageChart.tsx        ← AreaChart: input/output tokens last 60min
    │   │   ├── LatencyChart.tsx           ← LineChart: p50/p95/p99 per minute
    │   │   ├── AgentActivityBar.tsx       ← BarChart: calls per model last hour
    │   │   └── EventRateSparkline.tsx     ← Tiny sparkline for dashboard cards
    │   ├── providers/
    │   │   └── SocketProvider.tsx         ← PORT ahs-admin-panel/SocketProvider.tsx
    │   └── components/
    │       ├── StatusBadge.tsx
    │       ├── JsonTree.tsx               ← Dark collapsible JSON viewer
    │       ├── CodeBlock.tsx              ← Shiki syntax highlighting
    │       └── DataTable.tsx              ← shadcn DataTable (sort/filter/paginate)
    ├── pages/
    │   └── LandingDashboard.tsx           ← Route `/` — live ops overview
    └── ui/                                ← shadcn/ui copy-paste components (YOU own them)
        ├── button.tsx
        ├── card.tsx
        └── ... (add per-need: bunx shadcn add <component>)

src/css/modules/<name>/templates/          ← MODULE-COLOCATED panels
    ├── index.tsx                          ← default export: <NamePanel />
    ├── components/
    ├── hooks.ts                           ← useSettings(), useChat(), etc.
    └── types.ts                           ← TypeScript types matching Python API schemas
```

> **`templates/` naming rule**: colocated panel dirs are named `templates/` NOT `frontend/`.  
> Exception: YAML profiles in `@settings` live in `profiles/` to avoid collision.

---

## Stack Decisions

| Choice | Version | Why |
|--------|---------|-----|
| **Bun** | latest | Package manager + runtime. Never npm/yarn. |
| **Vite** | 6 | Fastest HMR, Bun-native, excellent TS DX |
| **React** | 19 | `use()` hook for streaming/Suspense; familiar |
| **TypeScript** | strict | Catches API contract mismatches at compile time |
| **Tailwind CSS** | v4 | Oxide engine (CSS-first, no PostCSS config), 5× faster than v3 |
| **shadcn/ui** | latest | You own the components (copy-paste, not installed), dark mode first, Radix primitives |
| **TanStack Router** | v1 | Fully type-safe params, loaders, per-route error boundaries |
| **TanStack Query** | v5 | REST data fetching + cache + background refresh |
| **Zustand** | v5 | Tiny global state for WS/live data. No Redux. |
| **Recharts** | latest | Dark-themeable charts for live metrics |
| **Lucide React** | latest | Icons (used by shadcn) |
| **Shiki** | latest | Syntax highlighting in CodeBlock + Chat output |

**Explicitly not using**: npm, Next.js, Remix, Webpack, Redux, class-variance-authority directly (only via shadcn)

---

## Shell Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  TopBar: [≡ CSS]  [breadcrumb]           [● WS] [● API] [⚙]    │
├──────────────┬──────────────────────────────────────────────────┤
│  Sidebar     │  <Outlet /> — active panel renders here          │
│              │                                                  │
│  ● Dashboard │                                                  │
│  ● Settings  │                                                  │
│  ● Marketplace                                                  │
│  ● Chat      │                                                  │
│  ─────────   │                                                  │
│  ● Projects  │                                                  │
│  ● Agents    │                                                  │
│  ● Events    │                                                  │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

- Sidebar items auto-generated from `MODULE_PANELS` registry
- TopBar: WS connection badge (green/amber/red), API health, breadcrumb
- `PanelContainer`: Suspense skeleton + retry-able ErrorBoundary per panel
- Collapsible sidebar (icon-only at narrow widths)
- Theme: near-black base (`--background: 0 0% 3.9%`), green accent (`--primary: 142 70% 45%`)

---

## Module Panel System

Adding a new panel is 3 steps:

1. Create `src/css/modules/<name>/templates/index.tsx` — export default component
2. Add entry to `MODULE_PANELS` in `module-registry.ts`
3. Done — sidebar nav item + route + lazy loading all auto-wired

```typescript
// src/frontend/src/module-registry.ts
export const MODULE_PANELS: ModulePanel[] = [
  { id: 'settings',     label: 'Settings',     path: '/settings',
    component: lazy(() => import('@css/core/settings/templates')) },
  { id: 'marketplace',  label: 'Marketplace',  path: '/marketplace',
    component: lazy(() => import('@css/core/marketplace/templates')) },
  { id: 'chat',         label: 'Chat',         path: '/chat',
    component: lazy(() => import('@css/modules/chat/templates')) },
  // Add here → auto appears in nav
]
```

`@css` alias in `vite.config.ts` → `../../css` (modules live next to Python code, no monorepo complexity)

---

## API Layer

### REST (`client.ts`)
```typescript
apiGet<T>(path)     // GET  /api/...
apiPost<T>(path, body)
apiPut<T>(path, body)
apiDelete(path)
// All throw ApiError({ status, message, detail }) on non-2xx
```
Dev server proxies `/api/*`, `/ws/*`, `/sse/*`, `/v1/*` to `http://localhost:8000` — no CORS in dev. Backend runs locally via `make serve`.

### WebSocket (`ws-manager.ts`)
```typescript
// Singleton. Auto-reconnects with exponential backoff.
wsManager.subscribe('agent.output', (msg: AgentOutputMsg) => void)
wsManager.subscribe('tool.call', (msg: ToolCallMsg) => void)
wsManager.subscribe('settings.changed', (msg: SettingsChangedMsg) => void)
// status: 'connected' | 'connecting' | 'disconnected' | 'error'
```

### SSE (`sse-client.ts`)
```typescript
// For streaming LLM output via HTTP SSE (/v1/chat streams)
async function* streamSSE<T>(url, body): AsyncGenerator<T>
// useSSE hook: consumes generator, updates React state token-by-token
```

---

## Live Data Flow

```
Backend events (WebSocket)
    │
    ▼
ws-manager.ts (typed subscribe)
    │
    ├──► SocketProvider (React Context) 
    │         └──► useWebSocket() hooks in panels
    │
    └──► Zustand store
              ├── wsStatus
              ├── activeAgents       ← from agent.run.* events
              ├── recentEvents       ← last 20 DomainEvents
              └── metricsSlice       ← 60-bucket rolling window per metric
                        └──► Recharts chart components
```

---

## Three Initial Live Panels

### Dashboard (`/`)
6 widgets, responsive 3-column grid (shadcn Card + Skeleton):
- **SystemHealth** — backend/DB/Redis/OTEL ping status
- **LiveMetrics** — Recharts area/line/bar charts (WS-fed)
- **ActiveAgents** — running agents with status badges (WS push)
- **RecentEvents** — last 20 domain events, auto-scroll, infinite scroll
- **SessionOverview** — active sessions + last 5 (REST)
- **ModelUsage** — top 5 models by call count + spend (REST)

### Settings (`/settings`)
- Category accordion, search bar across all keys
- Inline edit (click → input → Enter, optimistic TanStack Query mutation)
- Sensitive values masked (`••••••`) with click-to-reveal
- `requires_restart=true` settings → amber ⚠ badge
- Export to YAML button, Load template dropdown
- **Blocked by**: Phase 17 settings REST API

### Chat (`/chat`)
```
┌─────────────────────────────────────────────────────────────────┐
│  Chat               [Model: claude-opus-4 ▾] [Session: #abc12]  │
│  ─────────────────────────────────────────────────────────────  │
│  USER: Scan 192.168.1.0/24 for open ports                       │
│                                                                  │
│  ASSISTANT: Running nmap scan...                                │
│  ┌ Tool: nmap ────────────────────────────────────────────────┐  │
│  │ $ nmap -sS 192.168.1.0/24                                  │  │
│  │ Discovered open port 22/tcp on 192.168.1.5 [streaming ▌]  │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ─────────────────────────────────────────────────────────────  │
│  [📎] [/commands]  Type a message...              [↑] [Send]    │
└─────────────────────────────────────────────────────────────────┘
```
- SSE streaming: tokens appear one-by-one
- Tool call blocks: collapsible, shiki-highlighted input/output
- Model selector from `@llm_models` REST registry
- `/commands` slash autocomplete
- Markdown rendering via shiki

---

## vite.config.ts (critical)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@':    path.resolve(__dirname, 'src'),
      '@css': path.resolve(__dirname, '../../css'),   // colocated module panels
      '@ui':  path.resolve(__dirname, 'src/ui'),
    }
  },
  server: {
    port: 8000,
    host: true,  // Required for Docker
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/ws':  { target: 'ws://localhost:8000',  ws: true },
      '/sse': { target: 'http://localhost:8000', changeOrigin: true },
      '/v1':  { target: 'http://localhost:8000', changeOrigin: true },
    }
  }
})
```

---

## Tailwind v4 Dark Theme

```css
/* src/index.css — CSS-first, no config file needed */
@import "tailwindcss";

@layer base {
  :root {
    --background:   0 0% 3.9%;    /* near-black */
    --foreground:   0 0% 98%;
    --card:         0 0% 7%;
    --border:       0 0% 14.9%;
    --primary:      142 70% 45%;  /* green — cybersec aesthetic */
    --destructive:  0 62.8% 30.6%;
    --ring:         142 70% 45%;
  }
}
```

Initial shadcn components:
```bash
bunx shadcn add button input card badge separator skeleton toast tabs
bunx shadcn add dialog sheet dropdown-menu tooltip command
bunx shadcn add table scroll-area resizable collapsible
```

---

## Implementation Order

```
T18.1 vite-scaffold  →  T18.2 tailwind-shadcn  →  T18.3 appshell
                                                         │
T18.4a port-hooks ──────────────────────────────────────┤
T18.4 api/ws/store ─────────────────────────────────────┤
                                                         ▼
                                              T18.5 module-registry
                                                    │
                                    ┌───────────────┼───────────────────┐
                                    ▼               ▼                   ▼
                              T18.7 marketplace  T18.6 settings     T18.8 chat
                                                  (blocks: P17)      (WS-first MVP)
                                    │
                                    ▼
                              T18.10 dev-tooling
                                    │
                                    ▼
                              T18.11 dashboard
                                    │
                                    ▼
                              T18.12 live-graphs

T18.4 sse-client  ← later generic utility for `/sse/*` and `/v1/*` streams
```

**Minimum to get something in the browser**: T18.1 + T18.2 + T18.3

---

## Phase 18 Todo List

| ID | Task | Blocked by |
|----|------|-----------|
| `frontend-vite-scaffold` | Vite + React 19 + TS, vite.config aliases+proxy, tsconfig strict | — |
| `frontend-tailwind-shadcn` | Tailwind v4 + shadcn dark theme + initial shadcn components | vite-scaffold |
| `frontend-appshell` | AppShell, Sidebar, TopBar, PanelContainer | tailwind-shadcn |
| `frontend-api-client` | REST client + ApiError class | vite-scaffold |
| `frontend-ws-manager` | PORT useSocket.ts from ahs-admin-panel | vite-scaffold |
| `frontend-sse-client` | SSE AsyncGenerator + useSSE hook for later generic `/sse/*` and `/v1/*` streams | vite-scaffold |
| `frontend-zustand-store` | Zustand store (wsStatus, activeAgents, recentEvents, metricsSlice) | vite-scaffold |
| `frontend-port-hooks` | PORT 9 hooks + SocketProvider from ahs-admin-panel | vite-scaffold |
| `frontend-module-registry` | ModulePanel type + MODULE_PANELS + TanStack Router routes | appshell |
| `frontend-panel-colocated-structure` | Scaffold `templates/` stubs in settings/marketplace/chat | module-registry |
| `frontend-landing-dashboard` | Dashboard `/` — 6 widgets, responsive grid, Skeleton states | appshell + port-hooks + zustand-store + sessions-endpoints |
| `frontend-live-graphs` | Recharts + 4 chart components + metricsSlice + useDashboardMetrics | landing-dashboard + ws-manager |
| `frontend-settings-panel` | Settings panel (accordion, search, inline edit, masking, restart badge) | panel-colocated-structure + settings-hooks + **settings-rest-routes** |
| `frontend-settings-hooks` | TanStack Query hooks for /api/settings/* | api-client + settings-rest-routes |
| `frontend-marketplace-panel` | Marketplace panel (grid, search, install button) | panel-colocated-structure + marketplace-hooks |
| `frontend-marketplace-hooks` | TanStack Query hooks for marketplace API | api-client |
| `frontend-chat-panel` | Chat panel (WS-first MVP, tool blocks, markdown, model selector) | panel-colocated-structure + chat-hooks + port-hooks |
| `frontend-chat-hooks` | useChat hook (REST + WebSocket MVP, later SSE/proxy-ready) | api-client + ws-manager |
| `frontend-dev-tooling` | TanStack devtools overlays, package.json scripts, tsc check | tailwind-shadcn |

**`frontend-settings-panel` blocked by Phase 17 (`settings-rest-routes`).  
Chat MVP should target the current REST + WebSocket backend first; generic SSE/proxy transport comes later.  
All other todos: no upstream blockers — implement in order above.**

---

## Open Decision

`src/frontend/` is the confirmed shell location (Option A).  
`src/css/core/templates/` contains only orphaned `node_modules` — tracked as `core-templates-cleanup` (Phase 19) to delete them.  
Docker/Nginx static serving: deferred post-MVP. Use `bun run dev` during development.
