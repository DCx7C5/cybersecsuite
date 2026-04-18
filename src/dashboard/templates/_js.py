"""All dashboard JavaScript: core utils, refresh, agent query, explorer."""

_JS = r"""
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
    const [ov, pv, uv, cv, av, iv, dv, agv, rtv, fv, pmv, pocv,
           findingsv, iocsv, yarav, netv, intv, auditv, compv] = await Promise.all([
      fetch('/dashboard/api/overview').then(r => r.json()),
      fetch('/dashboard/api/providers').then(r => r.json()),
      fetch('/dashboard/api/usage').then(r => r.json()),
      fetch('/dashboard/api/crypto').then(r => r.json()),
      fetch('/dashboard/api/a2a').then(r => r.json()),
      fetch('/dashboard/api/investigations').then(r => r.json()),
      fetch('/dashboard/api/db-counts').then(r => r.json()),
      fetch('/dashboard/api/agents').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/routing').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/agent-factory').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/prompts').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/pocs').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/findings').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/iocs').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/yara').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/network').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/intelligence').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/audit').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/compliance').then(r => r.json()).catch(() => ({error:'unavailable'})),
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

// ── Agent Query panel ────────────────────────────────────────────────────────
let _aqHistory = [];

function _aqPopulateAgents(agents) {
  const sel = $('aq-agent');
  const current = sel.value;
  // preserve existing default option, rebuild the rest
  while (sel.options.length > 1) sel.remove(1);
  (agents || []).forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.name;
    opt.textContent = a.name + (a.claude_metadata?.role === 'orchestrator' ? ' (orch)' : '');
    sel.appendChild(opt);
  });
  if (current) sel.value = current;
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
  const agent = $('aq-agent').value || 'cybersec';
  const prompt = ($('aq-prompt').value || '').trim();
  if (!prompt) { $('aq-status').textContent = '⚠ Prompt is empty'; return; }

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

    const res = await fetch('/dashboard/api/agent-query', {
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
    const res = await fetch('/dashboard/api/settings');
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
    const res = await fetch('/dashboard/api/settings', {
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
    const res = await fetch('/dashboard/api/settings', {
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

// ── Team Builder ─────────────────────────────────────────────────────────────
let _tbAgents = [];
let _tbAgentNames = [];

async function loadTeamBuilder() {
  try {
    const [agRes, skDomRes, teRes] = await Promise.all([
      fetch('/dashboard/api/team-agents').then(r => r.json()),
      fetch('/dashboard/api/skills?domain=').then(r => r.json()),
      fetch('/dashboard/api/teams').then(r => r.json()),
    ]);

    // Agent browser
    _tbAgents = agRes.agents || [];
    _tbAgentNames = _tbAgents.map(a => a.name);
    tbFilterAgents('');

    // Populate skill domain select
    const sel = $('tb-skill-domain');
    (skDomRes.domains || []).forEach(d => {
      const opt = document.createElement('option');
      opt.value = d; opt.textContent = d;
      sel.appendChild(opt);
    });
    tbRenderSkills(skDomRes.skills || []);

    // Populate team composer agent selects (after phases are present)
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
    const res = await fetch('/dashboard/api/skills?' + params.toString());
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

let _tbPhaseIdx = 0;
function tbAddPhase() {
  const i = _tbPhaseIdx++;
  const div = document.createElement('div');
  div.id = 'tb-phase-' + i;
  div.className = 'flex items-center gap-3 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2';
  div.innerHTML =
    '<span class="text-xs text-gray-400 w-16 shrink-0">Phase ' + (i+1) + '</span>'
    + '<input class="tb-phase-name flex-1 px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" placeholder="Phase name (e.g. Recon)">'
    + '<select class="tb-agent-select px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded">'
    + '<option value="">— select agent —</option>'
    + _tbAgentNames.map(n => '<option value="' + n + '">' + n + '</option>').join('')
    + '</select>'
    + '<button onclick="document.getElementById(\'tb-phase-' + i + '\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>';
  $('tb-phases').appendChild(div);
}

function _tbPopulateAgentSelect(sel) {
  _tbAgentNames.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n; opt.textContent = n;
    sel.appendChild(opt);
  });
}

function tbGenerateTeam() {
  const phases = [];
  document.querySelectorAll('[id^="tb-phase-"]').forEach(row => {
    const name = row.querySelector('.tb-phase-name').value.trim() || 'Phase';
    const agent = row.querySelector('.tb-agent-select').value;
    phases.push({phase: name, agent: agent || null});
  });
  const team = {team: phases, generated_at: new Date().toISOString()};
  const pre = $('tb-team-json');
  pre.textContent = JSON.stringify(team, null, 2);
  pre.style.display = '';
}

function tbCopyTeam() {
  const pre = $('tb-team-json');
  if (!pre.textContent) { tbGenerateTeam(); }
  navigator.clipboard.writeText(pre.textContent).catch(() => {});
}

// ── SSE: EventSource wiring for cases, tasks, health, telemetry ─────────────
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
  _sseConnect('health',    '/dashboard/sse/health',    _renderHealth);
  _sseConnect('cases',     '/dashboard/sse/cases',     _renderCases);
  _sseConnect('tasks',     '/dashboard/sse/tasks',     _renderTasks);
  _sseConnect('telemetry', '/dashboard/sse/telemetry', _renderTelemetry, 'telemetry_update');
  _sseUpdateBadge();
}

// ── OpenSearch: cluster health + index stats ─────────────────────────────────
async function loadOpenSearch() {
  $('os-cluster').innerHTML = '<div class="loading text-gray-500">Fetching...</div>';
  $('os-indices').innerHTML = '';
  try {
    const res = await fetch('/dashboard/api/opensearch');
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
loadSettings();
loadTeamBuilder();
loadOpenSearch();
initSSE();

refresh();
setInterval(refresh, 15000);
"""
