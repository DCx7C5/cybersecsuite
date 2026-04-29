# Frontend Development Guide

CyberSecSuite uses a React 19 + TypeScript SPA (`src/frontend/`) that talks to the Starlette backend over its existing REST/SSE API. This document covers everything needed to develop, build, and extend the frontend.

---

## Quick Start

```bash
# 1. Start the backend (required for API calls)
make run
# or: uv run python -m manage run

# 2. Start the React dev server (separate terminal)
cd src/frontend
npm run dev
# → http://localhost:5173  (proxies /api + /sse → localhost:8000)
```

HMR is enabled. Changes to `.tsx`/`.ts`/`.css` reload instantly.

---

## Project Layout

```
src/frontend/
├── index.html                 — HTML entry (title: CyberSecSuite)
├── vite.config.ts             — Vite + Tailwind plugin, proxy, build output
├── tsconfig.json / tsconfig.app.json
├── package.json
└── src/
    ├── main.tsx               — createRoot entry
    ├── App.tsx                — QueryClientProvider + layout shell + lazy panel router
    ├── index.css              — CSS tokens (var(--accent) etc.) + Tailwind 4 base
    │
    ├── constants/
    │   └── nav.ts             — NAV_ITEMS[] + NAV_GROUPS — single source of truth for sidebar
    │
    ├── store/
    │   └── uiStore.ts         — Zustand: activeTab, theme, sidebarCollapsed (localStorage)
    │
    ├── lib/
    │   ├── queryClient.ts     — TanStack QueryClient (staleTime: 30s, retry: 1)
    │   └── cn.ts              — clsx + tailwind-merge
    │
    ├── hooks/
    │   ├── useApi.ts          — fetchApi<T>(), useApiQuery<T>()
    │   └── useSSE.ts          — EventSource lifecycle hook
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.tsx    — collapsible grouped nav, settings dropdown
    │   │   ├── Topbar.tsx     — sidebar toggle, breadcrumb, theme switcher
    │   │   └── StatusBar.tsx
    │   ├── ui/
    │   │   ├── Badge.tsx      — variants: ok / err / warn / info
    │   │   ├── Button.tsx     — variants: primary / ghost / danger
    │   │   ├── Card.tsx       — title + children + optional actions
    │   │   ├── Input.tsx
    │   │   ├── Modal.tsx      — Radix Dialog, dark-themed
    │   │   ├── Select.tsx     — Radix Select
    │   │   ├── Spinner.tsx
    │   │   ├── Table.tsx      — TanStack Table, sortable, dark-themed
    │   │   └── Toast.tsx
    │   └── shared/
    │       └── ErrorBoundary.tsx
    │
    └── features/
        ├── platform/          — Health, Usage, Telemetry, ProvidersHub
        ├── proxy/             — Routing, QoLControls
        ├── agents/            — Chat, AgentFactory, AgentCrafter, TeamBuilder,
        │                        AgentQuery, Workflows, Flowgraph, Prompts,
        │                        SdkLab, Marketplace, MarketplaceFactory
        ├── operations/        — Cases, Tasks, PoCs, A2A
        ├── forensics/         — Investigations, Findings, IOCs, YARA,
        │                        Intel, Audit, Compliance
        ├── data/              — OpenSearch, Explorer, Templates
        └── settings/          — SettingsPanel, SettingsCybersecSuitePanel
```

---

## Configuration

### `vite.config.ts`

```typescript
{
  base: '/static/react/',          // asset URLs in production
  build: {
    outDir: '../dashboard/static/react',  // Starlette serves from here
    assetsDir: 'assets',
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/sse': 'http://localhost:8000',
      '/ts':  'http://localhost:8000',
    },
  },
}
```

### `tsconfig.app.json` path alias

```json
"paths": { "@/*": ["./src/*"] }
```

Use `@/` for all internal imports (e.g. `import Card from '@/components/ui/Card'`).

---

## How Panels Work

Each panel is a React component in `src/features/<group>/<Name>Panel.tsx`. It is registered in `App.tsx` as a `React.lazy()` import — it loads on first navigation to that tab.

### Minimal panel template

```typescript
import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'

interface MyData { items: { id: number; name: string }[] }

export default function MyPanel() {
  const { data, isLoading, error } = useApiQuery<MyData>(['my-key'], '/api/my-endpoint')
  if (isLoading) return <div style={{display:'flex',justifyContent:'center',padding:'40px'}}><Spinner /></div>
  if (error)     return <div style={{color:'var(--red)',padding:'16px'}}>{String(error)}</div>
  return (
    <Card title="My Panel">
      {(data?.items ?? []).map(i => <div key={i.id}>{i.name}</div>)}
    </Card>
  )
}
```

### Adding a new tab

1. Create `src/features/<group>/MyNewPanel.tsx`
2. Add a lazy import in `App.tsx`:
   ```typescript
   'my-tab': React.lazy(() => import('./features/<group>/MyNewPanel')),
   ```
