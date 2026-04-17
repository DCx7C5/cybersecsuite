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
  </div>

  <!-- Providers tab -->
  <div id="tab-providers" class="card">
    <table>
      <thead><tr><th>Provider</th><th>Status</th><th>Type</th><th>Format</th><th>Models</th><th>RPM</th><th>Cost Range</th></tr></thead>
      <tbody id="providers-body"><tr><td colspan="7" class="text-center text-gray-500 loading">Loading...</td></tr></tbody>
    </table>
  </div>

  <!-- Usage tab -->
  <div id="tab-usage" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">Recent Requests</h3>
    <table>
      <thead><tr><th>Provider</th><th>Model</th><th>Tokens</th><th>Cost</th><th>Latency</th><th>Status</th></tr></thead>
      <tbody id="usage-body"><tr><td colspan="6" class="text-center text-gray-500">No requests yet</td></tr></tbody>
    </table>
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
     <table>
       <thead><tr><th>Title</th><th>Priority</th><th>Mode</th><th>Facts</th><th>IOCs</th><th>Assets</th><th>MITRE</th><th>Created</th><th>Status</th></tr></thead>
       <tbody id="cases-body"><tr><td colspan="9" class="text-center text-gray-500 loading">Loading cases...</td></tr></tbody>
     </table>
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
     <table>
       <thead><tr><th>Task ID</th><th>State</th><th>Agent</th><th>Created</th><th>Updated</th><th>Action</th></tr></thead>
       <tbody id="tasks-body"><tr><td colspan="6" class="text-center text-gray-500 loading">Loading tasks...</td></tr></tbody>
     </table>
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

