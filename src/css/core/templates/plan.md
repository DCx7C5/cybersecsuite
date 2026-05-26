# core/templates — Frontend Ownership Surface

**Status**: 🟡 Active migration target | **Phase**: 18 (Frontend Foundation)

## Purpose

`src/css/core/templates/` is the canonical home for core frontend implementation surfaces.

- `src/frontend/` remains the runtime shell/bootstrap (router boot, bundler, providers).
- Feature/panel implementation should live under `core/templates/*` paths.
- Current high-priority target: marketplace/chat/dashboard/settings surfaces under template ownership.

## Active Directives

- Move frontend implementation ownership to template-localized files:
  - `core/templates/marketplace/*`
  - `core/templates/chat/*`
  - `core/templates/dashboard/*`
  - `core/templates/settings/*`
- Keep colocated module contracts intact while consolidating UI logic.
- Preserve import-order and runtime wiring discipline from `core/settings/config.py` module order rules.

## session.db Mapping

- `frontend-core-templates-home-cutover`
- `frontend-marketplace-installed-catalog-layout`
- `frontend-chat-thinking-task-visuals`
- `frontend-dashboard-tiles-workspace`

## Dependencies

- `src/frontend/` runtime shell
- `src/css/core/settings/`
- `src/css/core/menu/`
- `src/css/core/marketplace/`
- `src/css/modules/chat/`

## Phase 18 Execution Contract

`src/frontend/` owns only bootstrapping, application shell, routing, shared UI
utilities, transport clients, and chart processing. Domain panels live with
their owning CSS area under a `templates/` directory and are registered
explicitly in the shell; do not discover them through filesystem scanning.

| Surface | Required ownership and behavior |
|---------|---------------------------------|
| Shell | React 19 + strict TypeScript + Vite; AppShell, sidebar/topbar, error/loading wrappers, static panel registry. |
| Data clients | Typed REST client first; WebSocket manager for live state; SSE/proxy streaming may be added without rewriting panel state contracts. |
| Styling | Tailwind/shadcn dark shell with locally maintained components; use Bun tooling. |
| Navigation | Runtime-composed navigation aligned to `core/menu`; marketplace sub-navigation is sourced from sidebar children, not local duplicate tabs. |
| Settings | `core/settings/templates/` consumes settings REST routes with masking, reset/update, template/profile loading, and restart indicators. |
| Marketplace | `core/marketplace/templates/` owns browse/install/catalog views and menu-child navigation. |
| Chat | `modules/chat/templates/` owns REST/WebSocket-first streaming conversation UI, model/session controls, and tool output blocks. |
| MCP | MCP server status/start/stop/restart panel waits for lifecycle endpoints from `modules/mcps`. |
| Graphs | Integrate XYFlow for workflow/topology graph views through graph owner contracts. |

## Dashboard and Live Metrics

The landing dashboard should expose health, active agents, recent events,
session overview, model usage, and live metrics using real backend/stream data.

| Component | Implementation requirement |
|-----------|----------------------------|
| Charts | Apache ECharts charts for token usage, latency percentiles, agent activity, and event-rate sparkline. Do not substitute Recharts without an explicit design change. |
| Processing | A Web Worker batches/downsamples rolling time-series data before React state updates; Comlink is permitted for the worker boundary. |
| Live transport | WebSocket event feeds update Zustand-managed live state; REST/TanStack Query supplies initial or non-streaming widgets. |
| Empty/loading behavior | Render skeleton/empty states until genuine data arrives; no embedded mock telemetry in runtime panels. |

## Implementation Order

| Stage | Deliverable | Gate |
|-------|-------------|------|
| 1 | Vite/React/TS scaffold, styling, shell, REST client, WebSocket state. | Immediate foundational work. |
| 2 | Static panel registry and colocated panel stubs. | Shell ready. |
| 3 | Menu/navigation and marketplace behavior. | Menu and marketplace API contracts. |
| 4 | Settings, MCP, and chat panels. | Their backend endpoints/transports respectively. |
| 5 | XYFlow integration and landing dashboard. | Workflow/session/event surfaces. |
| 6 | ECharts worker-backed metrics. | Dashboard and live event transport. |

## Validation Boundary

Architecture/diagram documents are deliberately not being edited during the
documentation movement pass. Before Phase 18 implementation work relies on
old diagrams, compare them against the local contracts and current source,
especially chart-library and template-location claims.
