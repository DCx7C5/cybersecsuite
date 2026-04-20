// charts.ts — Chart.js + ECharts registry and per-tab loaders

/* global declarations for CDN-loaded libraries */
declare const Chart: any;
declare const echarts: any;

const _charts: Record<string, any> = {};

function _themeColors() {
  const style = getComputedStyle(document.documentElement);
  return {
    accent:    style.getPropertyValue('--accent').trim()    || '#3574f0',
    warn:      style.getPropertyValue('--amber').trim()     || '#cb902e',
    danger:    style.getPropertyValue('--red').trim()       || '#c75450',
    success:   style.getPropertyValue('--success').trim()   || '#6a9955',
    border:    style.getPropertyValue('--border').trim()    || '#3d3f43',
    textMuted: style.getPropertyValue('--text-muted').trim()|| '#808590',
    surface:   style.getPropertyValue('--surface-2').trim() || '#313438',
  };
}

function _initChartJs(id: string, config: any): void {
  const el = document.getElementById(id) as HTMLCanvasElement | null;
  if (!el) return;
  if (_charts[id]) { try { _charts[id].destroy(); } catch (_) {} }
  _charts[id] = new Chart(el, config);
}

function _initEChart(id: string, option: any): void {
  const el = document.getElementById(id);
  if (!el) return;
  if (_charts[id]) { try { _charts[id].dispose(); } catch (_) {} }
  _charts[id] = echarts.init(el, 'dark');
  _charts[id].setOption(option);
}

async function _fetchChartData(name: string, params: Record<string, string> = {}): Promise<any> {
  try {
    const qs = new URLSearchParams(params).toString();
    const res = await fetch(`/api/charts/${name}?${qs}`);
    return await res.json();
  } catch (_) {
    return { labels: [], datasets: [] };
  }
}

// ── Usage tab ─────────────────────────────────────────────────────────────────

export async function loadUsageCharts(): Promise<void> {
  if (typeof Chart === 'undefined') return;
  const t = _themeColors();
  const [share, trend] = await Promise.all([
    _fetchChartData('provider-share'),
    _fetchChartData('token-trend'),
  ]);

  _initChartJs('chart-provider-share', {
    type: 'doughnut',
    data: {
      labels: share.labels || [],
      datasets: [{
        data: share.datasets?.[0]?.data || [],
        backgroundColor: [t.accent, t.warn, t.success, t.danger, '#9876aa', '#6897bb'],
        borderColor: t.border,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { color: t.textMuted, font: { size: 11 } } } },
    },
  });

  _initChartJs('chart-token-trend', {
    type: 'bar',
    data: {
      labels: trend.labels || [],
      datasets: [{
        label: 'Requests',
        data: trend.datasets?.[0]?.data || [],
        backgroundColor: t.accent + '80',
        borderColor: t.accent,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: t.border }, ticks: { color: t.textMuted } },
        y: { grid: { color: t.border }, ticks: { color: t.textMuted } },
      },
    },
  });
}

// ── IOC tab ───────────────────────────────────────────────────────────────────

export async function loadIocCharts(): Promise<void> {
  if (typeof Chart === 'undefined' || typeof echarts === 'undefined') return;
  const t = _themeColors();
  const [types, timeline] = await Promise.all([
    _fetchChartData('ioc-types'),
    _fetchChartData('ioc-timeline'),
  ]);

  _initChartJs('chart-ioc-types', {
    type: 'doughnut',
    data: {
      labels: types.labels || [],
      datasets: [{
        data: types.datasets?.[0]?.data || [],
        backgroundColor: [t.accent, t.warn, t.danger, t.success, '#8b5cf6', '#06b6d4'],
        borderColor: t.border,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { color: t.textMuted, font: { size: 11 } } } },
    },
  });

  _initEChart('chart-ioc-timeline', {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    xAxis: { type: 'time', axisLabel: { color: t.textMuted, fontSize: 10 } },
    yAxis: {
      type: 'category',
      data: timeline.labels || [],
      axisLabel: { color: t.textMuted, fontSize: 10 },
    },
    series: [{
      type: 'scatter',
      data: (timeline.datasets?.[0]?.data || []).map((pt: any[]) => [pt[0], pt[1]]),
      symbolSize: 8,
      itemStyle: { color: t.accent },
    }],
    dataZoom: [{ type: 'inside' }],
  });
}

