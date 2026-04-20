// crud_ops.ts — CRUD operations for Cases, Tasks, PoCs, A2A, Investigations, Findings, IOCs, Prompts, Intel Sources

// ── Helpers ──────────────────────────────────────────────────────────────────

async function _cf(method: string, url: string, body?: object): Promise<{ ok: boolean; data: Record<string, unknown> }> {
  const res = await fetch(url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({})) as Record<string, unknown>;
  return { ok: res.ok, data };
}

function _show(id: string): void { const el = document.getElementById(id); if (el) el.style.display = 'flex'; }
function _hide(id: string): void { const el = document.getElementById(id); if (el) el.style.display = 'none'; }
function _val(id: string): string { return ((document.getElementById(id) as HTMLInputElement)?.value ?? '').trim(); }
function _set(id: string, v: string): void { const el = document.getElementById(id) as HTMLInputElement; if (el) el.value = v; }
function _esc(s: unknown): string { return String(s ?? '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;'); }

function _renderTable(
  tableId: string,
  cols: string[],
  rows: Record<string, unknown>[],
  actionsFn?: (row: Record<string, unknown>) => string
): void {
  const el = document.getElementById(tableId);
  if (!el) return;
  if (!rows.length) { el.innerHTML = '<p style="font-size:12px;color:var(--text-muted);padding:8px">No records found.</p>'; return; }
  const headers = [...cols, ...(actionsFn ? [''] : [])].map(c =>
    `<th style="text-align:left;padding:6px 8px;font-size:11px;color:var(--text-muted);font-family:var(--font-mono)">${c}</th>`
  ).join('');
  const body = rows.map(row => {
    const cells = cols.map(c =>
      `<td style="padding:6px 8px;font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${_esc(row[c])}">${_esc(row[c])}</td>`
    ).join('');
    const actions = actionsFn ? `<td style="padding:6px 8px;white-space:nowrap">${actionsFn(row)}</td>` : '';
    return `<tr style="border-bottom:1px solid var(--border)">${cells}${actions}</tr>`;
  }).join('');
  el.innerHTML = `<table style="width:100%;border-collapse:collapse">
    <thead><tr style="border-bottom:1px solid var(--border)">${headers}</tr></thead>
    <tbody>${body}</tbody></table>`;
}

// ── Cases ─────────────────────────────────────────────────────────────────────

let _caseId: number | null = null;

export function caseCreate(): void {
  _caseId = null; _set('cm-title',''); _set('cm-problem',''); _set('cm-hypothesis',''); _show('cases-modal');
}
export function caseEdit(id: number, title: string, problem: string, hypothesis: string): void {
  _caseId = id; _set('cm-title', title); _set('cm-problem', problem); _set('cm-hypothesis', hypothesis); _show('cases-modal');
}
export async function caseSave(): Promise<void> {
  const body = { title: _val('cm-title'), problem_statement: _val('cm-problem'), attack_hypothesis: _val('cm-hypothesis'), severity: _val('cm-severity') };
  const { ok } = _caseId ? await _cf('PATCH', `/api/cases/${_caseId}`, body) : await _cf('POST', '/api/cases', body);
  if (ok) { _hide('cases-modal'); loadCases(); }
}
export async function caseDelete(id: number): Promise<void> {
  if (!confirm('Delete case?')) return;
  const { ok } = await _cf('DELETE', `/api/cases/${id}`);
  if (ok) loadCases();
}
export async function loadCases(): Promise<void> {
  try {
    const res = await fetch('/api/cases'); const data = await res.json();
    _renderTable('cases-table', ['id','title','created_at'], data.recent || [], row =>
      `<button class="btn btn-xs" onclick="caseEdit(${row.id},'${_esc(row.title)}','${_esc(row.problem_statement)}','${_esc(row.attack_hypothesis)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="caseDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadCases:', e); }
}
export function filterCases(): void { _clientFilter('cases-search', 'cases-table'); }

// ── Tasks ─────────────────────────────────────────────────────────────────────

let _taskId: string | null = null;

export function taskCreate(): void { _taskId = null; _set('tm-session',''); _show('tasks-modal'); }
export function taskEdit(id: string, session: string, state: string): void {
  _taskId = id; _set('tm-session', session); _set('tm-state', state); _show('tasks-modal');
}
export async function taskSave(): Promise<void> {
  const body = { session_id: _val('tm-session') || undefined, state: _val('tm-state') };
  const { ok } = _taskId ? await _cf('PATCH', `/api/tasks/${_taskId}`, body) : await _cf('POST', '/api/tasks', body);
  if (ok) { _hide('tasks-modal'); loadTasks(); }
}
export async function taskDelete(id: string): Promise<void> {
  if (!confirm('Delete task?')) return;
  const { ok } = await _cf('DELETE', `/api/tasks/${id}`);
  if (ok) loadTasks();
}
export async function loadTasks(): Promise<void> {
  try {
    const res = await fetch('/api/tasks-list'); const data = await res.json();
    _renderTable('tasks-table', ['id','state','session_id','updated_at'], data.tasks || [], row =>
      `<button class="btn btn-xs" onclick="taskEdit('${_esc(row.id)}','${_esc(row.session_id)}','${_esc(row.state)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="taskDelete('${_esc(row.id)}')">Del</button>`
    );
  } catch (e) { console.error('loadTasks:', e); }
}
export function filterTasks(): void { _clientFilter('tasks-search', 'tasks-table'); }

