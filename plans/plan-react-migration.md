# CyberSecSuite Dashboard: React + TypeScript Migration Plan

**Version:** 2026-04-22  
**Status:** Ready for execution  
**Goal:** Replace bloated Jinja2 + vanilla TypeScript frontend with a clean, modern React 19 + TypeScript SPA while keeping the entire Python/Starlette backend (all `/api/*`, `/sse/*`, A2A, etc.) 100% unchanged.

**Current Pain:** ~15,000+ lines of mixed Jinja macros (`_components.py`, `base.html`, `forensics.py`, `operations.py`, `agents.py`, `advanced.py`, `platform.py`, `data.py`, `settings.py`, `marketplace.py`, `agent_factory.py`, `_base.py`, `_tabs.py`, `jinja_env.py`, `panel_helpers.py`) + 20+ TypeScript modules (`refresh.ts` 29kB, `chat.ts`, `core.ts`, `index.ts`, `crud_ops.ts`, etc.) generating dynamic HTML on every request. This is unsustainable.

**Target Stack (Recommended):**
- **Build:** Vite 6 + React 19 + TypeScript 5.8+
- **Styling:** Tailwind CSS 4 + shadcn/ui (or Radix UI primitives)
- **Data:** TanStack Query v5 (replaces manual fetch + refresh.ts polling)
- **State:** Zustand or Jotai (lightweight, replaces scattered window globals)
- **Charts:** Recharts (or keep ECharts/Chart.js via npm if needed)
- **Routing:** React Router v7 (or TanStack Router)
- **Real-time:** Native EventSource + TanStack Query for SSE
- **Icons:** Lucide-react or Heroicons
- **Forms:** React Hook Form + Zod (for validation, replaces Jinja forms)

---

## 1. High-Level Architecture After Migration

```
src/
├── dashboard/                  # Python backend (UNCHANGED)
│   ├── routes.py               # All 80+ API routes stay exactly as-is
│   ├── asgi.py                 # Starlette app
│   ├── api/                    # All handlers (crud_ops, charts, sse, etc.)
│   └── templates/              # Jinja removed for frontend (keep only if needed for emails)
│
├── frontend/                   # NEW React SPA (this is what we build)
│   ├── src/
│   │   ├── components/         # Reusable UI (Card, Table, Modal, Badge, etc.)
│   │   ├── features/           # Domain panels (Health, Agents, Forensics, Chat, etc.)
│   │   ├── hooks/              # useApi, useSSE, useSettings, etc.
│   │   ├── lib/                # api client (TanStack Query), utils
│   │   ├── pages/              # Tab views
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css           # Tailwind + custom tokens (port from dashboard.css)
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
└── static/                     # Built React assets served by Starlette
    └── js/                     # (Vite output → /static/js/)
```

**Backend Change:** Zero.  
**Frontend Change:** 100% (Jinja deleted, React takes over `/`).

---

## 2. File-by-File Mapping (Current → React Equivalent)

### Core Layout & Navigation
| Current File                  | Lines | React Replacement                          | Notes |
|-------------------------------|-------|--------------------------------------------|-------|
| `_tabs.py` + `topbar_nav_menu()` | ~200  | `src/components/Sidebar.tsx` + `Topbar.tsx` | Use shadcn `Sidebar` + collapsible + theme toggle |
| `base.html` + `_base.py`      | ~15k  | `src/App.tsx` + layout components          | Port tokens from `dashboard.css` + `themes.css` |
| `jinja_env.py`                | 1.8k  | N/A (deleted)                              | No more Python template rendering |
| `panel_helpers.py`            | 3.7k  | `src/components/` (stat cards, heatmaps)   | Convert to React components |

### Major Panels (Each becomes a Feature)
| Current                          | React Feature Path                     | Complexity | Priority |
|----------------------------------|----------------------------------------|------------|----------|
| `platform.py` (_providers, _health, _usage, _telemetry) | `features/platform/` | Medium | High |
| `forensics.py` (_findings, _iocs, _investigations, _yara, _intel, _audit, _compliance) | `features/forensics/` | High | High |
| `operations.py` (_cases, _tasks, _pocs, _a2a) | `features/operations/` | Medium | High |
| `agents.py` + `advanced.py` (_chat, _team-builder, _agent-crafter, _agent-factory, _workflows, _flowgraph, _sdk-lab) | `features/agents/` + `features/advanced/` | Very High | Medium |
| `marketplace.py` + `agent_factory.py` | `features/marketplace/` | Medium | Medium |
| `settings.py` + `settings.ts`   | `features/settings/` | Medium | High |
| `data.py` (_opensearch, _explorer) | `features/data/` | Low | Low |
| `chat.ts` (full streaming + tools + memory) | `features/chat/` (reuse most logic) | High | High |

### TypeScript Modules (Highly Reusable)
- `refresh.ts` (29k lines) → Split into `hooks/useDashboardData.ts` + TanStack Query
- `chat.ts` → `features/chat/ChatPanel.tsx` (keep SSE token streaming logic)
- `core.ts`, `table.ts`, `routing.ts`, `crud_ops.ts`, `qol.ts`, `vault.ts`, `flowgraph.ts`, `sdk_panel.ts`, `providers_hub.ts`, `team.ts`, `craft.ts`, `factory.ts`, `workflows.ts`, `explorer.ts`, `opensearch.ts` → Direct port or adaptation (most business logic stays)
- `index.ts` → `main.tsx` + route definitions