// ── Findings tab ──────────────────────────────────────────────────────────────

export async function loadFindingsCharts(): Promise<void> {
  if (typeof echarts === 'undefined') return;
  const t = _themeColors();
  const heatmap = await _fetchChartData('findings-heatmap');

  _initEChart('chart-findings-heatmap', {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: (p: any) => `${p.data[2]} findings` },
    visualMap: {
      min: 0,
      max: heatmap.max || 10,
      inRange: { color: [t.surface, t.danger] },
      textStyle: { color: t.textMuted, fontSize: 10 },
    },
    xAxis: {
      type: 'category',
      data: heatmap.labels || [],
      axisLabel: { color: t.textMuted, fontSize: 9, rotate: 45 },
    },
    yAxis: {
      type: 'category',
      data: heatmap.severities || ['critical', 'high', 'medium', 'low', 'info'],
      axisLabel: { color: t.textMuted, fontSize: 10 },
    },
    series: [{
      type: 'heatmap',
      data: heatmap.datasets?.[0]?.data || [],
      emphasis: { itemStyle: { shadowBlur: 10 } },
    }],
    grid: { containLabel: true },
  });
}

// ── Compliance / MITRE tab ────────────────────────────────────────────────────

export async function loadComplianceCharts(): Promise<void> {
  if (typeof echarts === 'undefined') return;
  const t = _themeColors();
  const heatmap = await _fetchChartData('mitre-heatmap');

  _initEChart('chart-mitre-heatmap', {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: (p: any) => `${p.data[2]} hits` },
    visualMap: {
      min: 0,
      max: heatmap.max || 5,
      inRange: { color: [t.surface, t.accent] },
      textStyle: { color: t.textMuted, fontSize: 10 },
    },
    xAxis: {
      type: 'category',
      data: heatmap.tactics || [],
      axisLabel: { color: t.textMuted, fontSize: 9, rotate: 30 },
    },
    yAxis: {
      type: 'category',
      data: heatmap.labels || [],
      axisLabel: { color: t.textMuted, fontSize: 9 },
    },
    series: [{ type: 'heatmap', data: heatmap.datasets?.[0]?.data || [] }],
    dataZoom: [{ type: 'inside', orient: 'vertical' }],
    grid: { containLabel: true },
  });
}

// ── Health tab ────────────────────────────────────────────────────────────────

export async function loadHealthCharts(): Promise<void> {
  if (typeof Chart === 'undefined') return;
  const t = _themeColors();
  const pct = await _fetchChartData('latency-percentiles');

  _initChartJs('chart-latency-pct', {
    type: 'line',
    data: {
      labels: pct.labels || [],
      datasets: [
        { label: 'p50', data: pct.datasets?.[0]?.data || [], borderColor: t.success,  backgroundColor: 'transparent', tension: 0.3 },
        { label: 'p95', data: pct.datasets?.[1]?.data || [], borderColor: t.warn,    backgroundColor: 'transparent', tension: 0.3 },
        { label: 'p99', data: pct.datasets?.[2]?.data || [], borderColor: t.danger,  backgroundColor: 'transparent', tension: 0.3 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: t.textMuted, font: { size: 11 } } } },
      scales: {
        x: { grid: { color: t.border }, ticks: { color: t.textMuted } },
        y: {
          grid: { color: t.border },
          ticks: { color: t.textMuted },
          title: { display: true, text: 'ms', color: t.textMuted },
        },
      },
    },
  });
}

// ── Resize handler ────────────────────────────────────────────────────────────

window.addEventListener('resize', () => {
  Object.values(_charts).forEach((c: any) => {
    if (c && typeof c.resize === 'function') c.resize(); // ECharts
  });
});
