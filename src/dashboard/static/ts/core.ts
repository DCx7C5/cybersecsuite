// Core utilities: DOM helpers, tab management, context bar, formatting

export const $: (id: string) => HTMLElement | null = (id) => document.getElementById(id);

export let currentTab = 'health';

// Per-tab context stats cache: { tabName: [{label, value}, ...] }
interface ContextStat {
  label: string;
  value: string | number;
}

const _ctxCache: Record<string, ContextStat[]> = {};

function _setCtxStat(el: HTMLElement | null, label: string, value: string | number): void {
  if (!el) return;
  el.innerHTML = '<strong>' + value + '</strong>' + label;
  el.style.display = '';
}

function _clearCtx(): void {
  for (let i = 1; i <= 5; i++) {
    const el = $('ctx-s' + i);
    if (el) {
      el.innerHTML = '';
      el.style.display = 'none';
    }
  }
}

function _showCtxStats(stats: ContextStat[]): void {
  const bar = $('context-bar');
  if (!bar) return;
  _clearCtx();
  if (!stats || !stats.length) {
    bar.style.display = 'none';
    return;
  }
  stats.slice(0, 5).forEach((s, i) => _setCtxStat($('ctx-s' + (i + 1)), s.label, s.value));
  bar.style.display = 'flex';
}

export async function _updateContextBar(name: string): Promise<void> {
  if (_ctxCache[name]) {
    _showCtxStats(_ctxCache[name]);
    return;
  }

  const tab_stats: Record<string, () => Promise<ContextStat[]>> = {
    health: () =>
      fetch('/api/overview')
        .then((r) => r.json())
        .then((d) => [
          {
            value: d.uptime_seconds ? Math.round(d.uptime_seconds) + 's' : '—',
            label: ' uptime',
          },
          { value: d.providers?.enabled ?? '—', label: ' providers on' },
          { value: d.models?.total ?? '—', label: ' models' },
        ]),
    usage: () =>
      fetch('/api/overview')
        .then((r) => r.json())
        .then((d) => [
          { value: fmt(d.usage?.total_requests ?? 0), label: ' requests' },
          { value: fmt(d.usage?.total_tokens ?? 0), label: ' tokens' },
          { value: '$' + (d.usage?.total_cost_usd ?? 0).toFixed(4), label: ' cost' },
        ]),
    routing: () =>
      fetch('/api/routing')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.strategy ?? '—', label: ' strategy' },
          { value: d.providers_available ?? '—', label: ' providers' },
        ]),
    findings: () =>
      fetch('/api/findings')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.total ?? 0, label: ' total' },
          { value: d.critical ?? 0, label: ' critical' },
          { value: d.high ?? 0, label: ' high' },
          { value: d.last_24h ?? 0, label: ' last 24h' },
        ]),
    iocs: () =>
      fetch('/api/iocs')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.total ?? 0, label: ' total' },
          { value: d.active ?? 0, label: ' active' },
          { value: d.high_confidence ?? 0, label: ' high conf' },
        ]),
    cases: () =>
      fetch('/api/cases')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.total ?? 0, label: ' cases' },
          { value: d.open ?? 0, label: ' open' },
          { value: d.closed ?? 0, label: ' closed' },
        ]),
    tasks: () =>
      fetch('/api/tasks')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.total ?? 0, label: ' tasks' },
          { value: d.working ?? 0, label: ' running' },
          { value: d.completed ?? 0, label: ' done' },
        ]),
    'agent-factory': () =>
      fetch('/api/agents')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.agents?.length ?? 0, label: ' agents' },
          {
            value: d.agents?.filter((a: any) => a.role === 'orchestrator').length ?? 0,
            label: ' orchestrators',
          },
        ]),
    'agent-crafter': () =>
      fetch('/api/team-agents')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [{ value: d.total ?? 0, label: ' agents' }]),
    intel: () =>
      fetch('/api/intelligence')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.mitre_techniques ?? 0, label: ' MITRE' },
          { value: d.cves ?? 0, label: ' CVEs' },
          { value: d.cwes ?? 0, label: ' CWEs' },
        ]),
    compliance: () =>
      fetch('/api/compliance')
        .then((r) => r.json())
        .catch(() => ({}))
        .then((d) => [
          { value: d.total ?? 0, label: ' rules' },
          { value: d.critical ?? 0, label: ' critical' },
          { value: d.frameworks ?? 0, label: ' frameworks' },
        ]),
  };

  const fn = tab_stats[name];
  if (!fn) {
    _showCtxStats([]);
    return;
  }

  try {
    const stats = await fn();
    _ctxCache[name] = stats;
    _showCtxStats(stats);
  } catch {
    _showCtxStats([]);
  }
}

export function showTab(name: string): void {
  document.querySelectorAll('[id^="tab-"]').forEach((el) => {
    (el as HTMLElement).style.display = 'none';
  });
  document.querySelectorAll('.tab').forEach((el) => {
    el.classList.remove('active');
  });
  const panel = $('tab-' + name);
  if (panel) {
    panel.style.display = '';
    panel.classList.add('panel-enter');
  }
  const navItem = $('nav-' + name);
  if (navItem) navItem.classList.add('active');
  const crumb = document.querySelector('#topbar-title') as HTMLElement | null;
  if (crumb && navItem) crumb.textContent = '▶ ' + navItem.textContent!.trim().toUpperCase();
  currentTab = name;
  _updateStatusBar(name);
  _updateContextBar(name);
}

export function fmt(n: number): string {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return String(n);
}

interface Provider {
  is_free?: boolean;
  auth_type?: string;
  models: { cost_in: number; cost_out: number }[];
}

export function tierBadge(p: Provider): string {
  if (p.is_free || p.auth_type === 'none' || p.auth_type === 'browser')
    return '<span class="badge badge-free">FREE</span>';
  if (!p.models.length) return '<span class="badge badge-standard">STD</span>';
  const avg = p.models.reduce((s, m) => s + (m.cost_in + m.cost_out) / 2, 0) / p.models.length;
  if (avg < 1) return '<span class="badge badge-budget">BUDGET</span>';
  if (avg <= 5) return '<span class="badge badge-standard">STD</span>';
  return '<span class="badge badge-premium">PREMIUM</span>';
}

interface Model {
  cost_in: number;
}

export function costRange(models: Model[]): string {
  if (!models.length) return '$0';
  const costs = models.map((m) => m.cost_in);
  const min = Math.min(...costs);
  const max = Math.max(...costs);
  if (min === max) return '$' + min.toFixed(2);
  return '$' + min.toFixed(2) + '-' + max.toFixed(2);
}

export async function fetchApi(endpoint: string): Promise<any> {
  try {
    const response = await fetch(endpoint);
    return await response.json();
  } catch (e) {
    console.error('API fetch failed for ' + endpoint, e);
    return { error: 'Failed to fetch: ' + (e instanceof Error ? e.message : String(e)) };
  }
}

function _updateStatusBar(tab: string): void {
  const el = $('sb-tab');
  if (el) el.textContent = '\u2B21 ' + tab.toUpperCase().replace(/-/g, ' ');
}

// Update time in status bar every second
setInterval(() => {
  const el = $('sb-time');
  if (el) el.textContent = new Date().toLocaleTimeString();
}, 1000);