### Styles
- `dashboard.css` (32k) + `themes.css` → `src/index.css` (Tailwind + CSS vars for modes: blue/purple/red)
- Keep exact color tokens (`--accent`, `--mode-blue`, etc.)

---

## 3. Migration Phases (Incremental — Zero Downtime)

### Phase 0: Setup (1-2 days)
1. Create `src/frontend/` with Vite + React template
2. Install: `tailwindcss`, `shadcn/ui`, `@tanstack/react-query`, `react-router-dom`, `lucide-react`, `zod`, `react-hook-form`
3. Port CSS tokens + create `ThemeProvider` (blue/purple/red modes)
4. Add proxy in `vite.config.ts` → `http://localhost:8000` for `/api` and `/sse`
5. Build once and serve from Starlette `/static` (update `asgi.py` if needed)

### Phase 1: Core Shell (2-3 days)
- Sidebar + Topbar + Tab routing (use React Router)
- Context bar + status bar
- Global toast system (port from `_base.py`)
- Theme switcher (already in `themes.css`)

### Phase 2: High-Impact Tabs (1 week)
Priority order:
1. **Health** (simple cards + latency chart)
2. **Providers Hub** (table + toggle + modal)
3. **Usage** (charts + table)
4. **Chat** (reuse 90% of `chat.ts` logic — this is the killer feature)
5. **Findings / IOCs** (tables + heatmaps — use Recharts or keep ECharts)

### Phase 3: Complex Features (1-2 weeks)
- Agent Factory / Crafter / Team Builder (heavy form + preview logic)
- Flowgraph (Drawflow → React Flow or keep canvas lib)
- SDK Lab (5 sub-tabs with streaming/structured/thinking/memory)
- Workflows + Marketplace
- Settings toggles + hooks

### Phase 4: Cleanup (2-3 days)
- Delete all `templates/panels/*.py`, `_components.py`, `jinja_env.py`, `_base.py`, `_tabs.py`
- Remove Jinja2 from `pyproject.toml` / requirements
- Update `routes.py` — serve React `index.html` at `/` instead of `dashboard_page()`
- Update `index.ts` → delete old wiring, keep only if any shared utils

### Phase 5: Polish & Testing
- Full E2E with Playwright (already have `playwright.py`)
- Performance: React devtools, bundle size < 500kB gzipped
- Accessibility (already good aria labels in Jinja)

---

## 4. Key Technical Decisions

- **Charts:** Start with Recharts (simpler API). If ECharts features are critical, install `echarts-for-react`.
- **Tables:** Use TanStack Table v8 (excellent sorting, filtering, pagination — replaces `renderTable` in `table.ts`).
- **SSE:** Keep native `EventSource` + TanStack Query `useQuery` with refetch on events.
- **Modals:** shadcn `Dialog` component (port all current modals: findings, iocs, cases, etc.).
- **Forms:** React Hook Form + Zod schemas (port from `form_field`, `form_input` etc.).
- **State Management:** Minimal — TanStack Query for server state + Zustand for UI state (sidebar collapsed, active tab, theme).
- **Build Output:** Vite builds to `src/dashboard/static/js/` (same as current TS output) so no change to `asgi.py` static mount.

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Flowgraph Drawflow canvas | Use `@xyflow/react` (modern replacement) |
| Heavy agent generation forms | Keep Python backend for generation, React only for UI |
| 80+ API endpoints | Use OpenAPI spec (if exists) or generate types with `openapi-typescript` |
| Time to port 40+ panels | Start with 5 most used tabs; use feature flags or keep old Jinja behind `/old` route temporarily |
| Bundle size | Code-split per tab with React.lazy + Suspense |

---

## 6. Immediate Next Steps (You Can Run Today)

1. **Create the frontend skeleton**
   ```bash
   cd src
   npm create vite@latest frontend -- --template react-ts
   cd frontend
   npm install tailwindcss @tailwindcss/vite lucide-react @tanstack/react-query react-router-dom
   npx shadcn@latest init
   ```

2. **Port CSS tokens** (copy from `dashboard.css` root vars)

3. **Replace `dashboard_page()` in `routes.py`** with:
   ```python
   from starlette.responses import FileResponse
   async def dashboard_page(request):
       return FileResponse("src/dashboard/static/index.html")
   ```

4. **Reply with "Start Phase 0"** and I will generate the full `App.tsx`, `Sidebar.tsx`, first 3 tab components, and updated `routes.py` + `asgi.py` changes.

---

**✅ Plan created next to the existing Pydantic plan**

**Location:** `/home/workdir/plan-react-migration.md`

You can access it directly in your homedir.  
To view: `cat /home/workdir/plan-react-migration.md`

**Ready when you are.** Just say the word and we begin the migration. This will make the dashboard feel modern, fast, and maintainable again. 🚀

---

**Bonus:** After migration you can delete ~40,000 lines of Jinja/Python template code and gain full type safety + hot module replacement in development.