// qol.ts — QoL Output Controls panel

interface QolSettings {
  active_toggles: string[];
  scope: string;
  preset_name?: string;
  fragment_preview?: string;
  estimated_tokens?: number;
}

interface QolPreset {
  description?: string;
  enabled_toggles?: string[];
}

const _$ = (id: string): HTMLElement | null => document.getElementById(id);

export async function loadQolControls(): Promise<void> {
  try {
    const scopeEl = _$('qol-scope-select') as HTMLSelectElement | null;
    const scope = scopeEl?.value ?? 'session';
    const [settingsRes, presetsRes] = await Promise.all([
      fetch(`/api/qol?scope=${scope}`),
      fetch('/api/qol/presets'),
    ]);
    if (!settingsRes.ok) throw new Error(`HTTP ${settingsRes.status}`);
    const settings: QolSettings = await settingsRes.json();
    const presetsData = presetsRes.ok ? await presetsRes.json() : {};
    const presets: Record<string, QolPreset> = presetsData.presets ?? presetsData;
    _renderToggles(settings);
    _renderPresets(presets, settings.active_toggles);
    _renderPreview(settings.fragment_preview ?? '');
    _renderScope(settings.scope);
  } catch (e) {
    const el = _$('qol-status');
    if (el) el.textContent = `Error loading QoL settings: ${e}`;
  }
}

function _renderScope(scope: string): void {
  const el = _$('qol-scope-select') as HTMLSelectElement | null;
  if (el) el.value = scope;
}

function _renderToggles(settings: QolSettings): void {
  const container = _$('qol-toggles');
  if (!container) return;
  const allToggles = [
    ['NO_CHAT',         'No Chat',         'Suppress conversational filler and commentary.'],
    ['NO_THINKING',     'No Thinking',     'Disable visible reasoning / <thinking> blocks.'],
    ['FILE_ONLY',       'File Only',       'Output ONLY file content — nothing else may appear.'],
    ['MINIMAL_OUTPUT',  'Minimal Output',  'Keep responses as short as possible.'],
    ['NO_EXPLANATIONS', 'No Explanations', 'Skip explanations; go straight to results.'],
    ['CODE_ONLY',       'Code Only',       'Return code only — no prose or markdown wrapper.'],
    ['STRUCTURED_ONLY', 'Structured Only', 'Output structured data (JSON/YAML/tables) only.'],
    ['TOOL_CALLS_ONLY', 'Tool Calls Only', 'Respond exclusively with tool calls.'],
  ];
  container.innerHTML = allToggles.map(([key, label, desc]) => {
    const active = settings.active_toggles.includes(key);
    return `<label style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);cursor:pointer">
      <input type="checkbox" ${active ? 'checked' : ''} data-toggle="${key}"
        onchange="qolToggle('${key}', this.checked)"
        style="margin-top:2px;cursor:pointer;accent-color:var(--accent)">
      <div>
        <div style="font-size:13px;font-weight:500;color:var(--text-primary)">${label}</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px">${desc}</div>
      </div>
    </label>`;
  }).join('');
}

function _renderPresets(presets: Record<string, QolPreset>, activeToggles: string[]): void {
  const container = _$('qol-presets');
  if (!container) return;
  const names = Object.keys(presets);
  if (!names.length) { container.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No presets available.</span>'; return; }
  container.innerHTML = names.map(name => {
    const p = presets[name];
    const ptoggle = p.enabled_toggles ?? [];
    const isActive = ptoggle.length > 0 && ptoggle.every(t => activeToggles.includes(t)) && activeToggles.length === ptoggle.length;
    return `<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border)">
      <button onclick="qolApplyPreset('${name}')"
        style="font-size:11px;padding:3px 10px;background:${isActive ? 'var(--accent)' : 'var(--surface-2)'};color:${isActive ? '#000' : 'var(--text-primary)'};border:1px solid var(--border);border-radius:4px;cursor:pointer">
        ${name}
      </button>
      <span style="font-size:11px;color:var(--text-muted)">${p.description ?? ''}</span>
    </div>`;
  }).join('');
}

function _renderPreview(preview: string): void {
  const el = _$('qol-preview');
  if (!el) return;
  el.textContent = preview || '(no active toggles — no injection)';
}

export async function qolToggle(toggle: string, enabled: boolean): Promise<void> {
  try {
    const scopeEl = _$('qol-scope-select') as HTMLSelectElement | null;
    const scope = scopeEl?.value ?? 'session';
    await fetch('/api/qol', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [enabled ? 'enable' : 'disable']: [toggle], scope }),
    });
    await loadQolControls();
  } catch (e) { console.error('qolToggle:', e); }
}

export async function qolApplyPreset(name: string): Promise<void> {
  try {
    const scopeEl = _$('qol-scope-select') as HTMLSelectElement | null;
    const scope = scopeEl?.value ?? 'session';
    await fetch('/api/qol', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset: name, scope }),
    });
    await loadQolControls();
  } catch (e) { console.error('qolApplyPreset:', e); }
}

export async function qolReset(): Promise<void> {
  try {
    const scopeEl = _$('qol-scope-select') as HTMLSelectElement | null;
    const scope = scopeEl?.value ?? 'session';
    await fetch(`/api/qol?scope=${scope}`, { method: 'DELETE' });
    await loadQolControls();
  } catch (e) { console.error('qolReset:', e); }
}
