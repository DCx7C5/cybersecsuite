"""All dashboard JavaScript: core utils, refresh, agent query, explorer."""

_JS = r"""
const $ = id => document.getElementById(id);
let currentTab = 'health';
// per-tab context stats cache: { tabName: [{label, value}, ...] }
const _ctxCache = {};

function _setCtxStat(el, label, value) {
  if (!el) return;
  el.innerHTML = '<strong>' + value + '</strong>' + label;
  el.style.display = '';
}

function _clearCtx() {
  for (let i = 1; i <= 5; i++) {
    const el = $('ctx-s' + i);
    if (el) { el.innerHTML = ''; el.style.display = 'none'; }
  }
}

function _showCtxStats(stats) {
  // stats: [{label, value}, ...]
  const bar = $('context-bar');
  if (!bar) return;
  _clearCtx();
  if (!stats || !stats.length) { bar.style.display = 'none'; return; }
  stats.slice(0, 5).forEach((s, i) => _setCtxStat($('ctx-s' + (i+1)), s.label, s.value));
  bar.style.display = 'flex';
}

async function _updateContextBar(name) {
  if (_ctxCache[name]) { _showCtxStats(_ctxCache[name]); return; }
  const tab_stats = {
    'health':    () => fetch('/api/overview').then(r=>r.json()).then(d=>[
      {value: d.uptime_seconds ? Math.round(d.uptime_seconds)+'s' : '—', label: ' uptime'},
      {value: d.providers?.enabled ?? '—', label: ' providers on'},
      {value: d.models?.total ?? '—', label: ' models'},
    ]),
    'usage':     () => fetch('/api/overview').then(r=>r.json()).then(d=>[
      {value: fmt(d.usage?.total_requests ?? 0), label: ' requests'},
      {value: fmt(d.usage?.total_tokens ?? 0), label: ' tokens'},
      {value: '$'+(d.usage?.total_cost_usd??0).toFixed(4), label: ' cost'},
    ]),
    'routing':   () => fetch('/api/routing').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.strategy ?? '—', label: ' strategy'},
      {value: d.providers_available ?? '—', label: ' providers'},
    ]),
    'findings':  () => fetch('/api/findings').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' total'},
      {value: d.critical ?? 0, label: ' critical'},
      {value: d.high ?? 0, label: ' high'},
      {value: d.last_24h ?? 0, label: ' last 24h'},
    ]),
    'iocs':      () => fetch('/api/iocs').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' total'},
      {value: d.active ?? 0, label: ' active'},
      {value: d.high_confidence ?? 0, label: ' high conf'},
    ]),
    'cases':     () => fetch('/api/cases').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' cases'},
      {value: d.open ?? 0, label: ' open'},
      {value: d.closed ?? 0, label: ' closed'},
    ]),
    'tasks':     () => fetch('/api/tasks').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' tasks'},
      {value: d.working ?? 0, label: ' running'},
      {value: d.completed ?? 0, label: ' done'},
    ]),
    'agent-factory': () => fetch('/api/agents').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.agents?.length ?? 0, label: ' agents'},
      {value: d.agents?.filter(a=>a.role==='orchestrator').length ?? 0, label: ' orchestrators'},
    ]),
    'agent-crafter': () => fetch('/api/team-agents').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' agents'},
    ]),
    'intel': () => fetch('/api/intelligence').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.mitre_techniques ?? 0, label: ' MITRE'},
      {value: d.cves ?? 0, label: ' CVEs'},
      {value: d.cwes ?? 0, label: ' CWEs'},
    ]),
    'compliance': () => fetch('/api/compliance').then(r=>r.json()).catch(()=>({})).then(d=>[
      {value: d.total ?? 0, label: ' rules'},
      {value: d.critical ?? 0, label: ' critical'},
      {value: d.frameworks ?? 0, label: ' frameworks'},
    ]),
  };
  const fn = tab_stats[name];
  if (!fn) { _showCtxStats([]); return; }
  try {
    const stats = await fn();
    _ctxCache[name] = stats;
    _showCtxStats(stats);
  } catch { _showCtxStats([]); }
}

function showTab(name) {
  document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  const panel = $('tab-' + name);
  if (panel) { panel.style.display = ''; panel.classList.add('panel-enter'); }
  const navItem = $('nav-' + name);
  if (navItem) navItem.classList.add('active');
  const crumb = document.querySelector('#topbar-title');
  if (crumb && navItem) crumb.textContent = '▶ ' + navItem.textContent.trim().toUpperCase();
  currentTab = name;
  _updateStatusBar(name);
  _updateContextBar(name);
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
    if (val === null || val === undefined) return '<span style="color:var(--text-faint)">—</span>';
    const t = col.type || 'string';
    if (t === 'datetime' && val) {
      try { return new Date(val).toLocaleString(); } catch { return String(val); }
    }
    if (t === 'bool') return val ? '<span class="badge badge-ok">YES</span>' : '<span class="badge badge-err">NO</span>';
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

    let h = '<div class="rt-bar">';
    h += '<input type="text" class="rt-search" placeholder="Search…" value="' + filter.replace(/"/g,'&quot;') + '" '
       + 'oninput="window._rt_' + containerId + '_filter(this.value)">';
    h += '<span class="rt-count">' + data.length + ' rows</span>';
    h += '</div>';
    h += '<table><thead><tr>';
    schema.forEach((c, i) => {
      const arrow = sortCol === i ? (sortDir === 'asc' ? ' ▲' : ' ▼') : '';
      h += '<th onclick="window._rt_' + containerId + '_sort(' + i + ')">' + (c.label || c.key) + arrow + '</th>';
    });
    h += '</tr></thead><tbody>';
    if (!sliced.length) {
      h += '<tr><td colspan="' + schema.length + '" style="text-align:center;color:var(--text-muted);padding:24px">No data</td></tr>';
    } else {
      sliced.forEach(r => {
        h += '<tr>';
        schema.forEach(c => { h += '<td>' + formatCell(r[c.key], c) + '</td>'; });
        h += '</tr>';
      });
    }
    h += '</tbody></table>';
    if (totalPages > 1) {
      h += '<div class="rt-pager">';
      h += '<button class="rt-btn" onclick="window._rt_' + containerId + '_page(-1)"' + (page === 0 ? ' disabled' : '') + '>&laquo; Prev</button>';
      h += '<span class="rt-count">Page ' + (page+1) + ' / ' + totalPages + '</span>';
      h += '<button class="rt-btn" onclick="window._rt_' + containerId + '_page(1)"' + (page >= totalPages-1 ? ' disabled' : '') + '>Next &raquo;</button>';
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
    const [ov, uv, cv, av, iv, dv, agv, rtv, pmv, pocv,
           findingsv, iocsv, yarav, netv, intv, auditv, compv] = await Promise.all([
      fetch('/api/overview').then(r => r.json()),
      fetch('/api/usage').then(r => r.json()),
      fetch('/api/crypto').then(r => r.json()),
      fetch('/api/a2a').then(r => r.json()),
      fetch('/api/investigations').then(r => r.json()),
      fetch('/api/db-counts').then(r => r.json()),
      fetch('/api/agents').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/routing').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/prompts').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/pocs').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/findings').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/iocs').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/yara').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/network').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/intelligence').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/audit').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/api/compliance').then(r => r.json()).catch(() => ({error:'unavailable'})),
    ]);

    if ($('uptime') && ov.uptime_seconds !== undefined)
      $('uptime').textContent = Math.round(ov.uptime_seconds) + 's uptime';

    // Invalidate context cache so next showTab fetches fresh data
    Object.keys(_ctxCache).forEach(k => delete _ctxCache[k]);
    _updateContextBar(currentTab);

    // Remove loading
    document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));
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

    // Health → rendered by SSE (_renderHealth)

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
      // Populate agent-query context table selector
      _aqPopulateContextTables(Object.keys(dv.counts || {}));
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
        description: (a.description || '').substring(0, 90),
        role: (a.claude_metadata || {}).role || 'specialist',
        model: (a.claude_metadata || {}).model || '-',
        tools: (a.tools || []).length ? (a.tools || []).slice(0, 6).join(', ') + (a.tools.length > 6 ? ' …' : '') : '—',
        file: a.file || '-',
      }));
      renderTable('agents-table', [
        {key: 'name', label: 'Agent', type: 'string'},
        {key: 'description', label: 'Description', type: 'string'},
        {key: 'role', label: 'Role', type: 'string'},
        {key: 'model', label: 'Model', type: 'string'},
        {key: 'tools', label: 'Tools', type: 'string'},
        {key: 'file', label: 'File', type: 'string'},
      ], agentRows);
      // Populate agent-query selector
      _aqPopulateAgents(agv.agents || []);
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

    // Cases → rendered by SSE (_renderCases)

    // Tasks → rendered by SSE (_renderTasks)

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

    // Findings tab
    if (!findingsv.error) {
      $('findings-total').textContent = findingsv.total || 0;
      $('findings-critical').textContent = (findingsv.by_severity || {}).critical || 0;
      $('findings-high').textContent = (findingsv.by_severity || {}).high || 0;
      $('findings-24h').textContent = (findingsv.trend || {}).last_24h || 0;
      const sevBadge = s => {
        const m = {critical:'badge-err', high:'badge-err', medium:'badge-standard', low:'badge-budget', info:'badge-ok'};
        return '<span class="badge ' + (m[s] || '') + '">' + (s || '?').toUpperCase() + '</span>';
      };
      const stBadge = s => '<span class="badge ' + (s === 'open' ? 'badge-err' : s === 'resolved' ? 'badge-ok' : 'badge-standard') + '">' + (s || '?').toUpperCase() + '</span>';
      renderTable('findings-table', [
        {key: 'title', label: 'Title', type: 'string'},
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'status', label: 'Status', type: 'string'},
        {key: 'confidence', label: 'Confidence', type: 'string'},
        {key: 'location', label: 'Location', type: 'string'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
      ], (findingsv.recent || []).map(f => ({
        ...f,
        severity: sevBadge(f.severity),
        status: stBadge(f.status),
      })));
    }

    // IOCs tab
    if (!iocsv.error) {
      $('iocs-total').textContent = iocsv.total || 0;
      $('iocs-active').textContent = (iocsv.by_status || {}).active || 0;
      $('iocs-high-conf').textContent = (iocsv.by_confidence || {}).high || 0;
      $('iocs-types').textContent = Object.keys(iocsv.by_type || {}).length;
      const confBadge = c => '<span class="badge ' + (c === 'high' ? 'badge-err' : c === 'medium' ? 'badge-standard' : 'badge-budget') + '">' + (c || '?').toUpperCase() + '</span>';
      renderTable('iocs-table', [
        {key: 'ioc_type', label: 'Type', type: 'string'},
        {key: 'value', label: 'Value', type: 'string'},
        {key: 'confidence', label: 'Confidence', type: 'string'},
        {key: 'status', label: 'Status', type: 'string'},
        {key: 'sightings', label: 'Sightings', type: 'number'},
        {key: 'source', label: 'Source', type: 'string'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
      ], (iocsv.recent || []).map(i => ({
        ...i,
        confidence: confBadge(i.confidence),
        status: '<span class="badge ' + (i.status === 'active' ? 'badge-err' : 'badge-ok') + '">' + (i.status || '?').toUpperCase() + '</span>',
      })));
    }

    // YARA tab
    if (!yarav.error) {
      const yTotal = yarav.total || 0;
      const yActive = (yarav.by_status || {}).active || 0;
      const yDet = (yarav.recent || []).reduce((s, r) => s + (r.detection_count || 0), 0);
      const ySrc = Object.keys(yarav.by_source || {}).length;
      $('yara-total').textContent = yTotal;
      $('yara-active').textContent = yActive;
      $('yara-detections').textContent = yDet;
      $('yara-sources').textContent = ySrc;
      renderTable('yara-table', [
        {key: 'name', label: 'Rule Name', type: 'string'},
        {key: 'status', label: 'Status', type: 'string'},
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'source', label: 'Source', type: 'string'},
        {key: 'detection_count', label: 'Detections', type: 'number'},
        {key: 'false_positive_rate', label: 'FP Rate', type: 'number'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
      ], (yarav.recent || []).map(y => ({
        ...y,
        status: '<span class="badge ' + (y.status === 'active' ? 'badge-ok' : 'badge-standard') + '">' + (y.status || '?').toUpperCase() + '</span>',
      })));
    }

    // Network tab
    if (!netv.error) {
      $('net-hosts').textContent = (netv.hosts || {}).total || 0;
      $('net-compromised').textContent = (netv.hosts || {}).compromised || 0;
      $('net-ips').textContent = (netv.ip_addresses || {}).total || 0;
      $('net-countries').textContent = (netv.top_countries || []).length;
      renderTable('network-hosts-table', [
        {key: 'hostname', label: 'Hostname', type: 'string'},
        {key: 'os_name', label: 'OS', type: 'string'},
        {key: 'is_compromised', label: 'Compromised', type: 'bool'},
        {key: 'is_target', label: 'Target', type: 'bool'},
      ], netv.recent_hosts || []);
      renderTable('network-ips-table', [
        {key: 'address', label: 'IP Address', type: 'string'},
        {key: 'version', label: 'Ver', type: 'number'},
        {key: 'is_private', label: 'Private', type: 'bool'},
        {key: 'geo_country', label: 'Country', type: 'string'},
        {key: 'last_seen_at', label: 'Last Seen', type: 'datetime'},
      ], netv.recent_ips || []);
    }

    // Intel tab
    if (!intv.error) {
      $('intel-techniques').textContent = (intv.mitre || {}).techniques || 0;
      $('intel-cve').textContent = (intv.cve || {}).total || 0;
      $('intel-cwe').textContent = (intv.cwe || {}).total || 0;
      $('intel-capec').textContent = (intv.capec || {}).total || 0;
      renderTable('intel-mitre-table', [
        {key: 'technique_id', label: 'ID', type: 'string'},
        {key: 'name', label: 'Name', type: 'string'},
        {key: 'tactics', label: 'Tactics', type: 'json'},
        {key: 'platforms', label: 'Platforms', type: 'json'},
        {key: 'is_sub_technique', label: 'Sub-tech', type: 'bool'},
      ], intv.recent_mitre || []);
      const cveSevBadge = s => {
        const m = {CRITICAL:'badge-err', HIGH:'badge-err', MEDIUM:'badge-standard', LOW:'badge-budget'};
        return '<span class="badge ' + (m[s] || '') + '">' + (s || '?') + '</span>';
      };
      renderTable('intel-cve-table', [
        {key: 'cve_id', label: 'CVE ID', type: 'string'},
        {key: 'cvss_score', label: 'CVSS', type: 'number'},
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'exploit_available', label: 'Exploit', type: 'bool'},
      ], (intv.recent_cve || []).map(c => ({
        ...c,
        severity: cveSevBadge(c.severity),
      })));
    }

    // Audit tab
    if (!auditv.error) {
      $('audit-total').textContent = auditv.total || 0;
      $('audit-last-hour').textContent = auditv.last_hour_count || 0;
      $('audit-agents').textContent = Object.keys(auditv.by_agent || {}).length;
      renderTable('audit-table', [
        {key: 'action', label: 'Action', type: 'string'},
        {key: 'entity_type', label: 'Entity Type', type: 'string'},
        {key: 'entity_id', label: 'Entity ID', type: 'string'},
        {key: 'agent', label: 'Agent', type: 'string'},
        {key: 'resource', label: 'Resource', type: 'string'},
        {key: 'ip_address', label: 'IP', type: 'string'},
        {key: 'created_at', label: 'Timestamp', type: 'datetime'},
      ], auditv.recent || []);
    }

    // Compliance tab
    if (!compv.error) {
      $('comp-total').textContent = compv.total || 0;
      $('comp-critical').textContent = (compv.by_severity || {}).critical || 0;
      $('comp-frameworks').textContent = Object.keys(compv.by_framework || {}).length;
      $('comp-high').textContent = (compv.by_severity || {}).high || 0;
      renderTable('compliance-table', [
        {key: 'rule_id', label: 'Rule ID', type: 'string'},
        {key: 'title', label: 'Title', type: 'string'},
        {key: 'framework', label: 'Framework', type: 'string'},
        {key: 'severity', label: 'Severity', type: 'string'},
        {key: 'audit_frequency', label: 'Frequency', type: 'string'},
        {key: 'retention_period_days', label: 'Retention (d)', type: 'number'},
        {key: 'created_at', label: 'Created', type: 'datetime'},
      ], compv.recent || []);
    }

  } catch (e) {
    console.error('Dashboard refresh error:', e);
  }
}

async function cancelTask(taskId) {
  try {
    const response = await fetch('/api/tasks/' + taskId + '/cancel', { method: 'POST' });
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
    const response = await fetch(endpoint);
    return await response.json();
  } catch (e) {
    console.error('API fetch failed for ' + endpoint, e);
    return { error: 'Failed to fetch: ' + e.message };
  }
}

// ── Agent Query panel ────────────────────────────────────────────────────────
let _aqHistory = [];
let _aqAgents = [];

function _aqPopulateAgents(agents) {
  const seen = new Set();
  _aqAgents = (agents || []).filter(a => {
    const name = String(a.name || '').trim();
    if (!name) return false;
    const key = name.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).sort((a, b) => {
    const aMeta = a.claude_metadata || {};
    const bMeta = b.claude_metadata || {};
    const aScore = (aMeta.default ? 100 : 0) + (aMeta.role === 'orchestrator' ? 10 : 0);
    const bScore = (bMeta.default ? 100 : 0) + (bMeta.role === 'orchestrator' ? 10 : 0);
    if (aScore !== bScore) return bScore - aScore;
    return String(a.name || '').localeCompare(String(b.name || ''));
  });
  _aqPopulateAgentFilters(_aqAgents);
  _aqApplyAgentFilters();
}

function _aqMeta(agent) {
  const meta = agent.claude_metadata || {};
  return {
    role: meta.role || 'specialist',
    source: meta.source_label || 'Unknown',
    model: meta.model || 'unknown',
    isDefault: !!meta.default,
  };
}

function _aqFillFilterSelect(id, values, placeholder) {
  const sel = $(id);
  const current = sel.value;
  sel.innerHTML = '';
  const base = document.createElement('option');
  base.value = '';
  base.textContent = placeholder;
  sel.appendChild(base);
  values.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    sel.appendChild(opt);
  });
  if (current && values.includes(current)) sel.value = current;
}

function _aqPopulateAgentFilters(agents) {
  const roles = [...new Set(agents.map(a => _aqMeta(a).role).filter(Boolean))].sort();
  const sources = [...new Set(agents.map(a => _aqMeta(a).source).filter(Boolean))].sort();
  const models = [...new Set(agents.map(a => _aqMeta(a).model).filter(Boolean))].sort();
  _aqFillFilterSelect('aq-role', roles, 'All roles');
  _aqFillFilterSelect('aq-source', sources, 'All sources');
  _aqFillFilterSelect('aq-model', models, 'All models');
}

function _aqApplyAgentFilters() {
  const sel = $('aq-agent');
  const current = sel.value;
  const q = ($('aq-agent-search').value || '').trim().toLowerCase();
  const source = $('aq-source').value || '';
  const role = $('aq-role').value || '';
  const model = $('aq-model').value || '';
  const filtered = _aqAgents.filter(a => {
    const meta = _aqMeta(a);
    const haystack = [
      a.name || '',
      a.description || '',
      meta.role,
      meta.source,
      meta.model,
      (a.skills || []).map(s => s.name || '').join(' '),
    ].join(' ').toLowerCase();
    return (!q || haystack.includes(q))
      && (!source || meta.source === source)
      && (!role || meta.role === role)
      && (!model || meta.model === model);
  });

  sel.innerHTML = '';
  if (!filtered.length) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No agents match current filters';
    sel.appendChild(opt);
    $('aq-agent-help').textContent = '0 of ' + _aqAgents.length + ' agents match the current filters.';
    return;
  }

  filtered.forEach(a => {
    const meta = _aqMeta(a);
    const opt = document.createElement('option');
    opt.value = a.name;
    opt.textContent = a.name
      + (meta.role === 'orchestrator' ? ' (orch)' : '')
      + ' · ' + meta.source
      + ' · ' + meta.model;
    sel.appendChild(opt);
  });

  if (current && filtered.some(a => a.name === current)) {
    sel.value = current;
  } else {
    const preferred = filtered.find(a => _aqMeta(a).isDefault) || filtered[0];
    sel.value = preferred.name;
  }
  $('aq-agent-help').textContent = filtered.length + ' of ' + _aqAgents.length
    + ' agents shown. Filter by source, role, or model before running a query.';
}

function _aqPopulateContextTables(models) {
  const sel = $('aq-context-table');
  while (sel.options.length > 1) sel.remove(1);
  (models || []).forEach(m => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    sel.appendChild(opt);
  });
}

async function runAgentQuery() {
  const agent = $('aq-agent').value || 'cybersec-agent';
  const prompt = ($('aq-prompt').value || '').trim();
  if (!prompt) { $('aq-status').textContent = '⚠ Prompt is empty'; return; }
  if (!agent) { $('aq-status').textContent = '⚠ No agent matches the current filters'; return; }

  const contextTable = $('aq-context-table').value || null;
  const rowIds = ($('aq-row-ids').value || '').split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));

  const btn = $('aq-submit');
  const status = $('aq-status');
  btn.disabled = true;
  btn.textContent = '⏳ Running…';
  status.textContent = 'Sending to agent "' + agent + '"…';

  const t0 = Date.now();
  try {
    const body = { agent, prompt };
    if (contextTable) body.context_table = contextTable;
    if (rowIds.length) body.row_ids = rowIds;

    const res = await fetch('/api/agent-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    const elapsed = Date.now() - t0;

    if (data.status === 'error') {
      status.textContent = '✗ Error: ' + data.error;
    } else {
      status.textContent = '✓ Done in ' + (data.elapsed_ms ?? elapsed) + 'ms';
      _aqHistory.unshift({ agent: data.agent || agent, prompt, response: data.response || '', ts: new Date().toLocaleTimeString(), elapsed_ms: data.elapsed_ms ?? elapsed });
      $('aq-prompt').value = '';
      _aqRenderHistory();
    }
  } catch (e) {
    status.textContent = '✗ ' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = '▶ Run Query';
  }
}

function _aqRenderHistory() {
  const el = $('aq-history');
  if (!_aqHistory.length) { el.innerHTML = '<p class="text-xs text-gray-600">No queries yet.</p>'; return; }
  el.innerHTML = _aqHistory.map((h, i) => {
    const resp = (h.response || '').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    return '<div class="border border-gray-700 rounded-lg p-4 bg-gray-900">'
      + '<div class="flex justify-between items-start mb-2">'
      + '<span class="text-xs font-semibold text-cyan-400">' + h.agent + '</span>'
      + '<span class="text-xs text-gray-600">' + h.ts + ' · ' + h.elapsed_ms + 'ms</span>'
      + '</div>'
      + '<div class="text-xs text-gray-300 font-mono mb-3 whitespace-pre-wrap border-l-2 border-cyan-800 pl-3">' + (h.prompt.replace(/</g,'&lt;')) + '</div>'
      + '<div class="text-sm text-gray-100 font-mono whitespace-pre-wrap leading-relaxed">' + resp + '</div>'
      + '</div>';
  }).join('');
}

function clearAgentHistory() {
  _aqHistory = [];
  _aqRenderHistory();
  $('aq-status').textContent = '';
}

// ── Settings: viewer/editor for .claude/settings.json ───────────────────────
let _settingsData = null;

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    _settingsData = await res.json();
    _renderSettingsAgent();
    _renderSettingsEnv();
    _renderSettingsHooks();
  } catch (e) { console.error('Failed to load settings', e); }
}

function _inp(id, val, placeholder) {
  return '<input id="' + id + '" type="text" value="' + String(val).replace(/"/g,'&quot;') + '"'
    + ' placeholder="' + (placeholder||'').replace(/"/g,'&quot;') + '"'
    + ' class="flex-1 px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none font-mono">';
}

function _renderSettingsAgent() {
  const s = _settingsData && _settingsData.settings || {};
  const p = s.proxy || {};
  let h = '';
  h += '<div class="flex items-center gap-3">'
    + '<span class="text-xs text-gray-400 w-40 shrink-0">agent</span>'
    + _inp('st-agent', s.agent || '', 'e.g. cybersec-agent')
    + '</div>';
  h += '<div class="flex items-center gap-3">'
    + '<span class="text-xs text-gray-400 w-40 shrink-0">proxy.default_strategy</span>'
    + _inp('st-proxy-strategy', p.default_strategy || '', 'e.g. cost-optimized')
    + '</div>';
  h += '<div class="flex items-center gap-3">'
    + '<span class="text-xs text-gray-400 w-40 shrink-0">proxy.enabled</span>'
    + '<select id="st-proxy-enabled" class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg">'
    + '<option value="true"' + (p.enabled !== false ? ' selected' : '') + '>true</option>'
    + '<option value="false"' + (p.enabled === false ? ' selected' : '') + '>false</option>'
    + '</select></div>';
  $('settings-agent-form').innerHTML = h;
}

function _renderSettingsEnv() {
  const env = (_settingsData && _settingsData.settings && _settingsData.settings.env) || {};
  const rows = Object.entries(env);
  let h = '';
  rows.forEach(([k, v], i) => {
    h += '<div class="flex items-center gap-2" id="env-row-' + i + '">'
      + '<input class="env-key flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" value="' + k.replace(/"/g,'&quot;') + '">'
      + '<input class="env-val flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" value="' + String(v).replace(/"/g,'&quot;') + '">'
      + '<button onclick="this.closest(\'[id^=env-row]\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>'
      + '</div>';
  });
  $('settings-env-rows').innerHTML = h;
}

function settingsAddEnvRow() {
  const wrap = $('settings-env-rows');
  const idx = wrap.children.length;
  const div = document.createElement('div');
  div.id = 'env-row-' + idx;
  div.className = 'flex items-center gap-2';
  div.innerHTML = '<input class="env-key flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" placeholder="KEY">'
    + '<input class="env-val flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" placeholder="VALUE">'
    + '<button onclick="this.closest(\'[id^=env-row]\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>';
  wrap.appendChild(div);
}

function _renderSettingsHooks() {
  const hooks = (_settingsData && _settingsData.settings && _settingsData.settings.hooks) || {};
  const rows = Object.entries(hooks).map(([event, entries]) => {
    const cmds = (entries || []).flatMap(e => (e.hooks || []).map(h => h.command || '')).join('\n');
    return {event, commands: cmds};
  });
  renderTable('settings-hooks-table', [
    {key: 'event', label: 'Event', type: 'string'},
    {key: 'commands', label: 'Commands', type: 'string'},
  ], rows);
}

async function saveSettingsAgent() {
  const status = $('settings-agent-status');
  try {
    const agent = $('st-agent').value.trim();
    const strategy = $('st-proxy-strategy').value.trim();
    const enabled = $('st-proxy-enabled').value === 'true';
    const current = (_settingsData && _settingsData.settings && _settingsData.settings.proxy) || {};
    const res = await fetch('/api/settings', {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({agent, proxy: {...current, default_strategy: strategy, enabled}}),
    });
    const data = await res.json();
    if (data.error) { status.textContent = '✗ ' + data.error; status.style.color = '#f87171'; }
    else { status.textContent = '✓ Saved'; status.style.color = '#34d399'; setTimeout(() => { status.textContent = ''; }, 3000); }
    await loadSettings();
  } catch (e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

async function saveSettingsEnv() {
  const status = $('settings-env-status');
  try {
    const env = {};
    document.querySelectorAll('[id^="env-row-"]').forEach(row => {
      const k = row.querySelector('.env-key').value.trim();
      const v = row.querySelector('.env-val').value;
      if (k) env[k] = v;
    });
    const res = await fetch('/api/settings', {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({env}),
    });
    const data = await res.json();
    if (data.error) { status.textContent = '✗ ' + data.error; status.style.color = '#f87171'; }
    else { status.textContent = '✓ Saved'; status.style.color = '#34d399'; setTimeout(() => { status.textContent = ''; }, 3000); }
    await loadSettings();
  } catch (e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

// ── Settings Scope Switcher ───────────────────────────────────────────────────
function switchSettingsScope(scope) {
  const isGlobal = scope === 'global';
  $('settings-scope-global').style.display = isGlobal ? '' : 'none';
  $('settings-scope-project').style.display = isGlobal ? 'none' : '';
  $('scope-btn-global').className = 'btn ' + (isGlobal ? 'btn-accent' : 'btn-ghost');
  $('scope-btn-project').className = 'btn ' + (isGlobal ? 'btn-ghost' : 'btn-accent');
  $('scope-btn-global').style.fontSize = '12px';
  $('scope-btn-project').style.fontSize = '12px';
}

// ── Settings Toggles (MCPs, Skills, Plugins, Global) ────────────────────────
async function loadSettingsToggles() {
  try {
    const [mcpRes, skillRes, pluginRes, globalRes, globalMcpRes, globalEnvRes, projectEnvRes] = await Promise.all([
      fetch('/api/settings/mcps').then(r => r.json()).catch(() => ({servers:[]})),
      fetch('/api/settings/skills').then(r => r.json()).catch(() => ({domains:[]})),
      fetch('/api/settings/plugins').then(r => r.json()).catch(() => ({plugins:[]})),
      fetch('/api/settings/global').then(r => r.json()).catch(() => ({global:{}})),
      fetch('/api/settings/global-mcps').then(r => r.json()).catch(() => ({servers:[]})),
      fetch('/api/settings/global-env').then(r => r.json()).catch(() => ({env:{}})),
      fetch('/api/settings/project-env').then(r => r.json()).catch(() => ({env:{}})),
    ]);
    _renderMcpToggles(mcpRes.servers || []);
    _renderSkillToggles(skillRes.domains || []);
    _renderPluginToggles(pluginRes.plugins || []);
    _renderGlobalSummary(globalRes.global || {});
    _renderGlobalMcpToggles(globalMcpRes.servers || []);
    _renderEnvTable('settings-global-env', globalEnvRes.env || {});
    _renderEnvTable('settings-project-env', projectEnvRes.env || {});
    loadGlobalHooks();
  } catch(e) { console.error('loadSettingsToggles:', e); }
}

function _toggleSwitch(id, checked, onchange) {
  return '<label class="toggle-switch" title="' + id + '">'
    + '<input type="checkbox" ' + (checked ? 'checked' : '') + ' onchange="' + onchange + '">'
    + '<span class="toggle-slider"></span>'
    + '</label>';
}

function _renderMcpToggles(servers) {
  const el = $('settings-mcps');
  if (!el) return;
  if (!servers.length) { el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No MCP servers found in mcp.json</span>'; return; }
  el.innerHTML = servers.map(s =>
    '<div class="toggle-row">'
    + '<div><div class="toggle-label">' + s.name + '</div>'
    + '<div class="toggle-sub">' + (s.command || '') + '</div></div>'
    + _toggleSwitch('mcp-' + s.name, s.enabled, 'toggleMcp("' + s.name + '",this.checked)')
    + '</div>'
  ).join('');
}

async function toggleMcp(name, enabled) {
  try {
    const res = await fetch('/api/settings/mcps', {
      method: 'PATCH',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, enabled}),
    });
    const d = await res.json();
    if (d.error) console.error('toggleMcp:', d.error);
  } catch(e) { console.error('toggleMcp:', e); }
}

function _renderGlobalMcpToggles(servers) {
  const el = $('settings-global-mcps');
  if (!el) return;
  if (!servers.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No MCP servers in ~/.claude/settings.json</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = servers.map(s =>
    '<div class="toggle-row">'
    + '<div style="flex:1"><div class="toggle-label">' + s.name + '</div>'
    + '<div class="toggle-sub">' + (s.command || '') + '</div></div>'
    + _toggleSwitch('gmcp-' + s.name, s.enabled, 'toggleGlobalMcp("' + s.name + '",this.checked)')
    + '<button class="btn btn-ghost" style="font-size:10px;padding:2px 8px;margin-left:8px" '
      + 'onclick="removeMcp(\'' + s.name + '\')" title="Remove from ~/.claude/settings.json">&#x2715;</button>'
    + '</div>'
  ).join('');
}

async function toggleGlobalMcp(name, enabled) {
  try {
    const d = await fetch('/api/settings/global-mcps', {
      method: 'PATCH',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, enabled}),
    }).then(r => r.json());
    if (d.error) console.error('toggleGlobalMcp:', d.error);
  } catch(e) { console.error('toggleGlobalMcp:', e); }
}

function _renderEnvTable(elId, env) {
  const el = $(elId);
  if (!el) return;
  const entries = Object.entries(env);
  if (!entries.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No env vars set</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = '<div class="space-y-1">'
    + entries.map(([k, v]) =>
      '<div style="display:flex;align-items:flex-start;gap:12px;padding:4px 0;border-bottom:1px solid var(--border)">'
      + '<span class="text-xs font-mono" style="color:var(--cyan);min-width:280px;flex-shrink:0">' + k + '</span>'
      + '<span class="text-xs font-mono" style="color:var(--text-muted);word-break:break-all">' + v + '</span>'
      + '</div>'
    ).join('')
    + '</div>';
}

function _renderSkillToggles(domains) {
  const el = $('settings-skills');
  if (!el) return;
  if (!domains.length) { el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No skill domains found</span>'; return; }
  el.classList.remove('toggles-loading');
  el.innerHTML = domains.map(d =>
    '<div class="toggle-row">'
    + '<div><div class="toggle-label">' + d.name + '</div>'
    + '<div class="toggle-sub">' + d.skills + ' skills</div></div>'
    + _toggleSwitch('skill-' + d.name, d.enabled, 'toggleSkillDomain("' + d.name + '",this.checked)')
    + '</div>'
  ).join('');
}

async function toggleSkillDomain(name, enabled) {
  try {
    await fetch('/api/settings/skills', {
      method: 'PATCH',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, enabled}),
    });
  } catch(e) { console.error('toggleSkillDomain:', e); }
}

function _renderPluginToggles(plugins) {
  const el = $('settings-plugins');
  if (!el) return;
  if (!plugins.length) { el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No plugins installed</span>'; return; }
  el.innerHTML = plugins.map(p =>
    '<div class="toggle-row">'
    + '<div><div class="toggle-label">' + p.id.split('@')[0] + '</div>'
    + '<div class="toggle-sub">v' + p.version + ' · ' + p.scope + '</div></div>'
    + _toggleSwitch('plugin-' + p.id, p.enabled, 'togglePlugin("' + JSON.stringify(p.id).replace(/"/g,"\'") + '",this.checked)')
    + '</div>'
  ).join('');
}

async function togglePlugin(id, enabled) {
  try {
    await fetch('/api/settings/plugins', {
      method: 'PATCH',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({id, enabled}),
    });
  } catch(e) { console.error('togglePlugin:', e); }
}

function _renderGlobalSummary(g) {
  const el = $('settings-global');
  if (!el) return;
  const rows = [
    {k: 'Effort Level',      v: g.effortLevel || '—'},
    {k: 'Codemoss Provider', v: g.codemossProviderId ? g.codemossProviderId.substring(0,16)+'…' : '—'},
    {k: 'Active MCP Servers', v: (g.mcpServers || []).join(', ') || '—'},
    {k: 'Marketplaces',      v: (g.extraKnownMarketplaces || []).join(', ') || '—'},
    {k: 'Active Hooks',      v: (g.hooks || []).join(', ') || '—'},
  ];
  el.innerHTML = '<div class="space-y-1">'
    + rows.map(r =>
      '<div style="display:flex;align-items:center;gap:12px;padding:4px 0;border-bottom:1px solid var(--border)">'
      + '<span class="text-xs font-mono" style="color:var(--text-muted);min-width:140px;flex-shrink:0">' + r.k + '</span>'
      + '<span class="text-xs font-mono" style="color:var(--text-primary)">' + r.v + '</span>'
      + '</div>'
    ).join('')
    + '</div>';
  el.classList.remove('toggles-loading');
}

// ── Team Builder ─────────────────────────────────────────────────────────────
let _tbAgents = [];
let _tbAgentNames = [];
let _tbSubAgentNames = [];

async function loadTeamBuilder() {
  try {
    const [agRes, teRes] = await Promise.all([
      fetch('/api/team-agents').then(r => r.json()),
      fetch('/api/teams').then(r => r.json()),
    ]);

    // Agent browser — all agents
    _tbAgents = agRes.agents || [];
    _tbAgentNames = [...new Set(_tbAgents.map(a => a.name).filter(Boolean))].sort();
    // Sub-agents only for team member select
    _tbSubAgentNames = [...new Set(
      _tbAgents.filter(a => a.source_dir === 'sub_agents').map(a => a.name).filter(Boolean)
    )].sort();
    // Fallback: if no sub_agents tagged, use all
    if (!_tbSubAgentNames.length) _tbSubAgentNames = _tbAgentNames;
    tbFilterAgents('');

    // Populate team composer member selects
    document.querySelectorAll('.tb-agent-select').forEach(s => _tbPopulateAgentSelect(s));

  } catch(e) { console.error('Team builder load error', e); }
}

function tbFilterAgents(q) {
  const ql = q.toLowerCase();
  const filtered = ql
    ? _tbAgents.filter(a =>
        (a.name||'').toLowerCase().includes(ql) ||
        (a.description||'').toLowerCase().includes(ql) ||
        (a.model||'').toLowerCase().includes(ql))
    : _tbAgents;
  $('tb-agent-count').textContent = filtered.length + ' agents';
  renderTable('tb-agents-table', [
    {key: 'name', label: 'Agent', type: 'string'},
    {key: 'model', label: 'Model', type: 'string'},
    {key: 'maxTurns', label: 'MaxTurns', type: 'number'},
    {key: 'tools_str', label: 'Tools', type: 'string'},
    {key: 'description', label: 'Description', type: 'string'},
  ], filtered.map(a => ({
    name: '<strong>' + (a.name||'') + '</strong>',
    model: a.model || '—',
    maxTurns: a.maxTurns || '—',
    tools_str: Array.isArray(a.tools) ? a.tools.join(', ') : (a.tools || '—'),
    description: a.description || '—',
  })), {pageSize: 15});
}

async function tbLoadSkills() {
  const domain = $('tb-skill-domain').value;
  const q = $('tb-skill-q').value;
  try {
    const params = new URLSearchParams();
    if (domain) params.set('domain', domain);
    if (q) params.set('q', q);
    $('tb-skills-table').innerHTML = '<div class="text-xs text-gray-500">Loading...</div>';
    const res = await fetch('/api/skills?' + params.toString());
    const data = await res.json();
    tbRenderSkills(data.skills || []);
  } catch(e) {
    $('tb-skills-table').innerHTML = '<div class="text-red-400">Error: ' + e.message + '</div>';
  }
}

function tbRenderSkills(skills) {
  $('tb-skill-count').textContent = skills.length + ' skills';
  renderTable('tb-skills-table', [
    {key: 'name', label: 'Skill', type: 'string'},
    {key: 'domain', label: 'Domain', type: 'string'},
    {key: 'subdomain', label: 'Subdomain', type: 'string'},
    {key: 'description', label: 'Description', type: 'string'},
    {key: 'tags_str', label: 'Tags', type: 'string'},
    {key: 'mitre_str', label: 'MITRE', type: 'string'},
  ], skills.map(s => ({
    name: '<strong>' + s.name + '</strong>',
    domain: s.domain || '—',
    subdomain: s.subdomain || '—',
    description: s.description || '—',
    tags_str: Array.isArray(s.tags) ? s.tags.join(', ') : '—',
    mitre_str: Array.isArray(s.mitre_attack) ? s.mitre_attack.join(', ') : '—',
  })), {pageSize: 20});
}

function _tbPopulateAgentSelect(sel) {
  const current = sel.value;
  while (sel.options.length > 1) sel.remove(1);
  _tbSubAgentNames.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n; opt.textContent = n;
    sel.appendChild(opt);
  });
  if (current && _tbSubAgentNames.includes(current)) sel.value = current;
}

let _tbMemberIdx = 0;
function tbAddMember() {
  const i = _tbMemberIdx++;
  const div = document.createElement('div');
  div.id = 'tb-member-' + i;
  div.className = 'flex items-center gap-3 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2';
  div.innerHTML =
    '<span class="text-xs text-gray-400 w-20 shrink-0">Member ' + (i+1) + '</span>'
    + '<input class="tb-member-name flex-1 px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" placeholder="Role (e.g. Analyst)">'
    + '<select class="tb-agent-select px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded">'
    + '<option value="">— select agent —</option>'
    + _tbSubAgentNames.map(n => '<option value="' + n + '">' + n + '</option>').join('')
    + '</select>'
    + '<button onclick="document.getElementById(\'tb-member-' + i + '\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>';
  $('tb-members').appendChild(div);
}

function tbGenerateTeam() {
  const members = [];
  document.querySelectorAll('[id^="tb-member-"]').forEach(row => {
    const name = row.querySelector('.tb-member-name').value.trim() || 'Member';
    const agent = row.querySelector('.tb-agent-select').value;
    members.push({role: name, agent: agent || null});
  });
  const team = {team: members, generated_at: new Date().toISOString()};
  const pre = $('tb-team-json');
  pre.textContent = JSON.stringify(team, null, 2);
  pre.style.display = '';
}

function tbCopyTeam() {
  const pre = $('tb-team-json');
  if (!pre.textContent) { tbGenerateTeam(); }
  navigator.clipboard.writeText(pre.textContent).catch(() => {});
}

async function tbSaveTeam() {
  const status = $('tb-save-status');
  const name = ($('tb-team-name') || {}).value || '';
  if (!name.trim()) { status.textContent = '✗ Enter a team name'; status.style.color = '#f87171'; return; }

  const members = [];
  document.querySelectorAll('[id^="tb-member-"]').forEach(row => {
    const mname = row.querySelector('.tb-member-name').value.trim() || 'Member';
    const agent = row.querySelector('.tb-agent-select').value;
    members.push({name: mname, agents: agent ? [agent] : []});
  });
  if (!members.length) { status.textContent = '✗ Add at least one member'; status.style.color = '#f87171'; return; }

  status.textContent = 'Saving...'; status.style.color = '#9ca3af';
  try {
    const res = await fetch('/api/teams', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: name.trim(), phases: members}),
    });
    const data = await res.json();
    if (!res.ok) { status.textContent = '✗ ' + (data.error || 'Failed'); status.style.color = '#f87171'; return; }
    status.textContent = '✓ Saved: ' + data.team; status.style.color = '#34d399';
    tbLoadSavedTeams();
    setTimeout(() => { status.textContent = ''; }, 3000);
  } catch (e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

async function tbLoadSavedTeams() {
  try {
    const res = await fetch('/api/teams');
    const data = await res.json();
    const teams = data.teams || [];
    const el = $('tb-saved-teams');
    if (!el) return;
    if (!teams.length) { el.innerHTML = '<div class="text-xs text-gray-500">No saved teams.</div>'; return; }

    renderTable('tb-saved-teams', [
      {key: 'name', label: 'Team', type: 'string'},
      {key: 'role', label: 'Role', type: 'string'},
      {key: 'description', label: 'Description', type: 'string'},
      {key: 'actions', label: 'Actions', type: 'html'},
    ], teams.map(t => ({
      name: '<strong>' + (t.name || '') + '</strong>',
      role: t.role || '—',
      description: t.description || '—',
      actions: (['blue-team','red-team','purple-team'].includes(t.name))
        ? '<span class="text-gray-600 text-xs">built-in</span>'
        : '<button onclick="tbDeleteTeam(\'' + t.name + '\')" class="px-2 py-0.5 bg-red-900 hover:bg-red-800 text-xs rounded">Delete</button>',
    })), {pageSize: 10});
  } catch(e) { console.error('tbLoadSavedTeams', e); }
}

async function tbDeleteTeam(name) {
  if (!confirm('Delete team "' + name + '"?')) return;
  try {
    await fetch('/api/teams/' + encodeURIComponent(name), {method: 'DELETE'});
    tbLoadSavedTeams();
  } catch(e) { console.error(e); }
}

// ── Agent Craft ─────────────────────────────────────────────────────────────
let _acAgents = [];

async function acLoadAgents() {
  try {
    const res = await fetch('/api/team-agents');
    const data = await res.json();
    _acAgents = data.agents || [];
    acRenderAgents(_acAgents);
  } catch(e) { console.error('acLoadAgents', e); }
}

function acFilterAgents() {
  const q = ($('ac-filter') || {}).value || '';
  const ql = q.toLowerCase();
  const filtered = ql
    ? _acAgents.filter(a =>
        (a.name||'').toLowerCase().includes(ql) ||
        (a.description||'').toLowerCase().includes(ql))
    : _acAgents;
  acRenderAgents(filtered);
}

function acRenderAgents(agents) {
  $('ac-count').textContent = agents.length + ' agents';
  renderTable('ac-agents-table', [
    {key: 'name', label: 'Agent', type: 'string'},
    {key: 'model', label: 'Model', type: 'string'},
    {key: 'source_dir', label: 'Dir', type: 'string'},
    {key: 'description', label: 'Description', type: 'string'},
    {key: 'actions', label: '', type: 'html'},
  ], agents.map(a => ({
    name: '<strong>' + (a.name||'') + '</strong>',
    model: a.model || '—',
    source_dir: a.source_dir || '—',
    description: (a.description||'').substring(0, 80) + ((a.description||'').length > 80 ? '...' : ''),
    actions: (a.name === 'cybersec-agent')
      ? '<span class="text-gray-600 text-xs">protected</span>'
      : '<button onclick="acEditAgent(\'' + (a.name||'') + '\')" class="px-2 py-0.5 bg-cyan-800 hover:bg-cyan-700 text-xs rounded mr-1">Edit</button>'
        + '<button onclick="acDeleteAgent(\'' + (a.name||'') + '\')" class="px-2 py-0.5 bg-red-900 hover:bg-red-800 text-xs rounded">Del</button>',
  })), {pageSize: 15});
}

async function acCreateAgent() {
  const status = $('ac-status');
  const name = ($('ac-name') || {}).value || '';
  if (!name.trim()) { status.textContent = '✗ Name required'; status.style.color = '#f87171'; return; }

  const tools = [];
  document.querySelectorAll('#ac-tools input[type=checkbox]:checked').forEach(cb => tools.push(cb.value));

  const mcpStr = ($('ac-mcp') || {}).value || '';
  const mcpServers = mcpStr.split(',').map(s => s.trim()).filter(Boolean);

  const body = {
    name: name.trim(),
    description: ($('ac-desc') || {}).value || '',
    model: ($('ac-model') || {}).value || 'sonnet',
    maxTurns: parseInt(($('ac-maxturns') || {}).value || '25', 10),
    tools,
    mcpServers,
    instructions: ($('ac-instructions') || {}).value || '',
  };

  status.textContent = 'Creating...'; status.style.color = '#9ca3af';
  try {
    const res = await fetch('/api/agents/crud', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) { status.textContent = '✗ ' + (data.error || 'Failed'); status.style.color = '#f87171'; return; }
    status.textContent = '✓ Created: ' + data.agent; status.style.color = '#34d399';
    $('ac-name').value = ''; $('ac-desc').value = ''; $('ac-instructions').value = '';
    acLoadAgents();
    setTimeout(() => { status.textContent = ''; }, 3000);
  } catch (e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

async function acEditAgent(name) {
  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name));
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    $('ac-edit-name').textContent = name;
    $('ac-edit-name').dataset.name = name;
    $('ac-edit-model').value = (data.frontmatter || {}).model || 'sonnet';
    $('ac-edit-maxturns').value = (data.frontmatter || {}).maxTurns || 25;
    $('ac-edit-desc').value = (data.frontmatter || {}).description || '';
    $('ac-edit-instructions').value = data.body || '';
    $('ac-edit-modal').style.display = '';
  } catch(e) { alert(e.message); }
}

function acCloseEdit() { $('ac-edit-modal').style.display = 'none'; }

async function acSaveEdit() {
  const name = $('ac-edit-name').dataset.name;
  const status = $('ac-edit-status');
  const body = {
    description: $('ac-edit-desc').value,
    model: $('ac-edit-model').value,
    maxTurns: parseInt($('ac-edit-maxturns').value, 10),
    instructions: $('ac-edit-instructions').value,
  };
  status.textContent = 'Saving...'; status.style.color = '#9ca3af';
  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name), {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) { status.textContent = '✗ ' + (data.error||'Failed'); status.style.color = '#f87171'; return; }
    status.textContent = '✓ Saved'; status.style.color = '#34d399';
    acCloseEdit();
    acLoadAgents();
  } catch(e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

async function acDeleteAgent(name) {
  if (!confirm('Delete agent "' + name + '"?')) return;
  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name), {method: 'DELETE'});
    const data = await res.json();
    if (!res.ok) { alert(data.error || 'Failed'); return; }
    acLoadAgents();
  } catch(e) { alert(e.message); }
}

// ── Workflow Builder ────────────────────────────────────────────────────────
let _wfStepIdx = 0;

function wfAddStep() {
  const i = _wfStepIdx++;
  const div = document.createElement('div');
  div.id = 'wf-step-' + i;
  div.className = 'bg-gray-900 border border-gray-700 rounded-lg px-4 py-3';
  const existingIds = [];
  document.querySelectorAll('[id^="wf-step-"]').forEach(el => {
    const inp = el.querySelector('.wf-step-id');
    if (inp && inp.value) existingIds.push(inp.value);
  });
  const depOpts = existingIds.map(id => '<option value="' + id + '">' + id + '</option>').join('');
  div.innerHTML =
    '<div class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2">'
    + '<div><label class="text-xs text-gray-400 block mb-1">Step ID</label>'
    + '<input class="wf-step-id w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" value="step-' + (i+1) + '"></div>'
    + '<div><label class="text-xs text-gray-400 block mb-1">Agent</label>'
    + '<input class="wf-step-agent w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" placeholder="agent-name" list="wf-agent-list"></div>'
    + '<div><label class="text-xs text-gray-400 block mb-1">Depends On</label>'
    + '<select class="wf-step-deps w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded" multiple><option value="">none</option>' + depOpts + '</select></div>'
    + '<div class="flex items-end"><button onclick="document.getElementById(\'wf-step-' + i + '\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕ Remove</button></div>'
    + '</div>'
    + '<div><label class="text-xs text-gray-400 block mb-1">Prompt</label>'
    + '<textarea class="wf-step-prompt w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono resize-y" rows="2" placeholder="Analyze the target system..."></textarea></div>';
  $('wf-steps').appendChild(div);
}

function wfClear() {
  $('wf-steps').innerHTML = '';
  $('wf-name').value = '';
  _wfStepIdx = 0;
}

async function wfExecute() {
  const status = $('wf-status');
  const name = ($('wf-name') || {}).value || '';
  if (!name.trim()) { status.textContent = '✗ Enter workflow name'; status.style.color = '#f87171'; return; }

  const steps = [];
  document.querySelectorAll('[id^="wf-step-"]').forEach(el => {
    const id = el.querySelector('.wf-step-id').value.trim();
    const agent = el.querySelector('.wf-step-agent').value.trim();
    const prompt = el.querySelector('.wf-step-prompt').value.trim();
    const deps = Array.from(el.querySelector('.wf-step-deps').selectedOptions)
      .map(o => o.value).filter(Boolean);
    if (id && agent && prompt) steps.push({id, agent, prompt, depends_on: deps});
  });
  if (!steps.length) { status.textContent = '✗ Add at least one step'; status.style.color = '#f87171'; return; }

  status.textContent = '⏳ Executing...'; status.style.color = '#fbbf24';
  try {
    const res = await fetch('/api/workflows', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: name.trim(), steps, execute: true}),
    });
    const data = await res.json();
    if (!res.ok) { status.textContent = '✗ ' + (data.error || 'Failed'); status.style.color = '#f87171'; return; }
    status.textContent = '✓ ' + data.status; status.style.color = data.status === 'completed' ? '#34d399' : '#f87171';
    wfRenderResult(data);
  } catch (e) { status.textContent = '✗ ' + e.message; status.style.color = '#f87171'; }
}

function wfRenderResult(wf) {
  const history = $('wf-history');
  const card = document.createElement('div');
  card.className = 'bg-gray-900 border border-gray-700 rounded-lg p-4';
  const statusBadge = wf.status === 'completed'
    ? '<span class="badge badge-ok">completed</span>'
    : '<span class="badge badge-error">' + wf.status + '</span>';
  let stepsHtml = '';
  (wf.steps || []).forEach(s => {
    const sBadge = s.status === 'completed' ? '✓' : s.status === 'failed' ? '✗' : s.status === 'skipped' ? '⊘' : '?';
    const sColor = s.status === 'completed' ? 'text-green-400' : s.status === 'failed' ? 'text-red-400' : 'text-gray-500';
    stepsHtml += '<div class="mb-2 border-b border-gray-800 pb-2">'
      + '<div class="flex items-center gap-2 mb-1">'
      + '<span class="' + sColor + ' font-mono text-xs">' + sBadge + ' ' + s.id + '</span>'
      + '<span class="text-gray-500 text-xs">(' + s.agent + ', ' + s.elapsed_ms + 'ms)</span></div>';
    if (s.result) stepsHtml += '<pre class="text-xs text-gray-300 whitespace-pre-wrap max-h-32 overflow-y-auto">' + (s.result||'').substring(0,1000) + '</pre>';
    if (s.error) stepsHtml += '<div class="text-xs text-red-400">' + s.error + '</div>';
    stepsHtml += '</div>';
  });
  card.innerHTML = '<div class="flex items-center gap-2 mb-2"><strong class="text-sm">' + (wf.name||wf.id) + '</strong> ' + statusBadge + '</div>' + stepsHtml;
  history.prepend(card);
}

async function wfLoadAgentList() {
  try {
    const res = await fetch('/api/team-agents');
    const data = await res.json();
    let dl = document.getElementById('wf-agent-list');
    if (!dl) {
      dl = document.createElement('datalist');
      dl.id = 'wf-agent-list';
      document.body.appendChild(dl);
    }
    dl.innerHTML = (data.agents||[]).map(a => '<option value="' + (a.name||'') + '">').join('');
  } catch(e) { console.error(e); }
}

const _sseConns = {};
const _sseConnected = new Set();

function _sseUpdateBadge() {
  const badge = $('sse-status');
  if (!badge) return;
  const n = _sseConnected.size;
  badge.textContent = n === 4 ? '\u25cf SSE Live' : '\u25cf SSE ' + n + '/4';
  badge.className = n === 4 ? 'badge badge-ok' : 'badge badge-standard';
}

function _sseConnect(key, path, onData, eventName) {
  if (_sseConns[key]) { try { _sseConns[key].close(); } catch {} }
  const es = new EventSource(path);
  _sseConns[key] = es;
  const handler = e => { try { onData(JSON.parse(e.data)); } catch {} };
  if (eventName) es.addEventListener(eventName, handler);
  else es.onmessage = handler;
  es.onopen = () => { _sseConnected.add(key); _sseUpdateBadge(); };
  es.onerror = () => {
    _sseConnected.delete(key);
    _sseUpdateBadge();
    es.close();
    setTimeout(() => _sseConnect(key, path, onData, eventName), 3000);
  };
}

function _renderHealth(d) {
  const hc = $('health-content');
  if (!hc) return;
  if (d.error) { hc.innerHTML = '<p class="text-red-400">SSE error: ' + d.error + '</p>'; return; }
  const dbStatus = (d.database || {}).status === 'ok' ? '&#x2705;' : '&#x274c;';
  hc.innerHTML = '<div class="grid grid-cols-2 gap-4">'
    + '<div><h4 class="font-semibold mb-2">Database</h4>'
    + '<p>' + dbStatus + ' ' + ((d.database || {}).status || 'unknown') + '</p>'
    + '<p class="text-xs text-gray-500">Tables: ' + ((d.database || {}).table_count || '?') + '</p></div>'
    + '<div><h4 class="font-semibold mb-2">Proxy</h4>'
    + '<p>&#x2705; ' + ((d.proxy || {}).providers_enabled || 0) + ' providers enabled</p>'
    + '<p class="text-xs text-gray-500">' + ((d.proxy || {}).providers_free || 0) + ' free providers</p></div>'
    + '</div>';
  hc.classList.remove('loading');
}

function _renderCases(d) {
  if (d.error) { const t = $('cases-table'); if (t) t.innerHTML = '<p class="text-red-400">SSE error: ' + d.error + '</p>'; return; }
  const tot = $('cases-total'); if (tot) tot.textContent = d.total || 0;
  const op = $('cases-open'); if (op) op.textContent = d.open || 0;
  const cl = $('cases-closed'); if (cl) cl.textContent = d.closed || 0;
  const caseRows = (d.cases || []).map(c => ({
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

function _renderTasks(d) {
  if (d.error) { const t = $('tasks-table'); if (t) t.innerHTML = '<p class="text-red-400">SSE error: ' + d.error + '</p>'; return; }
  const tot = $('tasks-total'); if (tot) tot.textContent = d.total || 0;
  const sub = $('tasks-submitted'); if (sub) sub.textContent = (d.by_state || {}).submitted || 0;
  const wrk = $('tasks-working'); if (wrk) wrk.textContent = (d.by_state || {}).working || 0;
  const cmp = $('tasks-completed'); if (cmp) cmp.textContent = (d.by_state || {}).completed || 0;
  const fld = $('tasks-failed'); if (fld) fld.textContent = (d.by_state || {}).failed || 0;
  const taskRows = (d.tasks || []).map(t => ({
    id: '<span class="font-mono text-xs">' + t.id + '</span>',
    state: t.state === 'completed' ? '<span class="badge badge-ok">\u2713 DONE</span>'
      : t.state === 'failed' ? '<span class="badge badge-err">\u2717 FAIL</span>'
      : t.state === 'working' ? '<span class="badge badge-standard">\u27f3 WORK</span>'
      : t.state === 'submitted' ? '<span class="badge badge-budget">\u2295 SBMT</span>'
      : '<span class="badge">' + (t.state || '?').toUpperCase() + '</span>',
    agent: t.agent || '?',
    created_at: t.created_at,
    updated_at: t.updated_at,
    action: (t.state === 'completed' || t.state === 'failed' || t.state === 'canceled')
      ? '\u2014'
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

function _renderTelemetry(d) {
  const tc = $('telemetry-content');
  if (!tc) return;
  if (d.error) { tc.innerHTML = '<p class="text-red-400">SSE error: ' + d.error + '</p>'; return; }
  const keys = Object.keys(d);
  if (!keys.length) { tc.innerHTML = '<p class="text-gray-500">No metrics recorded yet.</p>'; return; }
  tc.classList.remove('loading');
  const rows = keys.map(k => ({
    metric: k,
    count: d[k].count,
    mean_ms: d[k].mean,
    p50_ms: d[k].p50,
    p95_ms: d[k].p95,
    p99_ms: d[k].p99,
    rps: d[k].rps,
  }));
  renderTable('telemetry-content', [
    {key: 'metric', label: 'Metric', type: 'string'},
    {key: 'count', label: 'Count', type: 'number'},
    {key: 'mean_ms', label: 'Mean (ms)', type: 'number'},
    {key: 'p50_ms', label: 'p50', type: 'number'},
    {key: 'p95_ms', label: 'p95', type: 'number'},
    {key: 'p99_ms', label: 'p99', type: 'number'},
    {key: 'rps', label: 'RPS', type: 'number'},
  ], rows);
}

function initSSE() {
  _sseConnect('health',    '/sse/health',    _renderHealth);
  _sseConnect('cases',     '/sse/cases',     _renderCases);
  _sseConnect('tasks',     '/sse/tasks',     _renderTasks);
  _sseConnect('telemetry', '/sse/telemetry', _renderTelemetry, 'telemetry_update');
  _sseUpdateBadge();
}

// ── OpenSearch: cluster health + index stats ─────────────────────────────────
async function loadOpenSearch() {
  $('os-cluster').innerHTML = '<div class="loading text-gray-500">Fetching...</div>';
  $('os-indices').innerHTML = '';
  try {
    const res = await fetch('/api/opensearch');
    const data = await res.json();
    if (data.error && !data.cluster) {
      $('os-cluster').innerHTML = '<div class="text-red-400">OpenSearch unavailable: ' + data.error + '</div>';
      return;
    }
    const c = data.cluster || {};
    const statusColor = {'green': 'text-green-400', 'yellow': 'text-yellow-400', 'red': 'text-red-400'}[c.status] || 'text-gray-400';
    $('os-cluster').innerHTML = '<div class="flex gap-6 text-sm mb-3">'
      + '<span class="' + statusColor + ' font-semibold">&#x25cf; ' + (c.status || '?').toUpperCase() + '</span>'
      + '<span class="text-gray-400">Nodes: <strong class="text-white">' + (c.number_of_nodes || 0) + '</strong></span>'
      + '<span class="text-gray-400">Active shards: <strong class="text-white">' + (c.active_shards || 0) + '</strong></span>'
      + '<span class="text-gray-400">Unassigned: <strong class="text-white">' + (c.unassigned_shards || 0) + '</strong></span>'
      + '<span class="text-gray-400">Total docs: <strong class="text-white">' + (data.total_docs || 0).toLocaleString() + '</strong></span>'
      + '</div>';
    const schema = [
      {key: 'index', label: 'Index', type: 'string'},
      {key: 'docs', label: 'Docs', type: 'number'},
      {key: 'size_mb', label: 'Size (MB)', type: 'number'},
    ];
    renderTable('os-indices', schema, data.indices || []);
  } catch (e) {
    $('os-cluster').innerHTML = '<div class="text-red-400">Error: ' + e.message + '</div>';
  }
}

// ── Explorer: generic table viewer ──────────────────────────────────────────
async function loadExplorerModels() {
  try {
    const res = await fetch('/api/models');
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
    const res = await fetch('/api/tables/' + encodeURIComponent(model) + '?limit=500');
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
loadSettingsToggles();
loadSettings();
loadTeamBuilder();
tbLoadSavedTeams();
wfLoadAgentList();
acLoadAgents();
loadOpenSearch();
initSSE();

// ── Status bar ───────────────────────────────────────────────────────────────
function _updateStatusBar(tab) {
  const el = $('sb-tab');
  if (el) el.textContent = '\u2B21 ' + tab.toUpperCase().replace(/-/g,' ');
}
setInterval(() => {
  const el = $('sb-time');
  if (el) el.textContent = new Date().toLocaleTimeString();
}, 1000);

// ── MCP Installer ─────────────────────────────────────────────────────────────
async function installMcp() {
  const name = ($('mcp-install-name') || {}).value && $('mcp-install-name').value.trim();
  const cmd  = ($('mcp-install-cmd')  || {}).value && $('mcp-install-cmd').value.trim();
  const argsStr = ($('mcp-install-args') || {}).value && $('mcp-install-args').value.trim();
  const envStr  = ($('mcp-install-env')  || {}).value && $('mcp-install-env').value.trim();
  const st = $('mcp-install-status');

  if (!name || !cmd) { if(st) { st.textContent = '\u2717 Name and command are required'; st.style.color='var(--red)'; } return; }

  const args = argsStr ? argsStr.split(',').map(s => s.trim()).filter(Boolean) : [];
  const env = {};
  if (envStr) envStr.split('\n').forEach(line => {
    const eqIdx = line.indexOf('=');
    if (eqIdx > 0) { const k = line.slice(0, eqIdx).trim(); const v = line.slice(eqIdx+1).trim(); if (k) env[k] = v; }
  });

  if(st) { st.textContent = 'Installing\u2026'; st.style.color='var(--text-muted)'; }
  try {
    const d = await fetch('/api/settings/install-mcp', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, command: cmd, args, env}),
    }).then(r => r.json());
    if (d.error) { if(st) { st.textContent = '\u2717 ' + d.error; st.style.color='var(--red)'; } return; }
    if(st) { st.textContent = '\u2713 Installed: ' + name; st.style.color='var(--success)'; }
    ['mcp-install-name','mcp-install-cmd','mcp-install-args','mcp-install-env'].forEach(id => { const el = $(id); if(el) el.value = ''; });
    fetch('/api/settings/global-mcps').then(r => r.json()).then(d => _renderGlobalMcpToggles(d.servers || []));
  } catch(e) { if(st) { st.textContent = '\u2717 ' + e.message; st.style.color='var(--red)'; } }
}

async function removeMcp(name) {
  if (!confirm('Remove MCP server "' + name + '" from ~/.claude/settings.json?')) return;
  try {
    const d = await fetch('/api/settings/remove-mcp', {
      method: 'DELETE', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name}),
    }).then(r => r.json());
    if (d.error) { alert('Error: ' + d.error); return; }
    fetch('/api/settings/global-mcps').then(r => r.json()).then(d => _renderGlobalMcpToggles(d.servers || []));
  } catch(e) { alert('Error: ' + e.message); }
}

// ── Hooks Manager ─────────────────────────────────────────────────────────────
async function loadGlobalHooks() {
  try {
    const d = await fetch('/api/settings/hooks').then(r => r.json());
    _renderHooksList(d.hooks || {});
  } catch(e) { console.error('loadGlobalHooks:', e); }
}

function _renderHooksList(hooks) {
  const el = $('settings-global-hooks');
  if (!el) return;
  const events = Object.keys(hooks);
  if (!events.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No hooks defined in ~/.claude/settings.json</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = events.map(event =>
    '<div style="margin-bottom:12px">'
    + '<div style="font-size:11px;font-weight:600;font-family:var(--font-mono);color:var(--cyan);margin-bottom:6px">' + event + '</div>'
    + (hooks[event] || []).map(h =>
      '<div class="toggle-row" style="padding:6px 0">'
      + '<div>'
        + '<div class="toggle-label" style="font-size:11px">' + h.command + '</div>'
        + (h.matcher ? '<div class="toggle-sub">matcher: ' + h.matcher + '</div>' : '')
      + '</div>'
      + '<button class="btn btn-ghost" style="font-size:10px;padding:2px 8px" '
        + 'onclick="removeHook(\'' + event + '\',\'' + h.command.replace(/\\/g,'\\\\').replace(/'/g,"\\'") + '\')">'
        + '\u2715 Remove</button>'
      + '</div>'
    ).join('')
    + '</div>'
  ).join('');
}

async function addHook() {
  const event   = ($('hook-add-event')   || {}).value;
  const matcher = ($('hook-add-matcher') || {}).value && $('hook-add-matcher').value.trim();
  const command = ($('hook-add-cmd')     || {}).value && $('hook-add-cmd').value.trim();
  const st = $('hook-add-status');
  if (!command) { if(st) { st.textContent='\u2717 Command required'; st.style.color='var(--red)'; } return; }
  if(st) { st.textContent='Adding\u2026'; st.style.color='var(--text-muted)'; }
  try {
    const d = await fetch('/api/settings/hooks', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({event, command, matcher}),
    }).then(r => r.json());
    if (d.error) { if(st) { st.textContent='\u2717 '+d.error; st.style.color='var(--red)'; } return; }
    if(st) { st.textContent='\u2713 Hook added'; st.style.color='var(--success)'; }
    const cmdEl = $('hook-add-cmd'); if(cmdEl) cmdEl.value = '';
    const matchEl = $('hook-add-matcher'); if(matchEl) matchEl.value = '';
    loadGlobalHooks();
  } catch(e) { if(st) { st.textContent='\u2717 '+e.message; st.style.color='var(--red)'; } }
}

async function removeHook(event, command) {
  if (!confirm('Remove hook from ' + event + '?')) return;
  try {
    const d = await fetch('/api/settings/hooks', {
      method:'DELETE', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({event, command}),
    }).then(r => r.json());
    if (d.error) { alert('Error: '+d.error); return; }
    loadGlobalHooks();
  } catch(e) { alert('Error: '+e.message); }
}

// ── Agent Factory ─────────────────────────────────────────────────────────────
let _afTemplates = [];
let _afSkills = [];
let _afTplIdx = 1;
let _afSkillIdx = 1;

async function afLoadTemplates() {
  try {
    const d = await fetch('/api/settings/agent-agents').then(r => r.json());
    _afTemplates = d.agents || [];
    // Populate initial template select
    const sel = $('af-tpl-0');
    if (sel) {
      while (sel.options.length > 1) sel.remove(1);
      _afTemplates.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t; opt.textContent = t.replace('.md','');
        sel.appendChild(opt);
      });
    }
  } catch(e) { console.error('afLoadTemplates', e); }
}

function afAddTemplate() {
  const i = _afTplIdx++;
  const row = document.createElement('div');
  row.style.cssText = 'display:flex;align-items:center;gap:6px';
  const sel = document.createElement('select');
  sel.id = 'af-tpl-' + i;
  sel.style.cssText = 'flex:1;padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono)';
  sel.innerHTML = '<option value="">— none —</option>' +
    _afTemplates.map(t => '<option value="' + t + '">' + t.replace('.md','') + '</option>').join('');
  const rm = document.createElement('button');
  rm.textContent = '✕'; rm.className = 'btn';
  rm.style.cssText = 'font-size:11px;padding:3px 8px';
  rm.onclick = () => row.remove();
  row.appendChild(sel); row.appendChild(rm);
  $('af-tpl-rows').appendChild(row);
}

async function afLoadSkillOptions() {
  if (_afSkills.length) return;
  try {
    const d = await fetch('/api/skills').then(r => r.json());
    _afSkills = (d.skills || []).map(s => s.name).filter(Boolean).sort();
  } catch(e) { console.error('afLoadSkillOptions', e); }
}

async function afAddSkill() {
  await afLoadSkillOptions();
  const i = _afSkillIdx++;
  const row = document.createElement('div');
  row.style.cssText = 'display:flex;align-items:center;gap:6px';
  const sel = document.createElement('select');
  sel.id = 'af-skill-' + i;
  sel.style.cssText = 'flex:1;padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono)';
  sel.innerHTML = '<option value="">— none —</option>' +
    _afSkills.map(s => '<option value="' + s + '">' + s + '</option>').join('');
  const rm = document.createElement('button');
  rm.textContent = '✕'; rm.className = 'btn';
  rm.style.cssText = 'font-size:11px;padding:3px 8px';
  rm.onclick = () => row.remove();
  // Also populate af-skill-0 if empty
  const sk0 = $('af-skill-0');
  if (sk0 && sk0.options.length <= 1) {
    sk0.innerHTML = '<option value="">— none —</option>' +
      _afSkills.map(s => '<option value="' + s + '">' + s + '</option>').join('');
  }
  row.appendChild(sel); row.appendChild(rm);
  $('af-skill-rows').appendChild(row);
}

// Update agent type hint
(function() {
  const hints = {
    'specialist':   'Focused expert — executes tasks, returns results.',
    'team-leader':  'Claude team orchestrator — manages a cohesive multi-agent claude team.',
    'orchestrator': 'Inter-API orchestrator — routes across multiple API providers and teams.',
  };
  document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'af-type') {
      const h = $('af-type-hint');
      if (h) h.textContent = hints[e.target.value] || '';
    }
  });
})();

async function afGenerate() {
  const st = $('af-status');
  const preview = $('af-preview');
  const type        = ($('af-type') || {}).value || 'specialist';
  const model       = ($('af-model') || {}).value || 'sonnet';
  const maxTurns    = parseInt(($('af-maxturns') || {}).value || '30');
  const name        = ($('af-name') || {}).value.trim();
  const description = ($('af-desc') || {}).value.trim();
  const extra       = ($('af-extra') || {}).value.trim();
  const saveFile    = ($('af-save-file') || {}).checked !== false;
  const projectCtx  = ($('af-project-ctx') || {}).checked || false;

  const tools = [...document.querySelectorAll('#af-tools input[type=checkbox]:checked')].map(c => c.value);
  const agents = [...document.querySelectorAll('[id^="af-tpl-"]')]
    .map(s => s.value).filter(Boolean);
  const skills = [...document.querySelectorAll('[id^="af-skill-"]')]
    .map(s => s.value).filter(Boolean);
  const research = [...document.querySelectorAll('[id^="af-r-"]:checked')].map(c => c.value);

  if (!name) { if(st){st.textContent='✗ Name required'; st.style.color='var(--red)';} return; }

  if(st){st.textContent='⟳ Generating…'; st.style.color='var(--text-muted)';}
  if(preview){preview.style.display='none';}

  try {
    const resp = await fetch('/api/agents/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        type, name, description, model, maxTurns, tools,
        agents, skills, research, project_context: projectCtx,
        extra_instructions: extra, save: saveFile,
      }),
    });
    const d = await resp.json();
    if (d.error) { if(st){st.textContent='✗ '+d.error; st.style.color='var(--red)';} return; }
    if(st){st.textContent='✓ Generated' + (saveFile ? ' & saved to .claude/agents/' : ''); st.style.color='var(--success)';}
    if(preview){preview.textContent = d.content || ''; preview.style.display='';}
  } catch(e) {
    if(st){st.textContent='✗ '+e.message; st.style.color='var(--red)';}
  }
}

// Load agents when Agent Factory opens
document.addEventListener('click', function(e) {
  const tab = e.target.closest('.tab');
  if (tab && tab.id === 'nav-agent-factory') afLoadTemplates();
});

// ── Init ──────────────────────────────────────────────────────────────────────
// Activate first sidebar tab on load
(function() {
  document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
  const first = document.getElementById('tab-health');
  if (first) first.style.display = '';
  const nav = document.getElementById('nav-health');
  if (nav) nav.classList.add('active');
  const crumb = document.querySelector('#topbar-title');
  if (crumb) crumb.textContent = '▶ HEALTH';
})();

refresh();
setInterval(refresh, 15000);
"""
