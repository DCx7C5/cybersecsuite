// Dashboard refresh: fetch all data and render all tabs

import { $, currentTab, fmt, _updateContextBar, clearCtxCache } from './core.js';
import { renderTable } from './table.js';

interface APIResponse {
  error?: string;
  [key: string]: any;
}

export async function refresh(): Promise<void> {
  try {
    const [ov, uv, cv, av, iv, dv, agv, rtv, pmv, pocv, findingsv, iocsv, yarav, netv, intv, auditv, compv, hv, afv] = await Promise.all([
      fetch('/api/overview').then((r) => r.json()),
      fetch('/api/usage').then((r) => r.json()),
      fetch('/api/crypto').then((r) => r.json()),
      fetch('/api/a2a').then((r) => r.json()),
      fetch('/api/investigations').then((r) => r.json()),
      fetch('/api/db-counts').then((r) => r.json()),
      fetch('/api/agents').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/routing').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/prompts').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/pocs').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/findings').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/iocs').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/yara').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/network').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/intelligence').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/audit').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/compliance').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/health').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
      fetch('/api/agent-factory').then((r) => r.json()).catch(() => ({ error: 'unavailable' })),
    ]);

    if ($('uptime') && ov.uptime_seconds !== undefined)
      $('uptime')!.textContent = Math.round(ov.uptime_seconds) + 's uptime';

    // Invalidate context cache so next showTab fetches fresh data
    clearCtxCache();
    _updateContextBar(currentTab);

    // Remove loading
    document.querySelectorAll('.loading').forEach((el) => {
      el.classList.remove('loading');
    });

    renderTable(
      'usage-table',
      [
        { key: 'provider', label: 'Provider', type: 'string' },
        { key: 'model', label: 'Model', type: 'string' },
        { key: 'tokens', label: 'Tokens', type: 'number' },
        { key: 'cost_usd', label: 'Cost USD', type: 'number' },
        { key: 'latency_ms', label: 'Latency ms', type: 'number' },
        { key: 'stream', label: 'Stream', type: 'bool' },
        { key: 'status', label: 'Status', type: 'string' },
      ],
      (uv.recent || []).map((r: any) => ({
        provider: r.provider,
        model: r.model,
        tokens: r.tokens,
        cost_usd: r.cost_usd,
        latency_ms: r.latency_ms,
        stream: r.stream,
        status: r.success ? '<span class="badge badge-ok">OK</span>' : '<span class="badge badge-err">FAIL</span>',
      }))
    );

    // Crypto tab
    const cc = $('crypto-content');
    if (cv.error) {
      cc!.innerHTML = '<p class="text-red-400">Error: ' + cv.error + '</p>';
    } else {
      cc!.innerHTML =
        '<div class="grid grid-cols-3 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        cv.total_artifacts +
        '</div><div class="text-xs text-gray-500">Total Artifacts</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-green-400">' +
        cv.valid +
        '</div><div class="text-xs text-gray-500">Valid Sigs</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' +
        cv.invalid +
        '</div><div class="text-xs text-gray-500">Invalid Sigs</div></div>' +
        '</div>' +
        '<h4 class="font-semibold mb-2">Recent Signature Logs</h4>' +
        '<div id="crypto-sig-table"></div>';
      renderTable(
        'crypto-sig-table',
        [
          { key: 'artifact_id', label: 'Artifact', type: 'string' },
          { key: 'action', label: 'Action', type: 'string' },
          { key: 'status', label: 'Status', type: 'string' },
          { key: 'key_id', label: 'Key', type: 'string' },
          { key: 'created_at', label: 'Time', type: 'datetime' },
        ],
        (cv.recent_signature_logs || []).map((l: any) => ({
          artifact_id: l.artifact_id,
          action: l.action,
          status:
            '<span class="badge ' +
            (l.status === 'valid' ? 'badge-ok' : 'badge-err') +
            '">' +
            (l.status || '?') +
            '</span>',
          key_id: l.key_id,
          created_at: l.created_at,
        }))
      );
    }

    // A2A tab
    const ac = $('a2a-content');
    if (av.error) {
      ac!.innerHTML = '<p class="text-red-400">Error: ' + av.error + '</p>';
    } else {
      ac!.innerHTML =
        '<div class="grid grid-cols-3 md:grid-cols-6 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        av.total_tasks +
        '</div><div class="text-xs text-gray-500">Total</div></div>' +
        Object.entries(av.by_state || {})
          .map(
            ([k, v]) =>
              '<div class="card text-center"><div class="text-xl font-bold">' +
              v +
              '</div><div class="text-xs text-gray-500">' +
              k +
              '</div></div>'
          )
          .join('') +
        '</div>' +
        '<h4 class="font-semibold mb-2">Recent Tasks</h4>' +
        '<div id="a2a-tasks-table"></div>';
      renderTable(
        'a2a-tasks-table',
        [
          { key: 'id', label: 'ID', type: 'string' },
          { key: 'session_id', label: 'Session', type: 'string' },
          { key: 'state', label: 'State', type: 'string' },
          { key: 'updated_at', label: 'Updated', type: 'datetime' },
        ],
        (av.recent_tasks || []).map((t: any) => ({
          id: '<span class="font-mono text-xs">' + (t.id || '?') + '</span>',
          session_id: t.session_id || '—',
          state:
            '<span class="badge ' +
            (t.state === 'completed' ? 'badge-ok' : t.state === 'failed' ? 'badge-err' : 'badge-budget') +
            '">' +
            (t.state || '?') +
            '</span>',
          updated_at: t.updated_at,
        }))
      );
    }

    // Investigations tab
    const ic = $('inv-content');
    if (iv.error) {
      ic!.innerHTML = '<p class="text-red-400">Error: ' + iv.error + '</p>';
    } else {
      ic!.innerHTML =
        '<div class="grid grid-cols-4 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        iv.findings +
        '</div><div class="text-xs text-gray-500">Findings</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        iv.iocs +
        '</div><div class="text-xs text-gray-500">IOCs</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        iv.risks +
        '</div><div class="text-xs text-gray-500">Risks</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        iv.mitre_techniques +
        '</div><div class="text-xs text-gray-500">MITRE</div></div>' +
        '</div>' +
        '<h4 class="font-semibold mb-2">Findings by Severity</h4>' +
        '<div id="inv-table"></div>';
      const sevRows = Object.entries(iv.findings_by_severity || {}).map(([k, v]) => ({
        severity: (k as string).toUpperCase(),
        count: v,
      }));
      renderTable(
        'inv-table',
        [
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'count', label: 'Count', type: 'number' },
        ],
        sevRows,
        { sortCol: 1, sortDir: 'desc' }
      );
    }

    // DB Counts tab
    const dc = $('db-content');
    if (dv.error) {
      dc!.innerHTML = '<p class="text-red-400">Error: ' + dv.error + '</p>';
    } else {
      dc!.innerHTML = '<div id="db-table"></div>';
      const dbRows = Object.entries(dv.counts || {}).map(([t, c]) => ({
        table_name: t,
        rows: c,
      }));
      renderTable(
        'db-table',
        [
          { key: 'table_name', label: 'Table', type: 'string' },
          { key: 'rows', label: 'Rows', type: 'number' },
        ],
        dbRows,
        { sortCol: 1, sortDir: 'desc' }
      );
      // Populate agent-query context table selector (assumes _aqPopulateContextTables exists in agents.ts)
      if ((window as any)._aqPopulateContextTables) {
        (window as any)._aqPopulateContextTables(Object.keys(dv.counts || {}));
      }
    }

    // Agents tab
    const agc = $('agents-content');
    if (agv.error) {
      agc!.innerHTML = '<p class="text-red-400">Error: ' + agv.error + '</p>';
    } else {
      agc!.innerHTML =
        '<div class="grid grid-cols-3 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        agv.total +
        '</div><div class="text-xs text-gray-500">Total Agents</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-purple-400">' +
        agv.orchestrators +
        '</div><div class="text-xs text-gray-500">Orchestrators</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-blue-400">' +
        agv.specialists +
        '</div><div class="text-xs text-gray-500">Specialists</div></div>' +
        '</div>' +
        '<div id="agents-table"></div>';
      const agentRows = (agv.agents || []).map((a: any) => ({
        name: a.name,
        description: (a.description || '').substring(0, 90),
        role: (a.claude_metadata || {}).role || 'specialist',
        model: (a.claude_metadata || {}).model || '-',
        tools: (a.tools || []).length ? (a.tools || []).slice(0, 6).join(', ') + (a.tools.length > 6 ? ' …' : '') : '—',
        file: a.file || '-',
      }));
      renderTable(
        'agents-table',
        [
          { key: 'name', label: 'Agent', type: 'string' },
          { key: 'description', label: 'Description', type: 'string' },
          { key: 'role', label: 'Role', type: 'string' },
          { key: 'model', label: 'Model', type: 'string' },
          { key: 'tools', label: 'Tools', type: 'string' },
          { key: 'file', label: 'File', type: 'string' },
        ],
        agentRows
      );
      // Populate agent-query selector (assumes _aqPopulateAgents exists in agents.ts)
      if ((window as any)._aqPopulateAgents) {
        (window as any)._aqPopulateAgents(agv.agents || []);
      }
    }

    // Routing tab
    const rtc = $('routing-content');
    if (rtv.error) {
      rtc!.innerHTML = '<p class="text-red-400">Error: ' + rtv.error + '</p>';
    } else {
      rtc!.innerHTML =
        '<div class="grid grid-cols-3 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        (rtv.strategies || []).length +
        '</div><div class="text-xs text-gray-500">Strategies</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        (rtv.circuit_breakers || []).length +
        '</div><div class="text-xs text-gray-500">Circuit Breakers</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' +
        (rtv.open_circuits || 0) +
        '</div><div class="text-xs text-gray-500">Open Circuits</div></div>' +
        '</div>' +
        '<h4 class="font-semibold mb-2">Strategies</h4>' +
        '<div id="routing-strategies-table"></div>' +
        '<h4 class="font-semibold mb-2">Circuit Breakers</h4>' +
        '<div id="routing-cb-table"></div>' +
        '<h4 class="font-semibold mt-4 mb-2">Budget Guards</h4>' +
        '<div id="routing-budgets-table"></div>';
      renderTable('routing-strategies-table', [{ key: 'name', label: 'Strategy', type: 'string' }], (rtv.strategies || []).map((s: string) => ({ name: s })));
      const cbRows = (rtv.circuit_breakers || []).map((cb: any) => ({
        target: cb.target,
        state: cb.state,
        failures: cb.failures,
      }));
      renderTable(
        'routing-cb-table',
        [
          { key: 'target', label: 'Target', type: 'string' },
          { key: 'state', label: 'State', type: 'string' },
          { key: 'failures', label: 'Failures', type: 'number' },
        ],
        cbRows
      );
      const budgetRows = Object.entries(rtv.budgets || {}).map(([k, v]) => ({
        guard: k,
        value: v,
      }));
      renderTable(
        'routing-budgets-table',
        [
          { key: 'guard', label: 'Guard', type: 'string' },
          { key: 'value', label: 'Value', type: 'json' },
        ],
        budgetRows
      );
    }

    // Factory tab
    const fc = $('agent-factory-content');
    if (afv.error) {
      fc!.innerHTML = '<p class="text-red-400">Error: ' + afv.error + '</p>';
    } else {
      fc!.innerHTML =
        '<div class="grid grid-cols-4 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold ' +
        (afv.factory_available ? 'text-green-400' : 'text-red-400') +
        '">' +
        (afv.factory_available ? '&#x2705;' : '&#x274c;') +
        '</div><div class="text-xs text-gray-500">Factory</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        afv.total_agents +
        '</div><div class="text-xs text-gray-500">Agent Files</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        afv.total_teams +
        '</div><div class="text-xs text-gray-500">Team Files</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        (afv.plugins || []).length +
        '</div><div class="text-xs text-gray-500">Templates</div></div>' +
        '</div>' +
        '<h4 class="font-semibold mb-2">Archetypes</h4>' +
        '<div class="flex gap-2 mb-4">' +
        (afv.archetypes || []).map((a: string) => '<span class="badge badge-standard">' + a + '</span>').join('') +
        '</div>' +
        '<h4 class="font-semibold mb-2">Agent Files</h4>' +
        '<div id="factory-agents-table"></div>' +
        '<h4 class="font-semibold mt-4 mb-2">Teams</h4>' +
        '<div id="factory-teams-table"></div>';
      const agentFileRows = (afv.agents || []).map((a: any) => ({
        name: a.name,
        size_kb: Math.round((a.size / 1024) * 10) / 10,
        lines: a.lines,
      }));
      renderTable(
        'factory-agents-table',
        [
          { key: 'name', label: 'Name', type: 'string' },
          { key: 'size_kb', label: 'Size (KB)', type: 'number' },
          { key: 'lines', label: 'Lines', type: 'number' },
        ],
        agentFileRows
      );
      renderTable(
        'factory-teams-table',
        [{ key: 'name', label: 'Team', type: 'string' }],
        (afv.teams || []).map((t: any) => ({ name: t.name }))
      );
    }

    // Prompts tab
    const pmc = $('prompts-content');
    if (pmv.error) {
      pmc!.innerHTML = '<p class="text-red-400">Error: ' + pmv.error + '</p>';
    } else {
      const promptRows: Array<{ category: string; file: string }> = [];
      Object.entries(pmv.plugins || {}).forEach(([cat, files]) => {
        (files as any[] || []).forEach((f) => promptRows.push({ category: cat, file: f }));
      });
      pmc!.innerHTML =
        '<div class="grid grid-cols-2 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        pmv.total_templates +
        '</div><div class="text-xs text-gray-500">Template Files</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        pmv.sessions +
        '</div><div class="text-xs text-gray-500">Sessions</div></div>' +
        '</div>' +
        '<div id="prompts-table"></div>';
      renderTable(
        'prompts-table',
        [
          { key: 'category', label: 'Category', type: 'string' },
          { key: 'file', label: 'File', type: 'string' },
        ],
        promptRows
      );
    }

    // PoCs tab
    const pocContent = $('pocs-content');
    if (pocv.error) {
      pocContent!.innerHTML = '<p class="text-red-400">Error: ' + pocv.error + '</p>';
    } else {
      const byStatus = pocv.by_status || {};
      const bySeverity = pocv.by_severity || {};
      pocContent!.innerHTML =
        '<div class="grid grid-cols-2 gap-4 mb-4">' +
        '<div class="card text-center"><div class="text-2xl font-bold">' +
        (pocv.total || 0) +
        '</div><div class="text-xs text-gray-500">Total PoCs</div></div>' +
        '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' +
        (pocv.weaponized || 0) +
        '</div><div class="text-xs text-gray-500">Weaponized</div></div>' +
        '</div>' +
        '<div class="grid grid-cols-2 gap-4 mb-4">' +
        '<div class="card"><h4 class="text-xs font-semibold mb-2 text-gray-400 uppercase tracking-wide">By Status</h4>' +
        '<div class="grid grid-cols-5 gap-2 text-center">' +
        Object.entries(byStatus)
          .map(([k, v]) => '<div><div class="text-lg font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>')
          .join('') +
        '</div></div>' +
        '<div class="card"><h4 class="text-xs font-semibold mb-2 text-gray-400 uppercase tracking-wide">By Severity</h4>' +
        '<div class="grid grid-cols-5 gap-2 text-center">' +
        Object.entries(bySeverity)
          .map(([k, v]) => '<div><div class="text-lg font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>')
          .join('') +
        '</div></div>' +
        '</div>' +
        '<div id="pocs-table"></div>';
      renderTable(
        'pocs-table',
        [
          { key: 'title', label: 'Title', type: 'string' },
          { key: 'status', label: 'Status', type: 'string' },
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'is_weaponized', label: 'Weaponized', type: 'bool' },
          { key: 'reliability_score', label: 'Reliability', type: 'number' },
          { key: 'language', label: 'Language', type: 'string' },
          { key: 'source', label: 'Source', type: 'string' },
          { key: 'tags', label: 'Tags', type: 'json' },
          { key: 'created_at', label: 'Created', type: 'datetime' },
        ],
        pocv.recent || []
      );
    }

    // Findings tab
    if (!findingsv.error) {
      const ft = $('findings-total');
      if (ft) ft.textContent = String(findingsv.total || 0);
      const fc = $('findings-critical');
      if (fc) fc.textContent = String((findingsv.by_severity || {}).critical || 0);
      const fh = $('findings-high');
      if (fh) fh.textContent = String((findingsv.by_severity || {}).high || 0);
      const f24 = $('findings-24h');
      if (f24) f24.textContent = String((findingsv.trend || {}).last_24h || 0);

      const sevBadge = (s: string) => {
        const m: Record<string, string> = {
          critical: 'badge-err',
          high: 'badge-err',
          medium: 'badge-standard',
          low: 'badge-budget',
          info: 'badge-ok',
        };
        return '<span class="badge ' + (m[s] || '') + '">' + (s || '?').toUpperCase() + '</span>';
      };
      const stBadge = (s: string) =>
        '<span class="badge ' +
        (s === 'open' ? 'badge-err' : s === 'resolved' ? 'badge-ok' : 'badge-standard') +
        '">' +
        (s || '?').toUpperCase() +
        '</span>';

      renderTable(
        'findings-table',
        [
          { key: 'title', label: 'Title', type: 'string' },
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'status', label: 'Status', type: 'string' },
          { key: 'confidence', label: 'Confidence', type: 'string' },
          { key: 'location', label: 'Location', type: 'string' },
          { key: 'created_at', label: 'Created', type: 'datetime' },
        ],
        (findingsv.recent || []).map((f: any) => ({
          ...f,
          severity: sevBadge(f.severity),
          status: stBadge(f.status),
        }))
      );
    }

    // IOCs tab
    if (!iocsv.error) {
      const it = $('iocs-total');
      if (it) it.textContent = String(iocsv.total || 0);
      const ia = $('iocs-active');
      if (ia) ia.textContent = String((iocsv.by_status || {}).active || 0);
      const ih = $('iocs-high-conf');
      if (ih) ih.textContent = String((iocsv.by_confidence || {}).high || 0);
      const itt = $('iocs-types');
      if (itt) itt.textContent = String(Object.keys(iocsv.by_type || {}).length);

      const confBadge = (c: string) =>
        '<span class="badge ' +
        (c === 'high' ? 'badge-err' : c === 'medium' ? 'badge-standard' : 'badge-budget') +
        '">' +
        (c || '?').toUpperCase() +
        '</span>';

      renderTable(
        'iocs-table',
        [
          { key: 'ioc_type', label: 'Type', type: 'string' },
          { key: 'value', label: 'Value', type: 'string' },
          { key: 'confidence', label: 'Confidence', type: 'string' },
          { key: 'status', label: 'Status', type: 'string' },
          { key: 'sightings', label: 'Sightings', type: 'number' },
          { key: 'source', label: 'Source', type: 'string' },
          { key: 'created_at', label: 'Created', type: 'datetime' },
        ],
        (iocsv.recent || []).map((i: any) => ({
          ...i,
          confidence: confBadge(i.confidence),
          status: '<span class="badge ' + (i.status === 'active' ? 'badge-err' : 'badge-ok') + '">' + (i.status || '?').toUpperCase() + '</span>',
        }))
      );
    }

    // YARA tab
    if (!yarav.error) {
      const yTotal = yarav.total || 0;
      const yActive = (yarav.by_status || {}).active || 0;
      const yDet = (yarav.recent || []).reduce((s: number, r: any) => s + (r.detection_count || 0), 0);
      const ySrc = Object.keys(yarav.by_source || {}).length;
      const yt = $('yara-total');
      if (yt) yt.textContent = String(yTotal);
      const ya = $('yara-active');
      if (ya) ya.textContent = String(yActive);
      const yd = $('yara-detections');
      if (yd) yd.textContent = String(yDet);
      const ys = $('yara-sources');
      if (ys) ys.textContent = String(ySrc);

      renderTable(
        'yara-table',
        [
          { key: 'name', label: 'Rule Name', type: 'string' },
          { key: 'status', label: 'Status', type: 'string' },
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'source', label: 'Source', type: 'string' },
          { key: 'detection_count', label: 'Detections', type: 'number' },
          { key: 'false_positive_rate', label: 'FP Rate', type: 'number' },
          { key: 'created_at', label: 'Created', type: 'datetime' },
        ],
        (yarav.recent || []).map((y: any) => ({
          ...y,
          status: '<span class="badge ' + (y.status === 'active' ? 'badge-ok' : 'badge-standard') + '">' + (y.status || '?').toUpperCase() + '</span>',
        }))
      );
    }

    // Network tab
    if (!netv.error) {
      const nh = $('net-hosts');
      if (nh) nh.textContent = String((netv.hosts || {}).total || 0);
      const nc = $('net-compromised');
      if (nc) nc.textContent = String((netv.hosts || {}).compromised || 0);
      const ni = $('net-ips');
      if (ni) ni.textContent = String((netv.ip_addresses || {}).total || 0);
      const nco = $('net-countries');
      if (nco) nco.textContent = String((netv.top_countries || []).length);

      renderTable(
        'network-hosts-table',
        [
          { key: 'hostname', label: 'Hostname', type: 'string' },
          { key: 'os_name', label: 'OS', type: 'string' },
          { key: 'is_compromised', label: 'Compromised', type: 'bool' },
          { key: 'is_target', label: 'Target', type: 'bool' },
        ],
        netv.recent_hosts || []
      );
      renderTable(
        'network-ips-table',
        [
          { key: 'address', label: 'IP Address', type: 'string' },
          { key: 'version', label: 'Ver', type: 'number' },
          { key: 'is_private', label: 'Private', type: 'bool' },
          { key: 'geo_country', label: 'Country', type: 'string' },
          { key: 'last_seen_at', label: 'Last Seen', type: 'datetime' },
        ],
        netv.recent_ips || []
      );
    }

    // Intel tab
    if (!intv.error) {
      const it = $('intel-techniques');
      if (it) it.textContent = String((intv.mitre || {}).techniques || 0);
      const ic = $('intel-cve');
      if (ic) ic.textContent = String((intv.cve || {}).total || 0);
      const icw = $('intel-cwe');
      if (icw) icw.textContent = String((intv.cwe || {}).total || 0);
      const ica = $('intel-capec');
      if (ica) ica.textContent = String((intv.capec || {}).total || 0);

      renderTable(
        'intel-mitre-table',
        [
          { key: 'technique_id', label: 'ID', type: 'string' },
          { key: 'name', label: 'Name', type: 'string' },
          { key: 'tactics', label: 'Tactics', type: 'json' },
          { key: 'platforms', label: 'Platforms', type: 'json' },
          { key: 'is_sub_technique', label: 'Sub-tech', type: 'bool' },
        ],
        intv.recent_mitre || []
      );

      const cveSevBadge = (s: string) => {
        const m: Record<string, string> = { CRITICAL: 'badge-err', HIGH: 'badge-err', MEDIUM: 'badge-standard', LOW: 'badge-budget' };
        return '<span class="badge ' + (m[s] || '') + '">' + (s || '?') + '</span>';
      };

      renderTable(
        'intel-cve-table',
        [
          { key: 'cve_id', label: 'CVE ID', type: 'string' },
          { key: 'cvss_score', label: 'CVSS', type: 'number' },
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'exploit_available', label: 'Exploit', type: 'bool' },
        ],
        (intv.recent_cve || []).map((c: any) => ({
          ...c,
          severity: cveSevBadge(c.severity),
        }))
      );
    }

    // Audit tab
    if (!auditv.error) {
      const at = $('audit-total');
      if (at) at.textContent = String(auditv.total || 0);
      const alh = $('audit-last-hour');
      if (alh) alh.textContent = String(auditv.last_hour_count || 0);
      const aa = $('audit-agents');
      if (aa) aa.textContent = String(Object.keys(auditv.by_agent || {}).length);

      renderTable(
        'audit-table',
        [
          { key: 'action', label: 'Action', type: 'string' },
          { key: 'entity_type', label: 'Entity Type', type: 'string' },
          { key: 'entity_id', label: 'Entity ID', type: 'string' },
          { key: 'agent', label: 'Agent', type: 'string' },
          { key: 'resource', label: 'Resource', type: 'string' },
          { key: 'ip_address', label: 'IP', type: 'string' },
          { key: 'created_at', label: 'Timestamp', type: 'datetime' },
        ],
        auditv.recent || []
      );
    }

    // Compliance tab
    if (!compv.error) {
      const ct = $('comp-total');
      if (ct) ct.textContent = String(compv.total || 0);
      const crit = $('comp-critical');
      if (crit) crit.textContent = String((compv.by_severity || {}).critical || 0);
      const cf = $('comp-frameworks');
      if (cf) cf.textContent = String(Object.keys(compv.by_framework || {}).length);
      const ch = $('comp-high');
      if (ch) ch.textContent = String((compv.by_severity || {}).high || 0);

      renderTable(
        'compliance-table',
        [
          { key: 'rule_id', label: 'Rule ID', type: 'string' },
          { key: 'title', label: 'Title', type: 'string' },
          { key: 'framework', label: 'Framework', type: 'string' },
          { key: 'severity', label: 'Severity', type: 'string' },
          { key: 'audit_frequency', label: 'Frequency', type: 'string' },
          { key: 'retention_period_days', label: 'Retention (d)', type: 'number' },
          { key: 'created_at', label: 'Created', type: 'datetime' },
        ],
        compv.recent || []
      );
    }

    // Health tab
    const errorBanner = $('health-error');
    if (hv.error) {
      if (errorBanner) {
        errorBanner.textContent = '⚠ Health check failed: ' + hv.error;
        errorBanner.style.display = 'block';
      }
    } else {
      if (errorBanner) errorBanner.style.display = 'none';
      const db = hv.database || {};
      const px = hv.proxy || {};
      const rd = hv.redis || {};
      const oo = hv.openobserve || {};
      const localLlm: Array<{id: string; name: string; reachable: boolean}> = hv.local_llm || [];

      // Service indicators
      _setHealthDot('health-db-dot', 'health-db-detail', db.status, db.table_count ? db.table_count + ' tables' : '');
      _setHealthDot('health-redis-dot', 'health-redis-detail', rd.status, rd.used_memory_human || '');
      _setHealthDot('health-oo-dot', 'health-oo-detail', oo.status, oo.http_status ? 'HTTP ' + oo.http_status : '');
      _setHealthDot('health-proxy-dot', 'health-proxy-detail', 'ok', px.providers_enabled + ' providers');

      // Stat boxes
      const tables = $('health-tables');
      if (tables) tables.textContent = String(db.table_count ?? '—');
      const prov = $('health-providers');
      if (prov) prov.textContent = String(px.providers_enabled ?? '—');
      const provFree = $('health-providers-free');
      if (provFree) provFree.textContent = String(px.providers_free ?? '—');
      const uptimeEl = $('health-uptime');
      if (uptimeEl) {
        const secs = px.uptime_seconds;
        if (secs !== undefined) {
          const h = Math.floor(secs / 3600);
          const m = Math.floor((secs % 3600) / 60);
          const s = Math.floor(secs % 60);
          uptimeEl.textContent = h > 0 ? h + 'h ' + m + 'm' : m > 0 ? m + 'm ' + s + 's' : s + 's';
        } else {
          uptimeEl.textContent = '—';
        }
      }
      const intel = $('health-intel');
      if (intel) intel.textContent = db.intel_bootstrapped ? '✅ Yes' : '⚠ No';
      const localEl = $('health-local-llm');
      if (localEl) {
        const reachable = localLlm.filter((l: {reachable: boolean}) => l.reachable);
        localEl.textContent = reachable.length > 0 ? '✅ ' + reachable.length : '—';
      }
    }
  } catch (e) {
    console.error('Dashboard refresh error:', e);
  }
}

function _setHealthDot(dotId: string, detailId: string, status: string | undefined, detail: string): void {
  const dot = $(dotId);
  const det = $(detailId);
  const s = (status || 'unknown').toLowerCase();
  if (dot) dot.className = 'svc-indicator ' + (s === 'ok' ? 'ok' : s === 'error' ? 'error' : 'unknown');
  if (det) det.textContent = detail || s;
}

export async function cancelTask(taskId: string): Promise<void> {
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
    alert('Failed to cancel task: ' + (e instanceof Error ? e.message : String(e)));
  }
}