async function refresh() {
  try {
    const [ov, pv, uv, hv, cv, av, iv, dv, agv, rtv, fv, pmv, casesv, tasksv] = await Promise.all([
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
    const pbody = $('providers-body');
    pbody.innerHTML = pv.map(p => {
      const statusBadge = p.status === 'available'
        ? '<span class="badge badge-ok">ON</span>'
        : '<span class="badge badge-err">' + p.status.toUpperCase() + '</span>';
      const typeBadge = p.auth_type === 'browser'
        ? '<span class="badge badge-browser">BROWSER</span>'
        : tierBadge(p);
      const rpm = p.rate_limit.rpm_remaining !== undefined
        ? Math.round(p.rate_limit.rpm_remaining) + '/' + p.rate_limit.rpm_capacity
        : '-';
      return '<tr><td><strong>' + p.name + '</strong><br><span class="text-xs text-gray-500">' + p.id + '</span></td>'
        + '<td>' + statusBadge + '</td>'
        + '<td>' + typeBadge + '</td>'
        + '<td class="text-xs">' + p.api_format + '</td>'
        + '<td>' + p.models.length + '</td>'
        + '<td class="text-xs">' + rpm + '</td>'
        + '<td class="text-xs">' + costRange(p.models) + '/M</td></tr>';
    }).join('');

    // Usage table
    const ubody = $('usage-body');
    if (uv.recent.length) {
      ubody.innerHTML = uv.recent.map(r => {
        const badge = r.success ? '<span class="badge badge-ok">OK</span>' : '<span class="badge badge-err">FAIL</span>';
        return '<tr><td>' + r.provider + '</td><td class="text-xs">' + r.model + '</td>'
          + '<td>' + fmt(r.tokens) + '</td><td>$' + r.cost_usd.toFixed(6) + '</td>'
          + '<td>' + r.latency_ms.toFixed(0) + 'ms</td><td>' + badge + '</td></tr>';
      }).join('');
    }

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
        + '<table><thead><tr><th>Artifact</th><th>Action</th><th>Status</th><th>Key</th><th>Time</th></tr></thead><tbody>'
        + (cv.recent_signature_logs || []).map(l =>
          '<tr><td>' + l.artifact_id + '</td><td>' + l.action + '</td>'
          + '<td><span class="badge ' + (l.status === 'valid' ? 'badge-ok' : 'badge-err') + '">' + l.status + '</span></td>'
          + '<td class="text-xs">' + l.key_id + '</td>'
          + '<td class="text-xs">' + (l.created_at || '-') + '</td></tr>'
        ).join('') + '</tbody></table>';
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
        + '<table><thead><tr><th>ID</th><th>Session</th><th>State</th><th>Updated</th></tr></thead><tbody>'
        + (av.recent_tasks || []).map(t =>
          '<tr><td class="text-xs">' + t.id + '</td><td class="text-xs">' + (t.session_id || '-') + '</td>'
          + '<td><span class="badge ' + (t.state === 'completed' ? 'badge-ok' : t.state === 'failed' ? 'badge-err' : 'badge-budget') + '">' + t.state + '</span></td>'
          + '<td class="text-xs">' + (t.updated_at || '-') + '</td></tr>'
        ).join('') + '</tbody></table>';
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
        + '<div class="grid grid-cols-5 gap-2">'
        + Object.entries(iv.findings_by_severity || {}).map(([k,v]) =>
          '<div class="card text-center"><div class="font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k.toUpperCase() + '</div></div>'
        ).join('')
        + '</div>';
    }

    // DB Counts tab
    const dc = $('db-content');
    if (dv.error) {
      dc.innerHTML = '<p class="text-red-400">Error: ' + dv.error + '</p>';
    } else {
      dc.innerHTML = '<table><thead><tr><th>Table</th><th>Rows</th></tr></thead><tbody>'
        + Object.entries(dv.counts || {}).sort((a,b) => b[1] - a[1]).map(([t,c]) =>
          '<tr><td>' + t + '</td><td class="font-bold">' + fmt(c) + '</td></tr>'
        ).join('') + '</tbody></table>';
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
        + '<table><thead><tr><th>Agent</th><th>Role</th><th>Model</th><th>Skills</th><th>URL</th></tr></thead><tbody>'
        + (agv.agents || []).map(a => {
          const role = (a.claude_metadata||{}).role || 'specialist';
          const model = (a.claude_metadata||{}).model || '-';
          const roleBadge = role === 'orchestrator'
            ? '<span class="badge badge-premium">ORCH</span>'
            : '<span class="badge badge-budget">SPEC</span>';
          const skills = (a.skills||[]).map(s => s.name).join(', ');
          return '<tr><td><strong>' + a.name + '</strong><br><span class="text-xs text-gray-500">' + (a.description||'').substring(0,80) + '</span></td>'
            + '<td>' + roleBadge + '</td>'
            + '<td class="text-xs">' + model + '</td>'
            + '<td class="text-xs">' + skills + '</td>'
            + '<td class="text-xs">' + (a.url||'-') + '</td></tr>';
        }).join('') + '</tbody></table>';
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
        + '<div class="flex flex-wrap gap-2 mb-4">' + (rtv.strategies||[]).map(s =>
          '<span class="badge badge-standard">' + s + '</span>'
        ).join('') + '</div>'
        + '<h4 class="font-semibold mb-2">Circuit Breakers</h4>'
        + '<table><thead><tr><th>Target</th><th>State</th><th>Failures</th></tr></thead><tbody>'
        + (rtv.circuit_breakers||[]).map(cb =>
          '<tr><td class="text-xs">' + cb.target + '</td>'
          + '<td><span class="badge ' + (cb.state === 'closed' ? 'badge-ok' : 'badge-err') + '">' + cb.state.toUpperCase() + '</span></td>'
          + '<td>' + cb.failures + '</td></tr>'
        ).join('') + '</tbody></table>'
        + '<h4 class="font-semibold mt-4 mb-2">Budget Guards</h4>'
        + '<pre class="text-xs bg-gray-900 p-3 rounded overflow-auto">' + JSON.stringify(rtv.budgets||{}, null, 2) + '</pre>';
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
        + '<table><thead><tr><th>Name</th><th>Size</th><th>Lines</th></tr></thead><tbody>'
        + (fv.agents||[]).map(a =>
          '<tr><td>' + a.name + '</td><td class="text-xs">' + (a.size/1024).toFixed(1) + ' KB</td><td class="text-xs">' + a.lines + '</td></tr>'
        ).join('') + '</tbody></table>'
        + '<h4 class="font-semibold mt-4 mb-2">Teams</h4>'
        + '<div class="flex flex-wrap gap-2">' + (fv.teams||[]).map(t =>
          '<span class="badge badge-budget">' + t.name + '</span>'
        ).join('') + '</div>';
    }

    // Prompts tab
    const pmc = $('prompts-content');
    if (pmv.error) {
      pmc.innerHTML = '<p class="text-red-400">Error: ' + pmv.error + '</p>';
    } else {
      pmc.innerHTML = '<div class="grid grid-cols-2 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.total_templates + '</div><div class="text-xs text-gray-500">Template Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.sessions + '</div><div class="text-xs text-gray-500">Sessions</div></div>'
        + '</div>'
        + Object.entries(pmv.plugins||{}).map(([cat, files]) =>
          '<h4 class="font-semibold mt-3 mb-2">' + cat + '</h4>'
          + '<div class="flex flex-wrap gap-2">' + files.map(f =>
            '<span class="badge badge-standard">' + f + '</span>'
          ).join('') + '</div>'
        ).join('');
    }

    // Cases tab (Phase 0)
    $('cases-total').textContent = cv.total || 0;
    $('cases-open').textContent = cv.open || 0;
    $('cases-closed').textContent = cv.closed || 0;
    const cases_body = $('cases-body');
    if (cv.error) {
      cases_body.innerHTML = '<tr><td colspan="9" class="text-center text-red-400">' + cv.error + '</td></tr>';
    } else {
      cases_body.innerHTML = (cv.cases || []).map(c => {
        const status_badge = c.closed_at ? '<span class="badge badge-err">CLOSED</span>' : '<span class="badge badge-ok">OPEN</span>';
        const priority_color = c.priority === 'critical' ? 'text-red-400' : c.priority === 'high' ? 'text-yellow-400' : 'text-gray-300';
        return '<tr>'
          + '<td><strong>' + (c.title || '').substring(0, 40) + '</strong></td>'
          + '<td class="' + priority_color + '">' + (c.priority || '?').toUpperCase() + '</td>'
          + '<td><span class="badge badge-standard">' + (c.mode || '?').toUpperCase() + '</span></td>'
          + '<td>' + (c.facts_count || 0) + '</td>'
          + '<td>' + (c.iocs_count || 0) + '</td>'
          + '<td>' + (c.assets_count || 0) + '</td>'
          + '<td>' + (c.mitre_count || 0) + '</td>'
          + '<td class="text-xs">' + (c.created_at ? c.created_at.substring(0, 10) : '?') + '</td>'
          + '<td>' + status_badge + '</td>'
          + '</tr>';
      }).join('') || '<tr><td colspan="9" class="text-center text-gray-500">No cases found</td></tr>';
    }

    // Tasks tab
    $('tasks-total').textContent = tv.total || 0;
    $('tasks-submitted').textContent = tv.by_state?.submitted || 0;
    $('tasks-working').textContent = tv.by_state?.working || 0;
    $('tasks-completed').textContent = tv.by_state?.completed || 0;
    $('tasks-failed').textContent = tv.by_state?.failed || 0;
    const tasks_body = $('tasks-body');
    if (tv.error) {
      tasks_body.innerHTML = '<tr><td colspan="6" class="text-center text-red-400">' + tv.error + '</td></tr>';
    } else {
      tasks_body.innerHTML = (tv.tasks || []).map(t => {
        const state_badge = t.state === 'completed' ? '<span class="badge badge-ok">✓ DONE</span>'
          : t.state === 'failed' ? '<span class="badge badge-err">✗ FAIL</span>'
          : t.state === 'working' ? '<span class="badge badge-standard">⟳ WORK</span>'
          : t.state === 'submitted' ? '<span class="badge badge-budget">⊕ SBMT</span>'
          : '<span class="badge">' + t.state.toUpperCase() + '</span>';
        const cancel_btn = (t.state === 'completed' || t.state === 'failed' || t.state === 'canceled')
          ? '-'
          : '<button onclick="cancelTask(' + t.id + ')" class="text-xs px-2 py-1 bg-red-900 hover:bg-red-800 rounded">Cancel</button>';
        return '<tr>'
          + '<td class="font-mono text-xs">' + t.id + '</td>'
          + '<td>' + state_badge + '</td>'
          + '<td class="text-xs">' + (t.agent || '?') + '</td>'
          + '<td class="text-xs">' + (t.created_at ? t.created_at.substring(0, 10) : '?') + '</td>'
          + '<td class="text-xs">' + (t.updated_at ? t.updated_at.substring(0, 10) : '?') + '</td>'
          + '<td>' + cancel_btn + '</td>'
          + '</tr>';
      }).join('') || '<tr><td colspan="6" class="text-center text-gray-500">No tasks found</td></tr>';
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

refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>"""