// ── PoCs ──────────────────────────────────────────────────────────────────────

let _pocId: number | null = null;

export function pocCreate(): void { _pocId = null; _set('pm-title',''); _set('pm-url',''); _set('pm-source',''); _set('pm-lang',''); _set('pm-desc',''); _show('pocs-modal'); }
export function pocEdit(id: number, title: string, url: string, source: string): void {
  _pocId = id; _set('pm-title', title); _set('pm-url', url); _set('pm-source', source); _show('pocs-modal');
}
export async function pocSave(): Promise<void> {
  const body = { title: _val('pm-title'), poc_url: _val('pm-url'), source: _val('pm-source'), language: _val('pm-lang'), severity: _val('pm-severity') || undefined, description: _val('pm-desc') };
  const { ok } = _pocId ? await _cf('PATCH', `/api/pocs/${_pocId}`, body) : await _cf('POST', '/api/pocs', body);
  if (ok) { _hide('pocs-modal'); loadPocs(); }
}
export async function pocDelete(id: number): Promise<void> {
  if (!confirm('Delete PoC?')) return;
  const { ok } = await _cf('DELETE', `/api/pocs/${id}`);
  if (ok) loadPocs();
}
export async function loadPocs(): Promise<void> {
  try {
    const res = await fetch('/api/pocs'); const data = await res.json();
    _renderTable('pocs-table', ['id','title','source','severity','created_at'], data.recent || [], row =>
      `<button class="btn btn-xs" onclick="pocEdit(${row.id},'${_esc(row.title)}','${_esc(row.poc_url)}','${_esc(row.source)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="pocDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadPocs:', e); }
}
export function filterPocs(): void { _clientFilter('pocs-search', 'pocs-table'); }

// ── A2A Tasks ─────────────────────────────────────────────────────────────────

let _a2aId: string | null = null;

export function a2aTaskCreate(): void { _a2aId = null; _set('am-session',''); _show('a2a-modal'); }
export function a2aTaskEdit(id: string, session: string, state: string): void {
  _a2aId = id; _set('am-session', session); _set('am-state', state); _show('a2a-modal');
}
export async function a2aTaskSave(): Promise<void> {
  const body = { session_id: _val('am-session') || undefined, state: _val('am-state') };
  const { ok } = _a2aId ? await _cf('PATCH', `/api/a2a/tasks/${_a2aId}`, body) : await _cf('POST', '/api/a2a/tasks', body);
  if (ok) { _hide('a2a-modal'); loadA2aTasks(); }
}
export async function a2aTaskDelete(id: string): Promise<void> {
  if (!confirm('Delete A2A task?')) return;
  const { ok } = await _cf('DELETE', `/api/a2a/tasks/${id}`);
  if (ok) loadA2aTasks();
}
export async function loadA2aTasks(): Promise<void> {
  try {
    const res = await fetch('/api/a2a/tasks'); const data = await res.json();
    _renderTable('a2a-table', ['id','state','session_id','updated_at'], data.tasks || [], row =>
      `<button class="btn btn-xs" onclick="a2aTaskEdit('${_esc(row.id)}','${_esc(row.session_id)}','${_esc(row.state)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="a2aTaskDelete('${_esc(row.id)}')">Del</button>`
    );
  } catch (e) { console.error('loadA2aTasks:', e); }
}
export function filterA2a(): void { _clientFilter('a2a-search', 'a2a-table'); }

// ── Investigations ────────────────────────────────────────────────────────────

let _invId: number | null = null;

