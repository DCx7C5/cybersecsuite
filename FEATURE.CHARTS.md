# Feature Plan: Interactive Charts

> Adds rich, interactive data visualisations to the dashboard — covering
> provider/routing analytics, forensic timelines, IOC scatter plots,
> cost trends, and MITRE ATT&CK heatmaps.

---

## 1. Goal

Replace all static `<div class="toggles-loading">` stat placeholders and raw
tables with interactive charts so analysts can:

- Spot trends in AI provider latency / cost over time
- Visualise IOC volume by type and date
- Drill into MITRE technique frequency heatmaps
- Compare routing strategy performance side-by-side

---

## 2. Library choices

Two complementary libraries, both CDN-installable, zero-framework:

### Chart.js 4 (MIT, ~14 KB gz)
https://www.chartjs.org/

Use for: **lightweight stats charts** — bar, doughnut, line, radar, mixed.

Chosen because:
- Tiny, fast, highly accessible
- Built-in animation and tooltips
- Minimal config; no build step
- Perfect for the Usage, Telemetry, Health, and Routing tabs

### Apache ECharts 5 (Apache 2.0, ~47 KB gz core)
https://echarts.apache.org/

Use for: **advanced forensic visualisations** — heatmap, scatter timeline,
treemap, sankey, candlestick, 3D scatter.

Chosen because:
- Rich chart types not in Chart.js (heatmap, sankey, tree)
- DataZoom/brush for time-series drill-down
- Excellent for MITRE ATT&CK matrix, IOC timelines, cost calendars

---

## 3. Chart inventory by tab

| Tab | Chart | Library | ID |
|---|---|---|---|
| Usage | Provider request share — doughnut | Chart.js | `chart-provider-share` |
| Usage | Token usage over 7 days — bar | Chart.js | `chart-token-trend` |
| Routing | Strategy latency comparison — bar | Chart.js | `chart-strategy-latency` |
| Routing | Circuit breaker events — line | Chart.js | `chart-cb-events` |
| Health | Request latency p50/p95/p99 — line | Chart.js | `chart-latency-pct` |
| Telemetry | Throughput over time — area | Chart.js | `chart-throughput` |
| IOCs | IOC type distribution — doughnut | Chart.js | `chart-ioc-types` |
| IOCs | IOC timeline scatter | ECharts | `chart-ioc-timeline` |
| Findings | Severity heatmap by date | ECharts | `chart-findings-heatmap` |
| Compliance | MITRE technique frequency heatmap | ECharts | `chart-mitre-heatmap` |
| Cases | Open vs closed trend — line | Chart.js | `chart-cases-trend` |

---

## 4. Integration points

| Layer | Change |
|---|---|
| `src/dashboard/templates/__init__.py` | Add Chart.js + ECharts CDN `<script>` to `<head>` |
| `src/dashboard/static/charts.js` | All chart init/update helpers + `registerCharts()` |
| `src/dashboard/templates/_panels.py` | Add `<canvas>` / `<div>` chart containers in relevant panels |
| `src/dashboard/routes/charts.py` | `GET /api/charts/{name}` — returns JSON dataset for each chart |

---

## 5. Data API

All chart data served from a single parameterised endpoint:

```
GET /api/charts/{name}?range=7d&granularity=hour
```

Returns `{ labels: [...], datasets: [...] }` — compatible with both Chart.js
and ECharts `dataset` format.

| Route | Source |
|---|---|
| `/api/charts/provider-share` | `mcp__cybersec__proxy_usage` |
| `/api/charts/token-trend` | Proxy usage log (rolling 7d) |
| `/api/charts/latency-percentiles` | Telemetry ring buffer |
| `/api/charts/ioc-timeline` | `IOC` model, `created_at` + `type` |
| `/api/charts/findings-heatmap` | `Finding` model, `severity` + `created_at` |
| `/api/charts/mitre-heatmap` | `MitreTechnique` + `Finding` join |

---

## 6. Panel changes

### Usage tab — add below stats grid
```python
panel_section(
    "Provider breakdown",
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">'
    '  <canvas id="chart-provider-share" height="200"></canvas>'
    '  <canvas id="chart-token-trend"    height="200"></canvas>'
    '</div>',
)
```

### IOCs tab — timeline chart
```python
panel_section(
    "Timeline",
    '<div id="chart-ioc-timeline" style="height:260px"></div>',
)
```

### Compliance tab — MITRE heatmap
```python
panel_section(
    "MITRE technique frequency",
    '<div id="chart-mitre-heatmap" style="height:340px"></div>',
    desc="Technique IDs detected across all findings. Darker = more hits.",
)
```

---

## 7. `charts.js` structure

```js
// Chart registry — maps canvas/div id → Chart.js or ECharts instance
const _charts = {};

function initChartJs(id, config)   { _charts[id] = new Chart(document.getElementById(id), config); }
function initEChart(id, option)    { _charts[id] = echarts.init(document.getElementById(id)); _charts[id].setOption(option); }
function updateChart(id, data)     { /* patch datasets, call update() / setOption() */ }
function destroyChart(id)          { _charts[id]?.destroy?.(); _charts[id]?.dispose?.(); delete _charts[id]; }

async function fetchChartData(name, params = {}) {
  const qs = new URLSearchParams(params).toString();
  return (await fetch(`/api/charts/${name}?${qs}`)).json();
}

// Per-tab loaders called from tab-switch handler
async function loadUsageCharts()      { /* fetchChartData + initChartJs */ }
async function loadHealthCharts()     { /* … */ }
async function loadIocCharts()        { /* … */ }
async function loadComplianceCharts() { /* … */ }

// Resize all on window resize
window.addEventListener("resize", () =>
  Object.values(_charts).forEach(c => c.resize?.() /* ECharts */ || c.resize?.())
);
```

---

## 8. Implementation steps (ordered)

1. **CDN injection** — add Chart.js + ECharts `<script>` to SPA `<head>`
2. **`charts.js`** — registry, fetch helper, resize handler
3. **API route** `GET /api/charts/{name}` — data adapter per chart name
4. **Panel `<canvas>` / `<div>` insertion** — Usage, Health, IOCs, Findings, Compliance
5. **Chart init loaders** — hook into existing tab-switch JS (`showTab()`)
6. **MITRE heatmap** — matrix layout using ECharts `heatmap` series
7. **IOC timeline** — ECharts `scatter` with DataZoom
8. **Polish** — dark theme palette (`var(--accent)` colours → chart datasets)

---

## 9. Theme integration

Inject CSS variable values into chart colour palettes at runtime:

```js
const style = getComputedStyle(document.documentElement);
const accent = style.getPropertyValue("--accent").trim();      // e.g. #22d3ee
const border = style.getPropertyValue("--border").trim();      // e.g. #1e293b
const textMuted = style.getPropertyValue("--text-muted").trim();
```

Use these as `borderColor`, `backgroundColor`, grid line colours, and label colours
so charts automatically inherit the dashboard theme.

---

## 10. Files to create / modify

```
src/dashboard/static/charts.js               ← new
src/dashboard/routes/charts.py               ← new
src/dashboard/templates/_panels.py           ← canvas/div containers in 5 panels
src/dashboard/templates/__init__.py          ← CDN links
src/dashboard/app.py                         ← mount /api/charts route
```

---

## 11. Out of scope (phase 1)

- Exportable PNG/SVG (Chart.js supports it — enable in phase 2)
- Dashboard-level chart layout persistence (phase 2)
- Real-time streaming chart updates via SSE (phase 3)
