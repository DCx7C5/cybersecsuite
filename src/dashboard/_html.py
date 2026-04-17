"""Dashboard HTML template."""

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CyberSecSuite Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwindcss_config={theme:{extend:{colors:{cyber:'#0ff',dark:'#0a0e17'}}}}</script>
<style>
  body { background: #0a0e17; color: #e2e8f0; font-family: 'JetBrains Mono', 'Fira Code', monospace; }
  .card { background: #111827; border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1.25rem; }
  .card:hover { border-color: #0ff3; }
  .glow { text-shadow: 0 0 10px #0ff6; }
  .badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
  .badge-free { background: #064e3b; color: #34d399; }
  .badge-budget { background: #1e3a5f; color: #60a5fa; }
  .badge-standard { background: #3b2f63; color: #a78bfa; }
  .badge-premium { background: #5b2130; color: #fb7185; }
  .badge-ok { background: #064e3b; color: #34d399; }
  .badge-err { background: #5b2130; color: #fb7185; }
  .badge-browser { background: #312e81; color: #818cf8; }
  .progress { height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; }
  .progress-bar { height: 100%; background: linear-gradient(90deg, #0ff, #6366f1); transition: width 0.5s; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 0.5rem; border-bottom: 1px solid #1e293b; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }
  td { padding: 0.5rem; border-bottom: 1px solid #1e293b08; font-size: 0.875rem; }
  tr:hover td { background: #1e293b40; }
  .tab { cursor: pointer; padding: 0.5rem 1rem; border-bottom: 2px solid transparent; color: #94a3b8; }
  .tab.active { border-color: #0ff; color: #0ff; }
  .tab:hover { color: #e2e8f0; }
  @keyframes pulse-glow { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
  .loading { animation: pulse-glow 1.5s infinite; }
</style>
</head>
<body class="min-h-screen">
<div class="max-w-7xl mx-auto px-4 py-6">
  <!-- Header -->
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-2xl font-bold glow" style="color:#0ff">&#x1f6e1; CyberSecSuite</h1>
      <p class="text-sm text-gray-500 mt-1">AI Proxy Dashboard &mdash; Multi-Provider Router</p>
    </div>
    <div class="flex gap-3">
      <button onclick="refresh()" class="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700">&#x21bb; Refresh</button>
      <span id="uptime" class="text-xs text-gray-500 self-center"></span>
    </div>
  </div>

  <!-- Stats row -->
  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6" id="stats">
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-providers">-</div><div class="text-xs text-gray-500">Providers</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-enabled">-</div><div class="text-xs text-gray-500">Enabled</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-models">-</div><div class="text-xs text-gray-500">Models</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-requests">-</div><div class="text-xs text-gray-500">Requests</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-tokens">-</div><div class="text-xs text-gray-500">Tokens</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-cost">-</div><div class="text-xs text-gray-500">Cost (USD)</div></div>
  </div>

  <!-- Tier breakdown -->
  <div class="grid grid-cols-4 gap-4 mb-6" id="tiers">
    <div class="card text-center"><span class="badge badge-free">FREE</span><div class="text-xl font-bold mt-2" id="t-free">-</div></div>
    <div class="card text-center"><span class="badge badge-budget">BUDGET</span><div class="text-xl font-bold mt-2" id="t-budget">-</div></div>
    <div class="card text-center"><span class="badge badge-standard">STANDARD</span><div class="text-xl font-bold mt-2" id="t-standard">-</div></div>
    <div class="card text-center"><span class="badge badge-premium">PREMIUM</span><div class="text-xl font-bold mt-2" id="t-premium">-</div></div>
  </div>

  <!-- Tabs -->
  <div class="flex gap-1 mb-4 border-b border-gray-800 flex-wrap">
    <div class="tab active" onclick="showTab('providers')">Providers</div>
    <div class="tab" onclick="showTab('usage')">Usage & Cost</div>
    <div class="tab" onclick="showTab('agents')">&#x1f916; Agents</div>
    <div class="tab" onclick="showTab('routing')">&#x1f500; Routing</div>
    <div class="tab" onclick="showTab('factory')">&#x1f3ed; Factory</div>
    <div class="tab" onclick="showTab('prompts')">&#x1f4dd; Prompts</div>
    <div class="tab" onclick="showTab('health')">Health</div>
    <div class="tab" onclick="showTab('crypto')">&#x1f512; Crypto</div>
    <div class="tab" onclick="showTab('a2a')">&#x1f310; A2A</div>
    <div class="tab" onclick="showTab('investigations')">&#x1f50d; Investigations</div>
    <div class="tab" onclick="showTab('dbcounts')">&#x1f4ca; DB Counts</div>
    <div class="tab" onclick="showTab('cases')">&#x1f4c2; Cases</div>
    <div class="tab" onclick="showTab('tasks')">&#x23f1; Tasks</div>
    <div class="tab" onclick="showTab('pocs')">&#x1f4a3; PoCs</div>
    <div class="tab" onclick="showTab('explorer')">&#x1f50e; Explorer</div>
  </div>

  <!-- Providers tab -->
  <div id="tab-providers" class="card">
    <h3 class="text-lg font-semibold mb-3">&#x1f310; Provider Registry</h3>
    <div id="providers-table"><div class="loading text-gray-500">Loading providers...</div></div>
  </div>

  <!-- Usage tab -->
  <div id="tab-usage" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f4c8; Recent Requests</h3>
    <div id="usage-table"><div class="loading text-gray-500">Loading usage...</div></div>
  </div>

  <!-- Health tab -->
  <div id="tab-health" class="card" style="display:none">
    <div id="health-content" class="loading">Checking health...</div>
  </div>

  <!-- Agents tab -->
  <div id="tab-agents" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f916; Agent Registry</h3>
    <div id="agents-content" class="loading">Loading agents...</div>
  </div>

  <!-- Routing tab -->
  <div id="tab-routing" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f500; Routing Engine</h3>
    <div id="routing-content" class="loading">Loading routing...</div>
  </div>

  <!-- Factory tab -->
  <div id="tab-factory" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f3ed; Agent Factory</h3>
    <div id="factory-content" class="loading">Loading factory...</div>
  </div>

  <!-- Prompts tab -->
  <div id="tab-prompts" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f4dd; Prompts & Templates</h3>
    <div id="prompts-content" class="loading">Loading prompts...</div>
  </div>

  <!-- Crypto tab -->
  <div id="tab-crypto" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f512; Artifact Signing</h3>
    <div id="crypto-content" class="loading">Loading crypto stats...</div>
  </div>

  <!-- A2A tab -->
  <div id="tab-a2a" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f916; A2A Agent Tasks</h3>
    <div id="a2a-content" class="loading">Loading A2A stats...</div>
  </div>

  <!-- Investigations tab -->
  <div id="tab-investigations" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f50d; Investigations</h3>
    <div id="inv-content" class="loading">Loading investigation stats...</div>
  </div>

   <!-- DB Counts tab -->
   <div id="tab-dbcounts" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f4ca; Database Table Counts</h3>
     <div id="db-content" class="loading">Loading DB counts...</div>
   </div>

   <!-- Cases tab -->
   <div id="tab-cases" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f4c2; Phase 0 Case Intake</h3>
     <div class="grid grid-cols-3 gap-4 mb-4">
       <div class="card text-center"><div class="text-2xl font-bold" id="cases-total">-</div><div class="text-xs text-gray-500">Total Cases</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-green-400" id="cases-open">-</div><div class="text-xs text-gray-500">Open</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-gray-400" id="cases-closed">-</div><div class="text-xs text-gray-500">Closed</div></div>
     </div>
     <div id="cases-table"><div class="loading text-gray-500">Loading cases...</div></div>
   </div>

   <!-- Tasks tab -->
   <div id="tab-tasks" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x23f1; Task Management</h3>
     <div class="grid grid-cols-5 gap-4 mb-4">
       <div class="card text-center"><div class="text-2xl font-bold" id="tasks-total">-</div><div class="text-xs text-gray-500">Total</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-blue-400" id="tasks-submitted">-</div><div class="text-xs text-gray-500">Submitted</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-yellow-400" id="tasks-working">-</div><div class="text-xs text-gray-500">Working</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-green-400" id="tasks-completed">-</div><div class="text-xs text-gray-500">Done</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-red-400" id="tasks-failed">-</div><div class="text-xs text-gray-500">Failed</div></div>
     </div>
     <div id="tasks-table"><div class="loading text-gray-500">Loading tasks...</div></div>
   </div>

   <!-- PoCs tab -->
   <div id="tab-pocs" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f4a3; Proof-of-Concept Exploits</h3>
     <div id="pocs-content" class="loading">Loading PoC data...</div>
   </div>

   <!-- Explorer tab -->
   <div id="tab-explorer" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f50e; Database Explorer</h3>
     <div class="flex items-center gap-3 mb-4">
       <select id="explorer-model" onchange="loadExplorerTable()"
         class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">
         <option value="">Select a model...</option>
       </select>
       <span id="explorer-count" class="text-xs text-gray-500"></span>
     </div>
     <div id="explorer-table"></div>
   </div>
</div>

<script>
const $ = id => document.getElementById(id);
let currentTab = 'providers';

function showTab(name) {
  document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  $('tab-' + name).style.display = '';
  event.target.classList.add('active');
  currentTab = name;
}

function fmt(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return String(n);
}

function tierBadge(p) {
  if (p.is_free || p.auth_type === 'none' || p.auth_type === 'browser') return '<span class="badge badge-free">FREE</span>';
  if (!p.models.length) return '<span class="badge badge-standard">STD</span>';
  const avg = p.models.reduce((s,m) => s + (m.cost_in + m.cost_out)/2, 0) / p.models.length;
  if (avg < 1) return '<span class="badge badge-budget">BUDGET</span>';
  if (avg <= 5) return '<span class="badge badge-standard">STD</span>';
  return '<span class="badge badge-premium">PREMIUM</span>';
}

function costRange(models) {
  if (!models.length) return '$0';
  const costs = models.map(m => m.cost_in);
  const min = Math.min(...costs), max = Math.max(...costs);
  if (min === max) return '$' + min.toFixed(2);
  return '$' + min.toFixed(2) + '-' + max.toFixed(2);
}

// ── renderTable: generic sortable, searchable, paginated table ──────────────
function renderTable(containerId, schema, rows, opts = {}) {
  const el = $(containerId);
  if (!el) return;
  const pageSize = opts.pageSize || 25;
  let page = 0;
  let sortCol = opts.sortCol || null;
  let sortDir = opts.sortDir || 'asc';
  let filter = '';

  function formatCell(val, col) {
    if (val === null || val === undefined) return '<span class="text-gray-600">—</span>';
    const t = col.type || 'string';
    if (t === 'datetime' && val) {
      try { return new Date(val).toLocaleString(); } catch { return String(val); }
    }
    if (t === 'bool') return val ? '&#x2705;' : '&#x274c;';
    if (t === 'json') {
      const s = typeof val === 'string' ? val : JSON.stringify(val);
      return s.length > 80 ? '<span title="' + s.replace(/"/g,'&quot;') + '">' + s.slice(0,77) + '&hellip;</span>' : s;
    }
    if (t === 'number') return typeof val === 'number' ? val.toLocaleString() : String(val);
    const s = String(val);
    return s.length > 120 ? '<span title="' + s.replace(/"/g,'&quot;') + '">' + s.slice(0,117) + '&hellip;</span>' : s;
  }

  function render() {
    let data = rows;
    if (filter) {
      const q = filter.toLowerCase();
      data = data.filter(r => schema.some(c => String(r[c.key] || '').toLowerCase().includes(q)));
    }
    if (sortCol !== null) {
      const col = schema[sortCol];
      data = [...data].sort((a, b) => {
        let va = a[col.key], vb = b[col.key];
        if (va == null) va = '';
        if (vb == null) vb = '';
        if (col.type === 'number') { va = Number(va) || 0; vb = Number(vb) || 0; }
        else { va = String(va).toLowerCase(); vb = String(vb).toLowerCase(); }
        return sortDir === 'asc' ? (va < vb ? -1 : va > vb ? 1 : 0) : (va > vb ? -1 : va < vb ? 1 : 0);
      });
    }
    const totalPages = Math.max(1, Math.ceil(data.length / pageSize));
    if (page >= totalPages) page = totalPages - 1;
    const sliced = data.slice(page * pageSize, (page + 1) * pageSize);

    let h = '<div class="flex items-center gap-3 mb-3">';
    h += '<input type="text" placeholder="Search..." value="' + filter.replace(/"/g,'&quot;') + '" '
       + 'oninput="window._rt_' + containerId + '_filter(this.value)" '
       + 'class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:220px">';
    h += '<span class="text-xs text-gray-500">' + data.length + ' rows</span>';
    h += '</div>';
    h += '<table><thead><tr>';
    schema.forEach((c, i) => {
      const arrow = sortCol === i ? (sortDir === 'asc' ? ' &#x25b2;' : ' &#x25bc;') : '';
      h += '<th style="cursor:pointer" onclick="window._rt_' + containerId + '_sort(' + i + ')">' + (c.label || c.key) + arrow + '</th>';
    });
    h += '</tr></thead><tbody>';
    if (!sliced.length) {
      h += '<tr><td colspan="' + schema.length + '" class="text-center text-gray-500">No data</td></tr>';
    } else {
      sliced.forEach(r => {
        h += '<tr>';
        schema.forEach(c => { h += '<td>' + formatCell(r[c.key], c) + '</td>'; });
        h += '</tr>';
      });
    }
    h += '</tbody></table>';
    if (totalPages > 1) {
      h += '<div class="flex items-center justify-between mt-3">';
      h += '<button onclick="window._rt_' + containerId + '_page(-1)" class="px-2 py-1 text-xs bg-gray-800 rounded' + (page === 0 ? ' opacity-30' : '') + '" ' + (page === 0 ? 'disabled' : '') + '>&laquo; Prev</button>';
      h += '<span class="text-xs text-gray-500">Page ' + (page+1) + ' / ' + totalPages + '</span>';
      h += '<button onclick="window._rt_' + containerId + '_page(1)" class="px-2 py-1 text-xs bg-gray-800 rounded' + (page >= totalPages-1 ? ' opacity-30' : '') + '" ' + (page >= totalPages-1 ? 'disabled' : '') + '>Next &raquo;</button>';
      h += '</div>';
    }
    el.innerHTML = h;
  }

  window['_rt_' + containerId + '_sort'] = function(i) {
    if (sortCol === i) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    else { sortCol = i; sortDir = 'asc'; }
    render();
  };
  window['_rt_' + containerId + '_filter'] = function(v) { filter = v; page = 0; render(); };
  window['_rt_' + containerId + '_page'] = function(d) { page += d; render(); };
  render();
}

async function refresh() {
  try {
    const [ov, pv, uv, hv, cv, av, iv, dv, agv, rtv, fv, pmv, casesv, tasksv, pocv] = await Promise.all([
      fetch('/dashboard/api/overview').then(r => r.json()),
      fetch('/dashboard/api/providers').then(r => r.json()),
      fetch('/dashboard/api/usage').then(r => r.json()),
      fetch('/dashboard/api/health').then(r => r.json()),
      fetch('/dashboard/api/crypto').then(r => r.json()),
      fetch('/dashboard/api/a2a').then(r => r.json()),
      fetch('/dashboard/api/investigations').then(r => r.json()),
      fetch('/dashboard/api/db-counts').then(r => r.json()),
      fetch('/dashboard/api/agents').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/routing').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/agent-factory').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/prompts').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/cases').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/tasks').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/pocs').then(r => r.json()).catch(() => ({error:'unavailable'})),
    ]);

    // Stats
    $('s-providers').textContent = ov.providers.total;
    $('s-enabled').textContent = ov.providers.enabled;
    $('s-models').textContent = ov.models.total;
    $('s-requests').textContent = fmt(ov.usage.total_requests);
    $('s-tokens').textContent = fmt(ov.usage.total_tokens);
    $('s-cost').textContent = '$' + ov.usage.total_cost_usd.toFixed(4);
    $('uptime').textContent = Math.round(ov.uptime_seconds) + 's uptime';

    // Tiers
    $('t-free').textContent = ov.tiers.free;
    $('t-budget').textContent = ov.tiers.budget;
    $('t-standard').textContent = ov.tiers.standard;
    $('t-premium').textContent = ov.tiers.premium;

    // Remove loading
    document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));

    // Providers table
    renderTable('providers-table', [
      {key: 'provider', label: 'Provider', type: 'string'},
      {key: 'status', label: 'Status', type: 'string'},
      {key: 'type', label: 'Type', type: 'string'},
      {key: 'format', label: 'Format', type: 'string'},
      {key: 'models', label: 'Models', type: 'number'},
      {key: 'rpm', label: 'RPM', type: 'string'},
      {key: 'cost', label: 'Cost /M', type: 'string'},
    ], pv.map(p => ({
      provider: '<strong>' + p.name + '</strong><br><span class="text-xs text-gray-500">' + p.id + '</span>',
      status: p.status === 'available'
        ? '<span class="badge badge-ok">ON</span>'
        : '<span class="badge badge-err">' + (p.status || '?').toUpperCase() + '</span>',
      type: p.auth_type === 'browser'
        ? '<span class="badge badge-browser">BROWSER</span>'
        : tierBadge(p),
      format: p.api_format,
      models: p.models.length,
      rpm: p.rate_limit && p.rate_limit.rpm_remaining !== undefined
        ? Math.round(p.rate_limit.rpm_remaining) + '/' + p.rate_limit.rpm_capacity
        : '—',
      cost: costRange(p.models) + '/M',
    })));

    // Usage table
    renderTable('usage-table', [
      {key: 'provider', label: 'Provider', type: 'string'},
      {key: 'model', label: 'Model', type: 'string'},
      {key: 'tokens', label: 'Tokens', type: 'number'},
      {key: 'cost_usd', label: 'Cost USD', type: 'number'},
      {key: 'latency_ms', label: 'Latency ms', type: 'number'},
      {key: 'stream', label: 'Stream', type: 'bool'},
      {key: 'status', label: 'Status', type: 'string'},
    ], (uv.recent || []).map(r => ({
      provider: r.provider,
      model: r.model,
      tokens: r.tokens,
      cost_usd: r.cost_usd,
      latency_ms: r.latency_ms,
      stream: r.stream,
      status: r.success
        ? '<span class="badge badge-ok">OK</span>'
        : '<span class="badge badge-err">FAIL</span>',
    })));

    // Health
    const hc = $('health-content');
    const dbStatus = hv.database.status === 'ok' ? '&#x2705;' : '&#x274c;';
    hc.innerHTML = '<div class="grid grid-cols-2 gap-4">'
      + '<div><h4 class="font-semibold mb-2">Database</h4>'
      + '<p>' + dbStatus + ' ' + (hv.database.status || 'unknown') + '</p>'
      + '<p class="text-xs text-gray-500">Tables: ' + (hv.database.table_count || '?') + '</p></div>'
      + '<div><h4 class="font-semibold mb-2">Proxy</h4>'
      + '<p>&#x2705; ' + hv.proxy.providers_enabled + ' providers enabled</p>'
      + '<p class="text-xs text-gray-500">' + hv.proxy.providers_free + ' free providers</p></div>'
      + '</div>';
    hc.classList.remove('loading');

    // Crypto tab
    const cc = $('crypto-content');
    if (cv.error) {
      cc.innerHTML = '<p class="text-red-400">Error: ' + cv.error + '</p>';
    } else {
      cc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + cv.total_artifacts + '</div><div class="text-xs text-gray-500">Total Artifacts</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-green-400">' + cv.valid + '</div><div class="text-xs text-gray-500">Valid Sigs</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' + cv.invalid + '</div><div class="text-xs text-gray-500">Invalid Sigs</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Recent Signature Logs</h4>'
        + '<div id="crypto-sig-table"></div>';
      renderTable('crypto-sig-table', [
        {key: 'artifact_id', label: 'Artifact', type: 'string'},
        {key: 'action', label: 'Action', type: 'string'},
        {key: 'status', label: 'Status', type: 'string'},
        {key: 'key_id', label: 'Key', type: 'string'},
        {key: 'created_at', label: 'Time', type: 'datetime'},
      ], (cv.recent_signature_logs || []).map(l => ({
        artifact_id: l.artifact_id,
        action: l.action,
        status: '<span class="badge ' + (l.status === 'valid' ? 'badge-ok' : 'badge-err') + '">' + (l.status || '?') + '</span>',
        key_id: l.key_id,
        created_at: l.created_at,
      })));
    }

    // A2A tab
    const ac = $('a2a-content');
    if (av.error) {
      ac.innerHTML = '<p class="text-red-400">Error: ' + av.error + '</p>';
    } else {
      ac.innerHTML = '<div class="grid grid-cols-3 md:grid-cols-6 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + av.total_tasks + '</div><div class="text-xs text-gray-500">Total</div></div>'
        + Object.entries(av.by_state || {}).map(([k,v]) =>
          '<div class="card text-center"><div class="text-xl font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>'
        ).join('')
        + '</div>'
        + '<h4 class="font-semibold mb-2">Recent Tasks</h4>'
        + '<div id="a2a-tasks-table"></div>';
      renderTable('a2a-tasks-table', [
        {key: 'id', label: 'ID', type: 'string'},
        {key: 'session_id', label: 'Session', type: 'string'},
        {key: 'state', label: 'State', type: 'string'},
        {key: 'updated_at', label: 'Updated', type: 'datetime'},
      ], (av.recent_tasks || []).map(t => ({
        id: '<span class="font-mono text-xs">' + (t.id || '?') + '</span>',
        session_id: t.session_id || '—',
        state: '<span class="badge ' + (t.state === 'completed' ? 'badge-ok' : t.state === 'failed' ? 'badge-err' : 'badge-budget') + '">' + (t.state || '?') + '</span>',
        updated_at: t.updated_at,
      })));
    }

    // Investigations tab
    const ic = $('inv-content');
    if (iv.error) {
      ic.innerHTML = '<p class="text-red-400">Error: ' + iv.error + '</p>';
    } else {
      ic.innerHTML = '<div class="grid grid-cols-4 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.findings + '</div><div class="text-xs text-gray-500">Findings</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.iocs + '</div><div class="text-xs text-gray-500">IOCs</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.risks + '</div><div class="text-xs text-gray-500">Risks</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.mitre_techniques + '</div><div class="text-xs text-gray-500">MITRE</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Findings by Severity</h4>'
        + '<div id="inv-table"></div>';
      const sevRows = Object.entries(iv.findings_by_severity || {}).map(([k, v]) => ({severity: k.toUpperCase(), count: v}));
      renderTable('inv-table', [
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'count', label: 'Count', type: 'number'},
      ], sevRows, {sortCol: 1, sortDir: 'desc'});
    }

    // DB Counts tab
    const dc = $('db-content');
    if (dv.error) {
      dc.innerHTML = '<p class="text-red-400">Error: ' + dv.error + '</p>';
    } else {
      dc.innerHTML = '<div id="db-table"></div>';
      const dbRows = Object.entries(dv.counts || {}).map(([t, c]) => ({table_name: t, rows: c}));
      renderTable('db-table', [
        {key: 'table_name', label: 'Table', type: 'string'},
        {key: 'rows', label: 'Rows', type: 'number'},
      ], dbRows, {sortCol: 1, sortDir: 'desc'});
    }

    // Agents tab
    const agc = $('agents-content');
    if (agv.error) {
      agc.innerHTML = '<p class="text-red-400">Error: ' + agv.error + '</p>';
    } else {
      agc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + agv.total + '</div><div class="text-xs text-gray-500">Total Agents</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-purple-400">' + agv.orchestrators + '</div><div class="text-xs text-gray-500">Orchestrators</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-blue-400">' + agv.specialists + '</div><div class="text-xs text-gray-500">Specialists</div></div>'
        + '</div>'
        + '<div id="agents-table"></div>';
      const agentRows = (agv.agents || []).map(a => ({
        name: a.name,
        description: (a.description || '').substring(0, 80),
        role: (a.claude_metadata || {}).role || 'specialist',
        model: (a.claude_metadata || {}).model || '-',
        skills: (a.skills || []).map(s => s.name).join(', '),
        url: a.url || '-',
      }));
      renderTable('agents-table', [
        {key: 'name', label: 'Agent', type: 'string'},
        {key: 'description', label: 'Description', type: 'string'},
        {key: 'role', label: 'Role', type: 'string'},
        {key: 'model', label: 'Model', type: 'string'},
        {key: 'skills', label: 'Skills', type: 'string'},
        {key: 'url', label: 'URL', type: 'string'},
      ], agentRows);
    }

    // Routing tab
    const rtc = $('routing-content');
    if (rtv.error) {
      rtc.innerHTML = '<p class="text-red-400">Error: ' + rtv.error + '</p>';
    } else {
      rtc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (rtv.strategies||[]).length + '</div><div class="text-xs text-gray-500">Strategies</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (rtv.circuit_breakers||[]).length + '</div><div class="text-xs text-gray-500">Circuit Breakers</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' + (rtv.open_circuits||0) + '</div><div class="text-xs text-gray-500">Open Circuits</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Strategies</h4>'
        + '<div id="routing-strategies-table"></div>'
        + '<h4 class="font-semibold mb-2">Circuit Breakers</h4>'
        + '<div id="routing-cb-table"></div>'
        + '<h4 class="font-semibold mt-4 mb-2">Budget Guards</h4>'
        + '<div id="routing-budgets-table"></div>';
      renderTable('routing-strategies-table', [
        {key: 'name', label: 'Strategy', type: 'string'},
      ], (rtv.strategies || []).map(s => ({name: s})));
      const cbRows = (rtv.circuit_breakers || []).map(cb => ({
        target: cb.target, state: cb.state, failures: cb.failures,
      }));
      renderTable('routing-cb-table', [
        {key: 'target', label: 'Target', type: 'string'},
        {key: 'state', label: 'State', type: 'string'},
        {key: 'failures', label: 'Failures', type: 'number'},
      ], cbRows);
      const budgetRows = Object.entries(rtv.budgets || {}).map(([k, v]) => ({
        guard: k, value: v,
      }));
      renderTable('routing-budgets-table', [
        {key: 'guard', label: 'Guard', type: 'string'},
        {key: 'value', label: 'Value', type: 'json'},
      ], budgetRows);
    }

    // Factory tab
    const fc = $('factory-content');
    if (fv.error) {
      fc.innerHTML = '<p class="text-red-400">Error: ' + fv.error + '</p>';
    } else {
      fc.innerHTML = '<div class="grid grid-cols-4 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold ' + (fv.factory_available ? 'text-green-400' : 'text-red-400') + '">' + (fv.factory_available ? '&#x2705;' : '&#x274c;') + '</div><div class="text-xs text-gray-500">Factory</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + fv.total_agents + '</div><div class="text-xs text-gray-500">Agent Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + fv.total_teams + '</div><div class="text-xs text-gray-500">Team Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (fv.plugins||[]).length + '</div><div class="text-xs text-gray-500">Templates</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Archetypes</h4>'
        + '<div class="flex gap-2 mb-4">' + (fv.archetypes||[]).map(a =>
          '<span class="badge badge-standard">' + a + '</span>'
        ).join('') + '</div>'
        + '<h4 class="font-semibold mb-2">Agent Files</h4>'
        + '<div id="factory-agents-table"></div>'
        + '<h4 class="font-semibold mt-4 mb-2">Teams</h4>'
        + '<div id="factory-teams-table"></div>';
      const agentFileRows = (fv.agents || []).map(a => ({
        name: a.name,
        size_kb: Math.round(a.size / 1024 * 10) / 10,
        lines: a.lines,
      }));
      renderTable('factory-agents-table', [
        {key: 'name', label: 'Name', type: 'string'},
        {key: 'size_kb', label: 'Size (KB)', type: 'number'},
        {key: 'lines', label: 'Lines', type: 'number'},
      ], agentFileRows);
      renderTable('factory-teams-table', [
        {key: 'name', label: 'Team', type: 'string'},
      ], (fv.teams || []).map(t => ({name: t.name})));
    }

    // Prompts tab
    const pmc = $('prompts-content');
    if (pmv.error) {
      pmc.innerHTML = '<p class="text-red-400">Error: ' + pmv.error + '</p>';
    } else {
      const promptRows = [];
      Object.entries(pmv.plugins || {}).forEach(([cat, files]) => {
        (files || []).forEach(f => promptRows.push({category: cat, file: f}));
      });
      pmc.innerHTML = '<div class="grid grid-cols-2 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.total_templates + '</div><div class="text-xs text-gray-500">Template Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.sessions + '</div><div class="text-xs text-gray-500">Sessions</div></div>'
        + '</div>'
        + '<div id="prompts-table"></div>';
      renderTable('prompts-table', [
        {key: 'category', label: 'Category', type: 'string'},
        {key: 'file', label: 'File', type: 'string'},
      ], promptRows);
    }

    // Cases tab (Phase 0)
    $('cases-total').textContent = casesv.total || 0;
    $('cases-open').textContent = casesv.open || 0;
    $('cases-closed').textContent = casesv.closed || 0;
    if (casesv.error) {
      $('cases-table').innerHTML = '<p class="text-red-400">Error: ' + casesv.error + '</p>';
    } else {
      const caseRows = (casesv.cases || []).map(c => ({
        title: (c.title || '').substring(0, 50),
        priority: c.priority === 'critical'
          ? '<span class="text-red-400 font-bold">' + (c.priority || '?').toUpperCase() + '</span>'
          : c.priority === 'high'
          ? '<span class="text-yellow-400">' + (c.priority || '?').toUpperCase() + '</span>'
          : (c.priority || '?').toUpperCase(),
        mode: '<span class="badge badge-standard">' + (c.mode || '?').toUpperCase() + '</span>',
        facts_count: c.facts_count || 0,
        iocs_count: c.iocs_count || 0,
        assets_count: c.assets_count || 0,
        mitre_count: c.mitre_count || 0,
        created_at: c.created_at,
        status: c.closed_at
          ? '<span class="badge badge-err">CLOSED</span>'
          : '<span class="badge badge-ok">OPEN</span>',
      }));
      renderTable('cases-table', [
        {key: 'title', label: 'Title', type: 'string'},
        {key: 'priority', label: 'Priority', type: 'string'},
        {key: 'mode', label: 'Mode', type: 'string'},
        {key: 'facts_count', label: 'Facts', type: 'number'},
        {key: 'iocs_count', label: 'IOCs', type: 'number'},
        {key: 'assets_count', label: 'Assets', type: 'number'},
        {key: 'mitre_count', label: 'MITRE', type: 'number'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
        {key: 'status', label: 'Status', type: 'string'},
      ], caseRows);
    }

    // Tasks tab
    $('tasks-total').textContent = tasksv.total || 0;
    $('tasks-submitted').textContent = tasksv.by_state?.submitted || 0;
    $('tasks-working').textContent = tasksv.by_state?.working || 0;
    $('tasks-completed').textContent = tasksv.by_state?.completed || 0;
    $('tasks-failed').textContent = tasksv.by_state?.failed || 0;
    if (tasksv.error) {
      $('tasks-table').innerHTML = '<p class="text-red-400">Error: ' + tasksv.error + '</p>';
    } else {
      const taskRows = (tasksv.tasks || []).map(t => ({
        id: '<span class="font-mono text-xs">' + t.id + '</span>',
        state: t.state === 'completed' ? '<span class="badge badge-ok">✓ DONE</span>'
          : t.state === 'failed' ? '<span class="badge badge-err">✗ FAIL</span>'
          : t.state === 'working' ? '<span class="badge badge-standard">⟳ WORK</span>'
          : t.state === 'submitted' ? '<span class="badge badge-budget">⊕ SBMT</span>'
          : '<span class="badge">' + (t.state || '?').toUpperCase() + '</span>',
        agent: t.agent || '?',
        created_at: t.created_at,
        updated_at: t.updated_at,
        action: (t.state === 'completed' || t.state === 'failed' || t.state === 'canceled')
          ? '—'
          : '<button onclick="cancelTask(\'' + t.id + '\')" class="text-xs px-2 py-1 bg-red-900 hover:bg-red-800 rounded">Cancel</button>',
      }));
      renderTable('tasks-table', [
        {key: 'id', label: 'Task ID', type: 'string'},
        {key: 'state', label: 'State', type: 'string'},
        {key: 'agent', label: 'Agent', type: 'string'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
        {key: 'updated_at', label: 'Updated', type: 'datetime'},
        {key: 'action', label: 'Action', type: 'string'},
      ], taskRows);
    }

    // PoCs tab
    const pocContent = $('pocs-content');
    if (pocv.error) {
      pocContent.innerHTML = '<p class="text-red-400">Error: ' + pocv.error + '</p>';
    } else {
      const byStatus = pocv.by_status || {};
      const bySeverity = pocv.by_severity || {};
      pocContent.innerHTML = '<div class="grid grid-cols-2 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (pocv.total || 0) + '</div><div class="text-xs text-gray-500">Total PoCs</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' + (pocv.weaponized || 0) + '</div><div class="text-xs text-gray-500">Weaponized</div></div>'
        + '</div>'
        + '<div class="grid grid-cols-2 gap-4 mb-4">'
        + '<div class="card"><h4 class="text-xs font-semibold mb-2 text-gray-400 uppercase tracking-wide">By Status</h4>'
        + '<div class="grid grid-cols-5 gap-2 text-center">'
        + Object.entries(byStatus).map(([k, v]) => '<div><div class="text-lg font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>').join('')
        + '</div></div>'
        + '<div class="card"><h4 class="text-xs font-semibold mb-2 text-gray-400 uppercase tracking-wide">By Severity</h4>'
        + '<div class="grid grid-cols-5 gap-2 text-center">'
        + Object.entries(bySeverity).map(([k, v]) => '<div><div class="text-lg font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>').join('')
        + '</div></div>'
        + '</div>'
        + '<div id="pocs-table"></div>';
      renderTable('pocs-table', [
        {key: 'title', label: 'Title', type: 'string'},
        {key: 'status', label: 'Status', type: 'string'},
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'is_weaponized', label: 'Weaponized', type: 'bool'},
        {key: 'reliability_score', label: 'Reliability', type: 'number'},
        {key: 'language', label: 'Language', type: 'string'},
        {key: 'source', label: 'Source', type: 'string'},
        {key: 'tags', label: 'Tags', type: 'json'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
      ], pocv.recent || []);
    }

  } catch (e) {
    console.error('Dashboard refresh error:', e);
  }
}

async function cancelTask(taskId) {
  try {
    const response = await fetch('/dashboard/api/tasks/' + taskId + '/cancel', { method: 'POST' });
    const data = await response.json();
    if (data.status === 'success') {
      alert('Task ' + taskId + ' canceled');
      refresh();
    } else {
      alert('Error: ' + (data.error || 'Unknown error'));
    }
  } catch (e) {
    alert('Failed to cancel task: ' + e);
  }
}

async function fetchApi(endpoint) {
  try {
    const response = await fetch('/dashboard' + endpoint);
    return await response.json();
  } catch (e) {
    console.error('API fetch failed for ' + endpoint, e);
    return { error: 'Failed to fetch: ' + e.message };
  }
}

// ── Explorer: generic table viewer ──────────────────────────────────────────
async function loadExplorerModels() {
  try {
    const res = await fetch('/dashboard/api/models');
    const data = await res.json();
    const sel = $('explorer-model');
    (data.models || []).forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.textContent = m;
      sel.appendChild(opt);
    });
  } catch (e) { console.error('Failed to load models', e); }
}

async function loadExplorerTable() {
  const model = $('explorer-model').value;
  if (!model) { $('explorer-table').innerHTML = ''; $('explorer-count').textContent = ''; return; }
  $('explorer-table').innerHTML = '<div class="loading text-gray-500">Loading...</div>';
  try {
    const res = await fetch('/dashboard/api/tables/' + encodeURIComponent(model) + '?limit=500');
    const data = await res.json();
    if (data.error) { $('explorer-table').innerHTML = '<div class="text-red-400">' + data.error + '</div>'; return; }
    $('explorer-count').textContent = (data.total || data.rows.length) + ' rows';
    const schema = (data.columns || []).map(c => ({
      key: c.name || c, label: c.label || c.name || c, type: c.type || 'string'
    }));
    renderTable('explorer-table', schema, data.rows || []);
  } catch (e) {
    $('explorer-table').innerHTML = '<div class="text-red-400">Error: ' + e.message + '</div>';
  }
}

loadExplorerModels();

refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>"""
