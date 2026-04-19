// Agent crafter and editor

import { $ } from './core.js';
import { renderTable } from './table.js';

export interface AgentEntry {
  name?: string;
  model?: string;
  source_dir?: string;
  description?: string;
  maxTurns?: number;
  tools?: string[];
}

interface AgentFrontmatter {
  model?: string;
  maxTurns?: number;
  description?: string;
}

let _acAgents: AgentEntry[] = [];

export async function acLoadAgents(): Promise<void> {
  try {
    const res = await fetch('/api/team-agents');
    const data = await res.json();
    _acAgents = (data as any).agents || [];
    acRenderAgents(_acAgents);
  } catch (e) {
    console.error('acLoadAgents', e);
  }
}

export function acFilterAgents(): void {
  const filterEl = $('ac-filter') as HTMLInputElement | null;
  const q = (filterEl?.value || '').toLowerCase();
  const filtered = q
    ? _acAgents.filter(
        (a) =>
          (a.name || '').toLowerCase().includes(q) ||
          (a.description || '').toLowerCase().includes(q)
      )
    : _acAgents;
  acRenderAgents(filtered);
}

function acRenderAgents(agents: AgentEntry[]): void {
  const countEl = $('ac-count');
  if (countEl) countEl.textContent = agents.length + ' agents';

  renderTable(
    'ac-agents-table',
    [
      { key: 'name', label: 'Agent', type: 'string' },
      { key: 'model', label: 'Model', type: 'string' },
      { key: 'source_dir', label: 'Dir', type: 'string' },
      { key: 'description', label: 'Description', type: 'string' },
      { key: 'actions', label: '', type: 'string' },
    ],
    agents.map((a) => ({
      name: '<strong>' + (a.name || '') + '</strong>',
      model: a.model || '—',
      source_dir: a.source_dir || '—',
      description: (a.description || '').substring(0, 80) + ((a.description || '').length > 80 ? '...' : ''),
      actions:
        a.name === 'cybersec-agent'
          ? '<span class="text-gray-600 text-xs">protected</span>'
          : '<button onclick="acEditAgent(\'' +
            (a.name || '') +
            '\')" class="px-2 py-0.5 bg-cyan-800 hover:bg-cyan-700 text-xs rounded mr-1">Edit</button>' +
            '<button onclick="acDeleteAgent(\'' +
            (a.name || '') +
            '\')" class="px-2 py-0.5 bg-red-900 hover:bg-red-800 text-xs rounded">Del</button>',
    })),
    { pageSize: 15 }
  );
}

export async function acCreateAgent(): Promise<void> {
  const status = $('ac-status');
  const nameEl = $('ac-name') as HTMLInputElement | null;
  const descEl = $('ac-desc') as HTMLInputElement | null;
  const modelEl = $('ac-model') as HTMLInputElement | null;
  const maxturnsEl = $('ac-maxturns') as HTMLInputElement | null;
  const mcpEl = $('ac-mcp') as HTMLInputElement | null;
  const instructionsEl = $('ac-instructions') as HTMLTextAreaElement | null;

  const name = (nameEl?.value || '').trim();

  if (!status) return;

  if (!name) {
    status.textContent = '✗ Name required';
    status.style.color = '#f87171';
    return;
  }

  const tools: string[] = [];
  document.querySelectorAll('#ac-tools input[type=checkbox]:checked').forEach((cb) => {
    const checkbox = cb as HTMLInputElement;
    tools.push(checkbox.value);
  });

  const mcpStr = (mcpEl?.value || '').trim();
  const mcpServers = mcpStr
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  const body = {
    name,
    description: (descEl?.value || '').trim(),
    model: (modelEl?.value || '').trim() || 'sonnet',
    maxTurns: parseInt(maxturnsEl?.value || '25', 10),
    tools,
    mcpServers,
    instructions: (instructionsEl?.value || '').trim(),
  };

  if (status) {
    status.textContent = 'Creating...';
    status.style.color = '#9ca3af';
  }

  try {
    const res = await fetch('/api/agents/crud', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      if (status) {
        status.textContent = '✗ ' + ((data as any).error || 'Failed');
        status.style.color = '#f87171';
      }
      return;
    }

    if (status) {
      status.textContent = '✓ Created: ' + (data as any).agent;
      status.style.color = '#34d399';
    }

    if (nameEl) nameEl.value = '';
    if (descEl) descEl.value = '';
    if (instructionsEl) instructionsEl.value = '';

    await acLoadAgents();
    setTimeout(() => {
      if (status) status.textContent = '';
    }, 3000);
  } catch (e) {
    if (status) {
      status.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
      status.style.color = '#f87171';
    }
  }
}