export function invCreate(): void { _invId = null; _set('ivm-name',''); _set('ivm-desc',''); _set('ivm-agent','cybersec-agent'); _show('inv-modal'); }
export function invEdit(id: number, name: string, desc: string, agent: string, mode: string, phase: string): void {
  _invId = id; _set('ivm-name', name); _set('ivm-desc', desc); _set('ivm-agent', agent); _set('ivm-mode', mode); _set('ivm-phase', phase); _show('inv-modal');
}
export async function invSave(): Promise<void> {
  const body = { name: _val('ivm-name'), description: _val('ivm-desc'), agent: _val('ivm-agent'), mode: _val('ivm-mode'), phase: _val('ivm-phase') };
  const { ok } = _invId ? await _cf('PATCH', `/api/investigations/${_invId}`, body) : await _cf('POST', '/api/investigations', body);
  if (ok) { _hide('inv-modal'); loadInvestigations(); }
}
export async function invDelete(id: number): Promise<void> {
  if (!confirm('Archive investigation?')) return;
  const { ok } = await _cf('DELETE', `/api/investigations/${id}`);
  if (ok) loadInvestigations();
}
export async function loadInvestigations(): Promise<void> {
  try {
    const res = await fetch('/api/investigations'); const data = await res.json();
    _renderTable('investigations-table', ['id','name','phase','agent','created_at'], data.recent || [], row =>
      `<button class="btn btn-xs" onclick="invEdit(${row.id},'${_esc(row.name)}','${_esc(row.description)}','${_esc(row.agent)}','${_esc(row.mode)}','${_esc(row.phase)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="invDelete(${row.id as number})">Archive</button>`
    );
  } catch (e) { console.error('loadInvestigations:', e); }
}
export function filterInv(): void { _clientFilter('inv-search', 'investigations-table'); }

// ── Findings ──────────────────────────────────────────────────────────────────

let _findingId: number | null = null;

