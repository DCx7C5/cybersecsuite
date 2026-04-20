// flowgraph.ts — Drawflow drag-and-drop pipeline canvas

declare const Drawflow: any;

let _editor: any = null;

interface NodeStyle { color: string; icon: string; }
const NODE_STYLES: Record<string, NodeStyle> = {
  agent:     { color: 'var(--accent)', icon: '🤖' },
  'mcp-tool':{ color: 'var(--amber)', icon: '🔧' },
  condition: { color: 'var(--violet)', icon: '⑂'  },
  merge:     { color: 'var(--success)', icon: '⊕'  },
  output:    { color: 'var(--text-muted)', icon: '◎'  },
};

function _nodeTemplate(type: string, label: string): string {
  const s = NODE_STYLES[type] || NODE_STYLES['agent'];
  return (
    `<div class="fg-node" style="font-family:var(--font-mono);padding:8px 12px;` +
    `border-top:2px solid ${s.color};min-width:140px">` +
    `<div style="font-size:10px;font-weight:600;color:${s.color};margin-bottom:4px">` +
    `${s.icon} ${type.toUpperCase()}</div>` +
    `<div style="font-size:12px;color:var(--text-primary)">${label}</div>` +
    `</div>`
  );
}

function _registerDragEvents(el: HTMLElement, type: string, label: string): void {
  el.addEventListener('dragstart', (e: DragEvent) => {
    e.dataTransfer?.setData('nodeType', type);
    e.dataTransfer?.setData('nodeLabel', label);
  });
}

export function initFlowgraph(): void {
  const container = document.getElementById('drawflow');
  if (!container) return;
  if (_editor) return; // already initialised

  _editor = new Drawflow(container);
  _editor.reroute = true;
  _editor.start();

  // Wire static palette items
  document.querySelectorAll<HTMLElement>('.fg-palette-item[data-type]').forEach((el) => {
    el.draggable = true;
    _registerDragEvents(el, el.dataset.type || 'agent', el.dataset.label || el.dataset.type || 'node');
  });

  // Drop handler
  container.addEventListener('dragover', (e: Event) => e.preventDefault());
  container.addEventListener('drop', (e: Event) => {
    const drop = e as DragEvent;
    drop.preventDefault();
    const type  = drop.dataTransfer?.getData('nodeType')  || 'agent';
    const label = drop.dataTransfer?.getData('nodeLabel') || type;
    const rect  = container.getBoundingClientRect();
    const posX  = (drop.clientX - rect.left  - (_editor.canvas_x || 0)) / (_editor.zoom || 1);
    const posY  = (drop.clientY - rect.top   - (_editor.canvas_y || 0)) / (_editor.zoom || 1);
    _editor.addNode(type, 1, 1, posX, posY, type, { label, type }, _nodeTemplate(type, label));
  });
}

export async function fgLoadAgents(): Promise<void> {
  const palette = document.getElementById('fg-palette-agents');
  if (!palette) return;
  try {
    const res  = await fetch('/api/flowgraph/agents');
    const data = await res.json();
    palette.innerHTML = '';
    (data.agents || []).forEach((agent: { name: string }) => {
      const tile = document.createElement('div');
      tile.className    = 'fg-palette-item';
      tile.draggable    = true;
      tile.dataset.type  = 'agent';
      tile.dataset.label = agent.name;
      tile.style.cssText = (
        'padding:6px 10px;margin-bottom:4px;' +
        'background:var(--surface-2);border:1px solid var(--border);' +
        'border-radius:4px;cursor:grab;font-size:12px;' +
        'font-family:var(--font-mono);color:var(--text-primary)'
      );
      tile.textContent = `🤖 ${agent.name}`;
      palette.appendChild(tile);
      _registerDragEvents(tile, 'agent', agent.name);
    });
    if (!data.agents?.length) {
      palette.innerHTML = '<span style="font-size:11px;color:var(--text-muted)">No agents found</span>';
    }
  } catch (_) {
    if (palette) palette.innerHTML = '<span style="font-size:11px;color:var(--text-muted)">Error loading agents</span>';
  }
}

export function fgClear(): void {
  if (!_editor) return;
  try { _editor.clearModuleSelected?.(); _editor.clear?.(); } catch (_) {}
}

export function fgExport(): any {
  return _editor?.export() ?? null;
}

export function fgImport(data: any): void {
  if (!_editor) return;
  try { _editor.import(data); } catch (_) {}
}

export function fgExportDialog(): void {
  if (!_editor) { alert('Canvas not initialised'); return; }
  const json = JSON.stringify(_editor.export(), null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'flowgraph.json';
  a.click();
  URL.revokeObjectURL(url);
}

export function fgImportDialog(): void {
  const inp = document.createElement('input');
  inp.type   = 'file';
  inp.accept = '.json,application/json';
  inp.onchange = () => {
    const file = inp.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const data = JSON.parse(ev.target?.result as string);
        fgImport(data);
      } catch (_) { alert('Invalid flowgraph JSON'); }
    };
    reader.readAsText(file);
  };
  inp.click();
}

export async function fgExecute(): Promise<void> {
  const logEl    = document.getElementById('fg-exec-log');
  const statusEl = document.getElementById('fg-status');

  if (!_editor) {
    if (statusEl) statusEl.textContent = 'Canvas not initialised';
    return;
  }
  const graph = _editor.export();
  if (statusEl) statusEl.textContent = 'Executing…';
  if (logEl)    logEl.textContent    = 'Starting pipeline execution…\n';

  try {
    const res  = await fetch('/api/flowgraph/execute', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ graph }),
    });
    const data = await res.json();
    if (data.error) {
      if (statusEl) statusEl.textContent = `Error: ${data.error}`;
      if (logEl)    logEl.textContent    = `Error: ${data.error}`;
      return;
    }
    const count = data.nodes_executed ?? 0;
    if (statusEl) statusEl.textContent = `Done — ${count} node${count === 1 ? '' : 's'} executed`;
    if (logEl) {
      const lines: string[] = [`Run ID: ${data.run_id}`, `Nodes executed: ${count}`, ''];
      for (const [nid, result] of Object.entries(data.results || {})) {
        lines.push(`── Node ${nid} ──`);
        lines.push(String(result));
        lines.push('');
      }
      logEl.textContent = lines.join('\n');
    }
  } catch (err: any) {
    if (statusEl) statusEl.textContent = `Error: ${err.message}`;
    if (logEl)    logEl.textContent    = `Error: ${err.message}`;
  }
}
