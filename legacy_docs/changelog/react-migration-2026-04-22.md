# Changelog: React + TypeScript SPA Migration (2026-04-22)

## Summary

Replaced the Jinja2 + vanilla TypeScript dashboard frontend with a full React 19 + TypeScript SPA. The Python/Starlette backend — all `/api/*`, `/sse/*`, A2A, and MCP — remains **100% unchanged**. The new frontend lives in `src/frontend/` and builds into `src/dashboard/static/react/`.

---

## Why

The previous architecture generated HTML on every request from ~15,000 lines of Python template code (`_base.py`, `_components.py`, `_tabs.py`, `jinja_env.py`, `panel_helpers.py`, `panels/*.py`), wired to 20+ TypeScript modules (`refresh.ts` 701 lines, `chat.ts`, `core.ts`, etc.) that wrote DOM directly. This made the codebase:

- Hard to extend (new features required changes in both Python and TypeScript)
- Difficult to type-check end-to-end
- Slow to iterate on (no HMR)
- Prone to silent breakage at the Python/JS boundary

---

## What Changed

### New: `src/frontend/` — React SPA

```
src/frontend/
├── src/
│   ├── App.tsx               — root component, lazy panel router, QueryClientProvider
│   ├── main.tsx              — React DOM entry point
│   ├── index.css             — CSS tokens + Tailwind 4 base
│   ├── constants/nav.ts      — NAV_ITEMS + NAV_GROUPS (ported from _tabs.py)
│   ├── store/uiStore.ts      — Zustand: activeTab, theme, sidebarCollapsed (persisted)
│   ├── lib/queryClient.ts    — TanStack Query v5 client (staleTime 30s)
│   ├── lib/cn.ts             — clsx + tailwind-merge helper
│   ├── hooks/useApi.ts       — fetchApi() + useApiQuery()
│   ├── hooks/useSSE.ts       — EventSource hook
│   ├── components/
│   │   ├── layout/           — Sidebar, Topbar, StatusBar
│   │   ├── ui/               — Badge, Button, Card, Input, Modal, Select,
│   │   │                       Spinner, Table, Toast
│   │   └── shared/           — ErrorBoundary
│   └── features/
│       ├── platform/         — Health, Usage, Telemetry, Providers
│       ├── proxy/            — Routing, QoL Controls
│       ├── agents/           — Chat, AgentFactory, AgentCrafter, TeamBuilder,
│       │                       AgentQuery, Workflows, Flowgraph, Prompts,
│       │                       SdkLab, Marketplace, MarketplaceFactory
│       ├── operations/       — Cases, Tasks, PoCs, A2A
│       ├── forensics/        — Investigations, Findings, IOCs, YARA,
│       │                       Intel, Audit, Compliance
│       ├── data/             — OpenSearch, Explorer, Templates
│       └── settings/         — Settings (Claude SDK), Settings (CyberSecSuite)
├── package.json              — React 19, Vite 8, TS 6, TanStack Query v5, etc.
├── vite.config.ts            — builds to ../dashboard/static/react/, base /static/react/
└── tsconfig.json
```

**33 panels** (one per sidebar tab), **13 UI components**, **3 layout components**, **2 hooks**, **1 Zustand store** — **56 files total**.

### Changed: `src/dashboard/api/page.py`

Now serves the React `index.html` when available; falls back to legacy Jinja HTML if the React build is absent:

```python
async def dashboard_page(request: Request) -> FileResponse | HTMLResponse:
    if _REACT_INDEX.exists():
        return FileResponse(str(_REACT_INDEX))
    from dashboard._html import _DASHBOARD_HTML
    return HTMLResponse(_DASHBOARD_HTML)
```

### Unchanged

- All Python backend code (`routes.py`, all 80+ API handlers, SSE endpoints)
- Legacy Jinja templates (still present in `src/dashboard/templates/` as fallback)
- MCP tools, A2A protocol, AI proxy, database, agents — nothing outside `src/frontend/` and `page.py` was touched

---

## Stack Versions

| Package | Version |
|---------|---------|
| React | 19.2.5 |
| Vite | 8.0.9 |
| TypeScript | 6.0.2 |
| Tailwind CSS | 4.2.4 (`@tailwindcss/vite`) |
| TanStack Query | 5.99.2 |
| TanStack Table | 8.21.3 |
| Zustand | 5.0.12 |
| Radix UI | ^1–2 (dialog, select, tabs, tooltip, dropdown, switch, separator, scroll-area) |
| Recharts | 3.8.1 |
| React Hook Form | 7.73.1 |
| Zod | 4.3.6 |
| lucide-react | 1.8.0 |
| react-router-dom | 7.14.2 |

---

## Build Output

```
src/dashboard/static/react/
├── index.html
├── favicon.svg
└── assets/
    ├── index-*.js          211 kB (66 kB gzip)  — shared vendor chunk
    ├── index-*.css         ~8 kB gzip            — Tailwind + CSS tokens
    ├── ChatPanel-*.js       4.3 kB gzip           — code-split per panel
    ├── SettingsPanel-*.js   6.1 kB
    └── ...                 (one chunk per panel, lazy-loaded)
```

All asset URLs are prefixed with `/static/react/` (`base: '/static/react/'` in vite.config.ts) so Starlette's existing `Mount("/static", StaticFiles(...))` serves them without any route changes.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| CSS custom properties over Tailwind dark mode | All existing tokens (`var(--accent)`, `var(--surface)`, etc.) carry over directly; themes (blue/purple/red) still driven by `body.theme-*` classes |
| TanStack Query for all data | Replaces manual `fetch` + polling in `refresh.ts`; automatic dedup, stale-while-revalidate, per-tab refetchInterval |
| Zustand for UI state | Lightweight; persists `activeTab`, `theme`, `sidebarCollapsed` to localStorage — survives page reload |
| `React.lazy()` + `Suspense` for every panel | Keeps initial bundle small; each tab loads its code on first visit |
| No React Router URL routing | State is in Zustand store, not URL — matches the SPA-in-a-tab UX of the original dashboard |
| Fallback to legacy HTML | `page.py` checks for `static/react/index.html` at startup — dev environments without a build continue to work |

---

## Migration Notes

The legacy Jinja templates are **not deleted**. They remain in `src/dashboard/templates/` and can be removed in a follow-up cleanup pass once the React SPA is validated in production.

To trigger the fallback manually (restore legacy UI), delete or rename `src/dashboard/static/react/`:
```bash
mv src/dashboard/static/react src/dashboard/static/react.bak
```

---

## References

- Plan: [`plans/plan-react-migration.md`](../../plans/plan-react-migration.md)
- Frontend source: [`src/frontend/`](../../src/frontend/)
- Built output: [`src/dashboard/static/react/`](../../src/dashboard/static/react/)
- Development guide: [`docs/development/frontend.md`](../development/frontend.md)
