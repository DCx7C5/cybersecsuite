# Feature Plan: Flowgraph — Drag-and-Drop Pipeline Editor

> Adds an interactive node-graph canvas to the dashboard for visual composition
> of agent pipelines, workflow steps, and MCP tool chains.

---

## 1. Goal

Replace the text-list Workflow Builder (`_workflows()`) with a drag-and-drop
node canvas where users can:

- Drag **agent nodes** from a sidebar palette onto a canvas
- Connect nodes via edges (dependency arrows)
- Configure each node inline (agent name, prompt template, inputs/outputs)
- Execute the resulting pipeline and stream results back per-node

---

## 2. Library choice: Drawflow

**Drawflow** (MIT, ~12 KB min+gz, zero framework deps, CDN-available)
https://github.com/jerosoler/Drawflow

Chosen because:
- Pure vanilla JS + CSS — no React/Vue/Svelte needed
- CDN-installable (`<script>` + `<link>` in the SPA `<head>`)
- Full node CRUD API (`addNode`, `removeNode`, `addConnection`, `export`, `import`)
- Export/import to plain JSON — trivially round-trips to the backend
- Actively maintained, used in production at scale (ComfyUI-adjacent ecosystem)

Alternative considered: **JointJS** (MIT community) — larger, richer, but adds ~500 KB and requires Backbone.

---

## 3. Integration points

| Layer | Change |
|---|---|
| `src/dashboard/templates/__init__.py` | Add Drawflow CDN `<script>` + `<link>` to `<head>` |
| `src/dashboard/templates/_panels.py` | New `_flowgraph()` panel (or replace `_workflows()`) |
| `src/dashboard/templates/_tabs.py` | Add "Flowgraph" entry to Workflows nav group |
| `src/dashboard/static/flowgraph.js` | All canvas logic (palette, node types, execute, SSE stream) |
| `src/dashboard/routes/` | `GET /api/flowgraph/agents` — list available agent nodes |
| `src/dashboard/routes/` | `POST /api/flowgraph/execute` — runs exported JSON as pipeline |

---

## 4. Node types

| Type | Colour | Inputs | Outputs |
|---|---|---|---|
| `agent` | cyan | `prompt` (text), `context` (table+ids) | `result` (text) |
| `mcp-tool` | amber | `args` (JSON) | `output` (JSON) |
| `condition` | purple | `value`, `comparator`, `threshold` | `true`, `false` |
| `merge` | green | `a`, `b`, … (N) | `merged` |
| `output` | gray | `text` | — |

---

## 5. Panel structure (`_flowgraph()`)

```
tab_panel("flowgraph", "🔗 Flowgraph")
├── panel_toolbar("Agent Pipeline Editor", refresh_btn, execute_btn, clear_btn, import_btn, export_btn)
├── <div id="fg-canvas-wrap">          ← split view
│   ├── <div id="fg-palette">          ← left: draggable node tiles
│   └── <div id="drawflow" …>         ← right: Drawflow canvas
├── panel_section("Execution log", loading_slot("fg-exec-log"))
└── action_bar(run_btn, status_span("fg-status"))
```

---

## 6. Backend execution flow

```
POST /api/flowgraph/execute
  body: { graph: <Drawflow JSON export> }
  → parse nodes in topological order
  → for each agent node: call A2A /a2a/run
  → stream per-node results via SSE /sse/flowgraph/{run_id}
  → final: { run_id, results: {node_id: text} }
```

---

## 7. Implementation steps (ordered)

1. **CDN injection** — add Drawflow `<script>` + `<link>` to SPA `<head>`
2. **`flowgraph.js`** — `initFlowgraph()`, palette drag-start, node templates, `fgExecute()`
3. **`_flowgraph()` panel** — canvas wrapper + palette + toolbar using component helpers
4. **API route** `GET /api/flowgraph/agents` — returns agent list for palette
5. **API route** `POST /api/flowgraph/execute` — topological executor + SSE stream
6. **SSE handler** `/sse/flowgraph/{run_id}` — per-node result streaming
7. **Tab registration** — add to `_tabs.py` nav

---

## 8. Files to create / modify

```
src/dashboard/static/flowgraph.js              ← new
src/dashboard/routes/flowgraph.py              ← new
src/dashboard/templates/_panels.py             ← _flowgraph() added
src/dashboard/templates/_tabs.py               ← nav entry
src/dashboard/templates/__init__.py            ← CDN link
src/dashboard/app.py                           ← mount routes
```

---

## 9. Out of scope (phase 1)

- Persistence of saved graphs to DB (phase 2: `FlowgraphTemplate` model)
- Multi-user shared canvas (phase 3: CRDT/WebSocket sync)
- Undo/redo (Drawflow supports it natively — enable in phase 2)
