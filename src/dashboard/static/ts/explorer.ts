// Explorer: generic model and table viewer

import { $ } from './core.js';
import { renderTable } from './table.js';

interface TableColumn {
  name?: string;
  label?: string;
  type?: string;
}

interface ExplorerData {
  error?: string;
  total?: number;
  columns?: TableColumn[];
  rows?: Record<string, unknown>[];
}

export async function loadExplorerModels(): Promise<void> {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    const sel = $('explorer-model') as HTMLSelectElement;
    if (!sel) return;
    (data.models || []).forEach((m: string) => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.textContent = m;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error('Failed to load models', e);
  }
}

export async function loadExplorerTable(): Promise<void> {
  const modelSel = $('explorer-model') as HTMLSelectElement;
  const model = modelSel.value;
  const tableEl = $('explorer-table');
  const countEl = $('explorer-count');

  if (!model) {
    if (tableEl) tableEl.innerHTML = '';
    if (countEl) countEl.textContent = '';
    return;
  }

  if (tableEl) tableEl.innerHTML = '<div class="loading text-gray-500">Loading...</div>';

  try {
    const res = await fetch('/api/tables/' + encodeURIComponent(model) + '?limit=500');
    const data: ExplorerData = await res.json();
    if (data.error) {
      if (tableEl) tableEl.innerHTML = '<div class="text-red-400">' + data.error + '</div>';
      return;
    }

    if (countEl) countEl.textContent = (data.total || (data.rows || []).length) + ' rows';

    const schema = (data.columns || []).map((c) => ({
      key: c.name || (c as any),
      label: c.label || c.name || (c as any),
      type: (c.type || 'string') as 'string' | 'number' | 'datetime' | 'bool' | 'json',
    }));
    renderTable('explorer-table', schema, data.rows || []);
  } catch (e) {
    if (tableEl)
      tableEl.innerHTML = '<div class="text-red-400">Error: ' + (e instanceof Error ? e.message : String(e)) + '</div>';
  }
}