export async function acEditAgent(name: string): Promise<void> {
  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name));
    const data = await res.json();

    if ((data as any).error) {
      alert((data as any).error);
      return;
    }

    const editNameEl = $('ac-edit-name') as HTMLElement & { dataset: { name?: string } };
    const editModelEl = $('ac-edit-model') as HTMLInputElement | null;
    const editMaxturnsEl = $('ac-edit-maxturns') as HTMLInputElement | null;
    const editDescEl = $('ac-edit-desc') as HTMLInputElement | null;
    const editInstructionsEl = $('ac-edit-instructions') as HTMLTextAreaElement | null;
    const editModalEl = $('ac-edit-modal') as HTMLElement | null;

    if (editNameEl) {
      editNameEl.textContent = name;
      editNameEl.dataset.name = name;
    }

    const fm = (data as any).frontmatter || {};
    if (editModelEl) editModelEl.value = fm.model || 'sonnet';
    if (editMaxturnsEl) editMaxturnsEl.value = fm.maxTurns || 25;
    if (editDescEl) editDescEl.value = fm.description || '';
    if (editInstructionsEl) editInstructionsEl.value = (data as any).body || '';
    if (editModalEl) editModalEl.style.display = '';
  } catch (e) {
    alert(e instanceof Error ? e.message : String(e));
  }
}

export function acCloseEdit(): void {
  const editModalEl = $('ac-edit-modal');
  if (editModalEl) editModalEl.style.display = 'none';
}

export async function acSaveEdit(): Promise<void> {
  const editNameEl = $('ac-edit-name') as HTMLElement & { dataset: { name?: string } };
  const name = editNameEl?.dataset.name;
  const status = $('ac-edit-status');

  if (!status || !name) return;

  const descEl = $('ac-edit-desc') as HTMLInputElement | null;
  const modelEl = $('ac-edit-model') as HTMLInputElement | null;
  const maxturnsEl = $('ac-edit-maxturns') as HTMLInputElement | null;
  const instructionsEl = $('ac-edit-instructions') as HTMLTextAreaElement | null;

  const body = {
    description: (descEl?.value || '').trim(),
    model: (modelEl?.value || '').trim(),
    maxTurns: parseInt(maxturnsEl?.value || '25', 10),
    instructions: (instructionsEl?.value || '').trim(),
  };

  status.textContent = 'Saving...';
  status.style.color = '#9ca3af';

  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      status.textContent = '✗ ' + ((data as any).error || 'Failed');
      status.style.color = '#f87171';
      return;
    }

    status.textContent = '✓ Saved';
    status.style.color = '#34d399';
    acCloseEdit();
    await acLoadAgents();
  } catch (e) {
    status.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
    status.style.color = '#f87171';
  }
}

export async function acDeleteAgent(name: string): Promise<void> {
  if (!confirm('Delete agent "' + name + '"?')) return;

  try {
    const res = await fetch('/api/agents/crud/' + encodeURIComponent(name), { method: 'DELETE' });
    const data = await res.json();

    if (!res.ok) {
      alert((data as any).error || 'Failed');
      return;
    }

    await acLoadAgents();
  } catch (e) {
    alert(e instanceof Error ? e.message : String(e));
  }
}