export function findingCreate(): void { _findingId = null; _set('fm-title',''); _set('fm-location',''); _set('fm-desc',''); _show('findings-modal'); }
export function findingEdit(id: number, title: string, severity: string, status: string, location: string): void {
  _findingId = id; _set('fm-title', title); _set('fm-severity', severity); _set('fm-status', status); _set('fm-location', location); _show('findings-modal');
}
export async function findingSave(): Promise<void> {
  const body = { title: _val('fm-title'), severity: _val('fm-severity'), status: _val('fm-status'), confidence: _val('fm-confidence'), location: _val('fm-location'), description: _val('fm-desc') };
  const { ok } = _findingId ? await _cf('PATCH', `/api/findings/${_findingId}`, body) : await _cf('POST', '/api/findings', body);
  if (ok) { _hide('findings-modal'); loadFindings(); }
}
export async function findingDelete(id: number): Promise<void> {
  if (!confirm('Delete finding?')) return;
  const { ok } = await _cf('DELETE', `/api/findings/${id}`);
  if (ok) loadFindings();
}
export async function loadFindings(): Promise<void> {
  try {
    const res = await fetch('/api/findings'); const data = await res.json();
    _renderTable('findings-table', ['id','title','severity','status','created_at'], data.recent || [], row =>
      `<button class="btn btn-xs" onclick="findingEdit(${row.id},'${_esc(row.title)}','${_esc(row.severity)}','${_esc(row.status)}','${_esc(row.location)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="findingDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadFindings:', e); }
}
export function filterFindings(): void { _clientFilter('findings-search', 'findings-table'); }

// ── IOCs ──────────────────────────────────────────────────────────────────────

let _iocId: number | null = null;

export function iocCreate(): void { _iocId = null; _set('iocm-value',''); _set('iocm-source',''); _show('iocs-modal'); }
export function iocEdit(id: number, type: string, value: string, confidence: string, source: string): void {
  _iocId = id; _set('iocm-type', type); _set('iocm-value', value); _set('iocm-confidence', confidence); _set('iocm-source', source); _show('iocs-modal');
}
export async function iocSave(): Promise<void> {
  const body = { ioc_type: _val('iocm-type'), value: _val('iocm-value'), confidence: _val('iocm-confidence'), source: _val('iocm-source') };
  const { ok } = _iocId ? await _cf('PATCH', `/api/iocs/${_iocId}`, body) : await _cf('POST', '/api/iocs', body);
  if (ok) { _hide('iocs-modal'); loadIocs(); }
}
export async function iocDelete(id: number): Promise<void> {
  if (!confirm('Delete IOC?')) return;
  const { ok } = await _cf('DELETE', `/api/iocs/${id}`);
  if (ok) loadIocs();
}
export async function loadIocs(): Promise<void> {
  try {
    const res = await fetch('/api/iocs'); const data = await res.json();
    _renderTable('iocs-table', ['id','ioc_type','value','confidence','created_at'], data.recent || [], row =>
      `<button class="btn btn-xs" onclick="iocEdit(${row.id},'${_esc(row.ioc_type)}','${_esc(row.value)}','${_esc(row.confidence)}','${_esc(row.source)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="iocDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadIocs:', e); }
}
export function filterIocs(): void { _clientFilter('iocs-search', 'iocs-table'); }

// ── Prompts ───────────────────────────────────────────────────────────────────

let _promptId: number | null = null;

export function promptCreate(): void { _promptId = null; _set('prm-name',''); _set('prm-content',''); _show('prompts-modal'); }
export function promptEdit(id: number, name: string, category: string, content: string): void {
  _promptId = id; _set('prm-name', name); _set('prm-category', category); _set('prm-content', content); _show('prompts-modal');
}
export async function promptSave(): Promise<void> {
  const body = { name: _val('prm-name'), category: _val('prm-category'), content: _val('prm-content') };
  const { ok } = _promptId ? await _cf('PATCH', `/api/prompts/${_promptId}`, body) : await _cf('POST', '/api/prompts', body);
  if (ok) { _hide('prompts-modal'); loadPrompts(); }
}
export async function promptDelete(id: number): Promise<void> {
  if (!confirm('Delete prompt?')) return;
  const { ok } = await _cf('DELETE', `/api/prompts/${id}`);
  if (ok) loadPrompts();
}
export async function loadPrompts(): Promise<void> {
  try {
    const res = await fetch('/api/prompts-list'); const data = await res.json();
    _renderTable('prompts-table', ['id','name','category','is_active'], data.prompts || [], row =>
      `<button class="btn btn-xs" onclick="promptEdit(${row.id},'${_esc(row.name)}','${_esc(row.category)}','${_esc(row.content)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="promptDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadPrompts:', e); }
}
export function filterPrompts(): void { _clientFilter('prompts-search', 'prompts-table'); }

// ── Intel Sources ─────────────────────────────────────────────────────────────

let _intelSrcId: number | null = null;

export function intelSourceCreate(): void { _intelSrcId = null; _set('ism-name',''); _set('ism-url',''); _set('ism-desc',''); _show('intel-src-modal'); }
export function intelSourceEdit(id: number, name: string, url: string, type: string, desc: string): void {
  _intelSrcId = id; _set('ism-name', name); _set('ism-url', url); _set('ism-type', type); _set('ism-desc', desc); _show('intel-src-modal');
}
export async function intelSourceSave(): Promise<void> {
  const body = { name: _val('ism-name'), url: _val('ism-url'), feed_type: _val('ism-type'), description: _val('ism-desc') };
  const { ok } = _intelSrcId ? await _cf('PATCH', `/api/intel-sources/${_intelSrcId}`, body) : await _cf('POST', '/api/intel-sources', body);
  if (ok) { _hide('intel-src-modal'); loadIntelSources(); }
}
export async function intelSourceDelete(id: number): Promise<void> {
  if (!confirm('Remove intel source?')) return;
  const { ok } = await _cf('DELETE', `/api/intel-sources/${id}`);
  if (ok) loadIntelSources();
}
export async function loadIntelSources(): Promise<void> {
  try {
    const res = await fetch('/api/intel-sources'); const data = await res.json();
    _renderTable('intel-sources-table', ['id','name','url','feed_type','is_active'], data.sources || [], row =>
      `<button class="btn btn-xs" onclick="intelSourceEdit(${row.id},'${_esc(row.name)}','${_esc(row.url)}','${_esc(row.feed_type)}','${_esc(row.description)}')">Edit</button>
       <button class="btn btn-xs btn-danger" onclick="intelSourceDelete(${row.id as number})">Del</button>`
    );
  } catch (e) { console.error('loadIntelSources:', e); }
}
export function filterIntelSources(): void { _clientFilter('intel-src-search', 'intel-sources-table'); }

export async function seedIntelSources(): Promise<void> {
  const { ok, data } = await _cf('POST', '/api/intel-sources/seed');
  if (ok) { alert(`Seeded ${(data as Record<string,unknown>).seeded} sources`); loadIntelSources(); }
}

// ── Client-side filter helper ─────────────────────────────────────────────────

function _clientFilter(inputId: string, tableId: string): void {
  const q = ((document.getElementById(inputId) as HTMLInputElement)?.value ?? '').toLowerCase();
  const table = document.getElementById(tableId);
  if (!table) return;
  table.querySelectorAll('tbody tr').forEach(row => {
    (row as HTMLElement).style.display = row.textContent?.toLowerCase().includes(q) ? '' : 'none';
  });
}
