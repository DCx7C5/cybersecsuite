// Workflow builder and executor

import { $ } from './core.js';

export interface WorkflowStep {
  id: string;
  agent: string;
  prompt: string;
  depends_on?: string[];
  status?: 'pending' | 'completed' | 'failed' | 'skipped';
  result?: string;
  error?: string;
  elapsed_ms?: number;
}

export interface WorkflowResult {
  id?: string;
  name: string;
  status: 'pending' | 'completed' | 'failed';
  steps: WorkflowStep[];
}

let _wfStepIdx = 0;

export function wfAddStep(): void {
  const i = _wfStepIdx++;
  const div = document.createElement('div');
  div.id = 'wf-step-' + i;
  div.className = 'bg-gray-900 border border-gray-700 rounded-lg px-4 py-3';

  const existingIds: string[] = [];
  document.querySelectorAll('[id^="wf-step-"]').forEach((el) => {
    const inp = el.querySelector('.wf-step-id') as HTMLInputElement | null;
    if (inp && inp.value) existingIds.push(inp.value);
  });

  const depOpts = existingIds.map((id) => '<option value="' + id + '">' + id + '</option>').join('');
  div.innerHTML =
    '<div class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2">' +
    '<div><label class="text-xs text-gray-400 block mb-1">Step ID</label>' +
    '<input class="wf-step-id w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" value="step-' +
    (i + 1) +
    '"></div>' +
    '<div><label class="text-xs text-gray-400 block mb-1">Agent</label>' +
    '<input class="wf-step-agent w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" placeholder="agent-name" list="wf-agent-list"></div>' +
    '<div><label class="text-xs text-gray-400 block mb-1">Depends On</label>' +
    '<select class="wf-step-deps w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded" multiple><option value="">none</option>' +
    depOpts +
    '</select></div>' +
    '<div class="flex items-end"><button onclick="document.getElementById(\'wf-step-' +
    i +
    '\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕ Remove</button></div>' +
    '</div>' +
    '<div><label class="text-xs text-gray-400 block mb-1">Prompt</label>' +
    '<textarea class="wf-step-prompt w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono resize-y" rows="2" placeholder="Analyze the target system..."></textarea></div>';

  const stepsContainer = $('wf-steps');
  if (stepsContainer) stepsContainer.appendChild(div);
}

export function wfClear(): void {
  const stepsEl = $('wf-steps');
  if (stepsEl) stepsEl.innerHTML = '';
  const nameEl = $('wf-name') as HTMLInputElement | null;
  if (nameEl) nameEl.value = '';
  _wfStepIdx = 0;
}

export async function wfExecute(): Promise<void> {
  const statusEl = $('wf-status');
  const nameEl = $('wf-name') as HTMLInputElement | null;
  const name = (nameEl?.value || '').trim();

  if (!statusEl) return;

  if (!name) {
    statusEl.textContent = '✗ Enter workflow name';
    statusEl.style.color = '#f87171';
    return;
  }

  const steps: WorkflowStep[] = [];
  document.querySelectorAll('[id^="wf-step-"]').forEach((el) => {
    const idInput = el.querySelector('.wf-step-id') as HTMLInputElement | null;
    const agentInput = el.querySelector('.wf-step-agent') as HTMLInputElement | null;
    const promptInput = el.querySelector('.wf-step-prompt') as HTMLTextAreaElement | null;
    const depsSelect = el.querySelector('.wf-step-deps') as HTMLSelectElement | null;

    const id = idInput?.value.trim() || '';
    const agent = agentInput?.value.trim() || '';
    const prompt = promptInput?.value.trim() || '';
    const deps = depsSelect
      ? Array.from(depsSelect.selectedOptions)
          .map((o) => o.value)
          .filter(Boolean)
      : [];

    if (id && agent && prompt) steps.push({ id, agent, prompt, depends_on: deps });
  });

  if (!steps.length) {
    statusEl.textContent = '✗ Add at least one step';
    statusEl.style.color = '#f87171';
    return;
  }

  statusEl.textContent = '⏳ Executing...';
  statusEl.style.color = '#fbbf24';

  try {
    const res = await fetch('/api/workflows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, steps, execute: true }),
    });
    const data: WorkflowResult = await res.json();

    if (!res.ok) {
      statusEl.textContent = '✗ ' + ((data as any).error || 'Failed');
      statusEl.style.color = '#f87171';
      return;
    }

    statusEl.textContent = '✓ ' + data.status;
    statusEl.style.color = data.status === 'completed' ? '#34d399' : '#f87171';
    wfRenderResult(data);
  } catch (e) {
    statusEl.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
    statusEl.style.color = '#f87171';
  }
}

export function wfRenderResult(wf: WorkflowResult): void {
  const history = $('wf-history');
  if (!history) return;

  const card = document.createElement('div');
  card.className = 'bg-gray-900 border border-gray-700 rounded-lg p-4';

  const statusBadge =
    wf.status === 'completed'
      ? '<span class="badge badge-ok">completed</span>'
      : '<span class="badge badge-error">' + wf.status + '</span>';

  let stepsHtml = '';
  (wf.steps || []).forEach((s) => {
    const sBadge =
      s.status === 'completed' ? '✓' : s.status === 'failed' ? '✗' : s.status === 'skipped' ? '⊘' : '?';
    const sColor =
      s.status === 'completed' ? 'text-green-400' : s.status === 'failed' ? 'text-red-400' : 'text-gray-500';

    stepsHtml +=
      '<div class="mb-2 border-b border-gray-800 pb-2">' +
      '<div class="flex items-center gap-2 mb-1">' +
      '<span class="' +
      sColor +
      ' font-mono text-xs">' +
      sBadge +
      ' ' +
      s.id +
      '</span>' +
      '<span class="text-gray-500 text-xs">(' +
      s.agent +
      ', ' +
      (s.elapsed_ms || 0) +
      'ms)</span></div>';

    if (s.result) stepsHtml += '<pre class="text-xs text-gray-300 whitespace-pre-wrap max-h-32 overflow-y-auto">' + ((s.result || '').substring(0, 1000) as string) + '</pre>';
    if (s.error) stepsHtml += '<div class="text-xs text-red-400">' + s.error + '</div>';
    stepsHtml += '</div>';
  });

  card.innerHTML =
    '<div class="flex items-center gap-2 mb-2"><strong class="text-sm">' +
    (wf.name || wf.id || 'Workflow') +
    '</strong> ' +
    statusBadge +
    '</div>' +
    stepsHtml;

  history.prepend(card);
}

export async function wfLoadAgentList(): Promise<void> {
  try {
    const res = await fetch('/api/team-agents');
    const data = await res.json();

    let dl = document.getElementById('wf-agent-list') as HTMLDataListElement | null;
    if (!dl) {
      dl = document.createElement('datalist');
      dl.id = 'wf-agent-list';
      document.body.appendChild(dl);
    }

    dl.innerHTML = ((data.agents as Array<{ name: string }>) || [])
      .map((a) => '<option value="' + (a.name || '') + '">')
      .join('');
  } catch (e) {
    console.error(e);
  }
}