3. Add a nav entry in `src/constants/nav.ts`:
   ```typescript
   { id: 'my-tab', label: 'My Tab', icon: '⊕', group: '<group>' },
   ```
4. Done — the sidebar and routing update automatically.

---

## Data Fetching

### `useApiQuery` — read data

```typescript
import { useApiQuery } from '@/hooks/useApi'

const { data, isLoading, error, refetch } = useApiQuery<MyType>(
  ['cache-key'],          // TanStack Query key
  '/api/endpoint',
  { refetchInterval: 5000 }  // optional: poll every 5s
)
```

### `fetchApi` — mutations / one-shot

```typescript
import { fetchApi } from '@/hooks/useApi'

// POST
await fetchApi('/api/cases', {
  method: 'POST',
  body: JSON.stringify({ title: 'New case', severity: 'high' }),
})

// PATCH
await fetchApi(`/api/cases/${id}`, {
  method: 'PATCH',
  body: JSON.stringify({ status: 'resolved' }),
})

// DELETE
await fetchApi(`/api/cases/${id}`, { method: 'DELETE' })
```

After a mutation, invalidate the query to refresh the table:

```typescript
import { useQueryClient } from '@tanstack/react-query'
const qc = useQueryClient()
await fetchApi(...)
qc.invalidateQueries({ queryKey: ['cases'] })
```

### `useSSE` — real-time events

```typescript
import { useSSE } from '@/hooks/useSSE'

useSSE('/sse/cases', (event) => {
  const payload = JSON.parse(event.data)
  // handle update
})
```

The hook closes the EventSource on component unmount automatically.

---

## Chat Panel (SSE Streaming)

The Chat panel (`features/agents/ChatPanel.tsx`) demonstrates the full streaming pattern:

1. `POST /api/agent-query` → `{ task_id: string }`
2. Open `EventSource("/sse/agent-run/{task_id}")`
3. Listen for named events:
   - `token` — `e.data` is a text chunk, append to current assistant message
   - `done`  — `e.data` is JSON `{ elapsed_ms, stop_reason }`, close EventSource
   - `error` — `e.data` is JSON `{ error }`, show error, close EventSource

---

## State Management

All UI state lives in `src/store/uiStore.ts` (Zustand, persisted to `localStorage`):

```typescript
import { useUIStore } from '@/store/uiStore'

const { activeTab, setActiveTab, theme, setTheme, sidebarCollapsed, toggleSidebar } = useUIStore()
```

Server state is in TanStack Query cache — do not duplicate it in Zustand.

---

## Theming

Three color modes driven by `body.theme-*` class:

| Mode | CSS class | `--accent` |
|------|-----------|-----------|
| Blue (default) | `body.theme-blue` | `#3574f0` |
| Purple | `body.theme-purple` | `#a855f7` |
| Red | `body.theme-red` | `#ef4444` |

Use CSS custom properties for all theme-sensitive styles:

```typescript
// ✅ correct
style={{ color: 'var(--accent)', background: 'var(--surface)' }}

// ❌ avoid — won't respond to theme changes
style={{ color: '#3574f0' }}
```

Full token reference: [`src/frontend/src/index.css`](../../src/frontend/src/index.css)

---

## UI Components

### Badge
```tsx
<Badge variant="ok">healthy</Badge>
<Badge variant="err">failed</Badge>
<Badge variant="warn">degraded</Badge>
<Badge variant="info">running</Badge>
```

### Card
```tsx
<Card title="My Section" actions={<Button onClick={refresh}>Refresh</Button>}>
  content
</Card>
```

### Button
```tsx
<Button variant="primary" onClick={save}>Save</Button>
<Button variant="ghost"   onClick={cancel}>Cancel</Button>
<Button variant="danger"  onClick={del}>Delete</Button>
<Button disabled={loading}>Submit</Button>
```

### Table
```tsx
import Table from '@/components/ui/Table'

<Table
  columns={[
    { accessorKey: 'name',    header: 'Name' },
    { accessorKey: 'status',  header: 'Status' },
    { accessorKey: 'created', header: 'Created' },
  ]}
  data={rows}
/>
```

Sortable by default. Columns use `accessorKey` (TanStack Table v8).

### Modal (CRUD pattern)
```tsx
import Modal from '@/components/ui/Modal'

const [open, setOpen] = useState(false)

<Button variant="primary" onClick={() => setOpen(true)}>New</Button>
<Modal open={open} onClose={() => setOpen(false)} title="Create Item">
  <form onSubmit={handleSubmit}>
    ...
    <Button type="submit">Create</Button>
  </form>
</Modal>
```

---

## Building for Production

```bash
cd src/frontend
npm run build
```

Output goes to `src/dashboard/static/react/`. The Starlette static mount at `/static` serves it automatically. The Python `dashboard_page()` handler serves `index.html` at `/`.

To rebuild after frontend changes:
```bash
make build-frontend   # if added to Makefile
# or:
cd src/frontend && npm run build
```

---

## Development Without the Backend

