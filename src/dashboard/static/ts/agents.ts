// Agent Query panel: filter, search, and run agent queries

import { $ } from './core.js';
import { renderTable } from './table.js';

interface AgentMetadata {
  role: string;
  source: string;
  model: string;
  isDefault: boolean;
}

interface Agent {
  name: string;
  description?: string;
  claude_metadata?: {
    role?: string;
    source_label?: string;
    model?: string;
    default?: boolean;
  };
  skills?: Array<{ name?: string }>;
}

interface QueryHistory {
  agent: string;
  prompt: string;
  response: string;
  ts: string;
  elapsed_ms: number;
}

let _aqHistory: QueryHistory[] = [];
let _aqAgents: Agent[] = [];

export function _aqPopulateAgents(agents: Agent[]): void {
  const seen = new Set<string>();
  _aqAgents = (agents || [])
    .filter((a) => {
      const name = String(a.name || '').trim();
      if (!name) return false;
      const key = name.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => {
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

function _aqMeta(agent: Agent): AgentMetadata {
  const meta = agent.claude_metadata || {};
  return {
    role: meta.role || 'specialist',
    source: meta.source_label || 'Unknown',
    model: meta.model || 'unknown',
    isDefault: !!meta.default,
  };
}

function _aqFillFilterSelect(id: string, values: string[], placeholder: string): void {
  const sel = $(id) as HTMLSelectElement;
  const current = sel.value;
  sel.innerHTML = '';
  const base = document.createElement('option');
  base.value = '';
  base.textContent = placeholder;
  sel.appendChild(base);
  values.forEach((v) => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    sel.appendChild(opt);
  });
  if (current && values.includes(current)) sel.value = current;
}

function _aqPopulateAgentFilters(agents: Agent[]): void {
  const roles = [...new Set(agents.map((a) => _aqMeta(a).role).filter(Boolean))].sort();
  const sources = [...new Set(agents.map((a) => _aqMeta(a).source).filter(Boolean))].sort();
  const models = [...new Set(agents.map((a) => _aqMeta(a).model).filter(Boolean))].sort();
  _aqFillFilterSelect('aq-role', roles, 'All roles');
  _aqFillFilterSelect('aq-source', sources, 'All sources');
  _aqFillFilterSelect('aq-model', models, 'All models');
}

export function _aqApplyAgentFilters(): void {
  const sel = $(('aq-agent') as unknown as string) as HTMLSelectElement;
  const current = sel.value;
  const q = ((($(('aq-agent-search') as unknown as string) as unknown as HTMLInputElement) || {}).value || '').trim().toLowerCase();
  const source = ($(('aq-source') as unknown as string) as HTMLSelectElement).value || '';
  const role = ($(('aq-role') as unknown as string) as HTMLSelectElement).value || '';
  const model = ($(('aq-model') as unknown as string) as HTMLSelectElement).value || '';

  const filtered = _aqAgents.filter((a) => {
    const meta = _aqMeta(a);
    const haystack = [
      a.name || '',
      a.description || '',
      meta.role,
      meta.source,
      meta.model,
      (a.skills || []).map((s) => s.name || '').join(' '),
    ]
      .join(' ')
      .toLowerCase();
    return (!q || haystack.includes(q)) && (!source || meta.source === source) && (!role || meta.role === role) && (!model || meta.model === model);
  });

  sel.innerHTML = '';
  if (!filtered.length) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No agents match current filters';
    sel.appendChild(opt);
    const help = $(('aq-agent-help') as unknown as string);
    if (help) help.textContent = '0 of ' + _aqAgents.length + ' agents match the current filters.';
    return;
  }

  filtered.forEach((a) => {
    const meta = _aqMeta(a);
    const opt = document.createElement('option');
    opt.value = a.name;
    opt.textContent = a.name + (meta.role === 'orchestrator' ? ' (orch)' : '') + ' · ' + meta.source + ' · ' + meta.model;
    sel.appendChild(opt);
  });

  if (current && filtered.some((a) => a.name === current)) {
    sel.value = current;
  } else {
    const preferred = filtered.find((a) => _aqMeta(a).isDefault) || filtered[0];
    sel.value = preferred.name;
  }
  const help = $(('aq-agent-help') as unknown as string);
  if (help)
    help.textContent =
      filtered.length +
      ' of ' +
      _aqAgents.length +
      ' agents shown. Filter by source, role, or model before running a query.';
}

export function _aqPopulateContextTables(models: string[]): void {
  const sel = $(('aq-context-table') as unknown as string) as HTMLSelectElement;
  while (sel.options.length > 1) sel.remove(1);
  (models || []).forEach((m) => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    sel.appendChild(opt);
  });
}

export async function runAgentQuery(): Promise<void> {
  const agentSel = $(('aq-agent') as unknown as string) as HTMLSelectElement;
  const agent = agentSel.value || 'cybersec-agent';
  const promptInput = $(('aq-prompt') as unknown as string) as HTMLTextAreaElement;
  const prompt = (promptInput.value || '').trim();
  const statusEl = $(('aq-status') as unknown as string);

  if (!prompt) {
    if (statusEl) statusEl.textContent = '⚠ Prompt is empty';
    return;
  }
  if (!agent) {
    if (statusEl) statusEl.textContent = '⚠ No agent matches the current filters';
    return;
  }

  const contextTableSel = $(('aq-context-table') as unknown as string) as HTMLSelectElement;
  const contextTable = contextTableSel.value || null;
  const rowIdsInput = $(('aq-row-ids') as unknown as string) as HTMLInputElement;
  const rowIds = (rowIdsInput.value || '')
    .split(',')
    .map((s) => parseInt(s.trim()))
    .filter((n) => !isNaN(n));

  const btn = $(('aq-submit') as unknown as string) as HTMLButtonElement;
  btn.disabled = true;
  btn.textContent = '⏳ Running…';
  if (statusEl) statusEl.textContent = 'Sending to agent "' + agent + '"…';

  const t0 = Date.now();
  try {
    const body: any = { agent, prompt };
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
      if (statusEl) statusEl.textContent = '✗ Error: ' + data.error;
    } else {
      if (statusEl) statusEl.textContent = '✓ Done in ' + (data.elapsed_ms ?? elapsed) + 'ms';
      _aqHistory.unshift({
        agent: data.agent || agent,
        prompt,
        response: data.response || '',
        ts: new Date().toLocaleTimeString(),
        elapsed_ms: data.elapsed_ms ?? elapsed,
      });
      promptInput.value = '';
      _aqRenderHistory();
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
  } finally {
    btn.disabled = false;
    btn.textContent = '▶ Run Query';
  }
}

function _aqRenderHistory(): void {
  const el = $(('aq-history') as unknown as string);
  if (!el) return;
  if (!_aqHistory.length) {
    el.innerHTML = '<p class="text-xs text-gray-600">No queries yet.</p>';
    return;
  }
  el.innerHTML = _aqHistory.map((h) => {
    const resp = (h.response || '').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    return (
      '<div class="border border-gray-700 rounded-lg p-4 bg-gray-900">' +
      '<div class="flex justify-between items-start mb-2">' +
      '<span class="text-xs font-semibold text-cyan-400">' +
      h.agent +
      '</span>' +
      '<span class="text-xs text-gray-600">' +
      h.ts +
      ' · ' +
      h.elapsed_ms +
      'ms</span>' +
      '</div>' +
      '<div class="text-xs text-gray-300 font-mono mb-3 whitespace-pre-wrap border-l-2 border-cyan-800 pl-3">' +
      (h.prompt.replace(/</g, '&lt;')) +
      '</div>' +
      '<div class="text-sm text-gray-100 font-mono whitespace-pre-wrap leading-relaxed">' +
      resp +
      '</div>' +
      '</div>'
    );
  }).join('');
}

export function clearAgentHistory(): void {
  _aqHistory = [];
  _aqRenderHistory();
  const status = $(('aq-status') as unknown as string);
  if (status) status.textContent = '';
}