If you only need to work on UI components without the backend running, mock the API in `vite.config.ts` with a mock plugin, or use `msw` (Mock Service Worker). The current setup will show loading states or errors for API-dependent panels.

---

## Linting

```bash
cd src/frontend
npm run lint
```

Uses `eslint-plugin-react-hooks` and `eslint-plugin-react-refresh`. TypeScript strict mode is enabled.

---

## Bundle Analysis

To inspect chunk sizes:

```bash
cd src/frontend
npx vite-bundle-visualizer
```

Current stats (2026-04-22):
- Main chunk: **211 kB** (66 kB gzip)
- CSS: ~30 kB (8 kB gzip)
- Per-panel chunks: 1–6 kB each (lazy-loaded)
- Total initial: **< 80 kB gzip**

---

---

## React Router v7 Architecture

CyberSecSuite frontend uses **React Router v7** for URL-driven navigation, enabling browser back/forward buttons, deep linking, and shareable URLs.

### URL Schemes

Navigation uses query parameter routing:

```
/app?tab=<panelId>                     — Navigate to panel
/app?tab=<panelId>&context=<value>     — Deep link with state
/app?tab=iocs&case=42                  — IOCs panel with Case #42 selected
/app?tab=opensearch&query=APT-28       — OpenSearch with query pre-filled
```

### Migration from activeTab

**Old pattern (Zustand state):**
```typescript
const { setActiveTab } = useUIStore()
<button onClick={() => setActiveTab('cases')}>Cases</button>
```

**New pattern (React Router):**
```typescript
import { useNavigate } from 'react-router-dom'
const navigate = useNavigate()
<button onClick={() => navigate('?tab=cases')}>Cases</button>
```

Or using `<Link>` component:
```typescript
import { Link } from 'react-router-dom'
<Link to="?tab=cases">Cases</Link>
```

### Extracting Current Tab

From URL parameters:
```typescript
import { useLocation } from 'react-router-dom'

export default function App() {
  const location = useLocation()
  const tab = new URLSearchParams(location.search).get('tab') || 'chat'
  // Use 'tab' to render the appropriate panel
}
```

### Lazy Loading & Code Splitting

All 33 panel components use `React.lazy()` for automatic code splitting:

```typescript
const ChatPanel = React.lazy(() => import('./features/agents/ChatPanel'))
const CasesPanel = React.lazy(() => import('./features/operations/CasesPanel'))
// ... one lazy import per panel
```

Each panel loads on-demand (~2–6 kB per chunk after gzip). Use Suspense to show a loading spinner:

```typescript
<Suspense fallback={<Spinner />}>
  {tab === 'chat' && <ChatPanel />}
  {tab === 'cases' && <CasesPanel />}
</Suspense>
```

### Browser Back/Forward Support

React Router automatically integrates with browser history:

1. Click panel → URL updates → back button works
2. Back button → URL reverts → panel switches
3. Forward button → URL re-applies → panel re-renders

No explicit history handling needed.

### Deep Linking & State Restoration

Use URL search params to persist context:

```typescript
// User navigates to IOCs panel with case=42 selected
navigate('?tab=iocs&case=42')

// On page reload or shared link, extract context:
const case_id = new URLSearchParams(location.search).get('case')
if (case_id) {
  // Load case 42 automatically
}
```

### Breadcrumb Integration

The Topbar breadcrumb reads from URL:

```typescript
import { useLocation } from 'react-router-dom'

export default function Topbar() {
  const location = useLocation()
  const tab = new URLSearchParams(location.search).get('tab') || 'chat'
  const breadcrumbs = { chat: ['Home', 'Chat'], cases: ['Home', 'Operations', 'Cases'] }
  return <Breadcrumb items={breadcrumbs[tab]} />
}
```

### TypeScript Contracts

Define router types for type safety:

```typescript
export interface RouteParams {
  tab: string
  case?: string
  query?: string
  entity?: string
}

export const parseRouteParams = (search: string): RouteParams => {
  const sp = new URLSearchParams(search)
  return {
    tab: sp.get('tab') || 'chat',
    case: sp.get('case'),
    query: sp.get('query'),
    entity: sp.get('entity'),
  }
}
```

### Performance & Best Practices

1. **Memoize components** that render conditionally based on URL:
   ```typescript
   const ChatPanelMemo = React.memo(ChatPanel)
   const CasesPanelMemo = React.memo(CasesPanel)
   ```

2. **Avoid re-parsing URL** in multiple places:
   ```typescript
   // Create a custom hook instead:
   export const useRouteParams = () => {
     const location = useLocation()
     return parseRouteParams(location.search)
   }
   ```

3. **Test route changes** with Playwright (see `/tests/e2e/`).

---

## See Also

- [`changelog/react-migration-2026-04-22.md`](../changelog/react-migration-2026-04-22.md) — full migration changelog
- [`architecture/overview.md`](../architecture/overview.md) — system architecture
- [`api/dashboard.md`](../api/dashboard.md) — all `/api/*` and `/sse/*` endpoints
