// Dashboard settings management

import { $ } from './core.js';
import { renderTable } from './table.js';

interface SettingsData {
  settings?: {
    agent?: string;
    proxy?: {
      default_strategy?: string;
      enabled?: boolean;
    };
    env?: Record<string, string>;
    hooks?: Record<string, Array<{ command: string; matcher?: string }>>;
  };
}

interface MCPServer {
  name: string;
  command?: string;
  enabled?: boolean;
}

interface Skill {
  name: string;
  domain?: string;
  subdomain?: string;
  description?: string;
  tags?: string[];
  mitre_attack?: string[];
}

interface Plugin {
  id: string;
  version: string;
  scope: string;
  enabled?: boolean;
}

interface GlobalSettings {
  effortLevel?: string;
  codemossProviderId?: string;
  mcpServers?: string[];
  extraKnownMarketplaces?: string[];
  hooks?: string[];
}

let _settingsData: SettingsData = {};
let _settingsPanelsRendered = false;

function _renderSettingsPanels(): void {
  if (!_settingsPanelsRendered) {
    const settingsContent = $('settings-content');
    if (settingsContent && !document.getElementById('settings-agent-form')) {
      settingsContent.innerHTML =
        '<div class="space-y-6">' +
        '<div class="flex items-center justify-between gap-3">' +
        '<div>' +
        '<div class="text-sm font-semibold text-gray-100">Claude SDK settings</div>' +
        '<div class="text-xs text-gray-400">Editable values from .claude/settings.json</div>' +
        '</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="flex items-center justify-between gap-3">' +
        '<div class="text-sm font-semibold text-gray-100">Agent and proxy</div>' +
        '<button class="btn btn-accent text-xs" onclick="saveSettingsAgent()">Save</button>' +
        '</div>' +
        '<div id="settings-agent-form" class="space-y-3"></div>' +
        '<div id="settings-agent-status" class="text-xs font-mono"></div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="flex items-center justify-between gap-3">' +
        '<div class="text-sm font-semibold text-gray-100">Environment</div>' +
        '<div class="flex items-center gap-2">' +
        '<button class="btn btn-ghost text-xs" onclick="settingsAddEnvRow()">Add row</button>' +
        '<button class="btn btn-accent text-xs" onclick="saveSettingsEnv()">Save</button>' +
        '</div>' +
        '</div>' +
        '<div id="settings-env-rows" class="space-y-2"></div>' +
        '<div id="settings-env-status" class="text-xs font-mono"></div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Hooks</div>' +
        '<div id="settings-hooks-table"></div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Local LLM</div>' +
        '<div id="local-llm-status" class="text-xs text-gray-400 font-mono">Loading local LLM status...</div>' +
        '<div id="local-llm-providers" class="text-xs font-mono text-gray-300">Loading local providers...</div>' +
        '<div class="flex items-center gap-2">' +
        '<select id="local-llm-model" class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg flex-1"></select>' +
        '<button class="btn btn-accent text-xs" onclick="activateLocalLlm()">Activate</button>' +
        '<button class="btn btn-ghost text-xs" onclick="deactivateLocalLlm()">Use cloud</button>' +
        '</div>' +
        '</div>' +
        '</div>';
    }

    const cybersecContent = $('settings-cs-content');
    if (cybersecContent && !document.getElementById('settings-global')) {
      cybersecContent.innerHTML =
        '<div class="space-y-6">' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Global summary</div>' +
        '<div id="settings-global" class="toggles-loading text-xs font-mono text-gray-400">Loading global settings...</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Workspace MCP servers</div>' +
        '<div id="settings-mcps" class="toggles-loading text-xs font-mono text-gray-400">Loading MCP servers...</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Global MCP servers</div>' +
        '<div id="settings-global-mcps" class="toggles-loading text-xs font-mono text-gray-400">Loading global MCP servers...</div>' +
        '<div class="grid grid-cols-1 gap-2 md:grid-cols-2">' +
        '<input id="mcp-install-name" type="text" placeholder="name" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono">' +
        '<input id="mcp-install-cmd" type="text" placeholder="command" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono">' +
        '<input id="mcp-install-args" type="text" placeholder="args (comma-separated)" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono md:col-span-2">' +
        '<textarea id="mcp-install-env" rows="3" placeholder="ENV=value" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono md:col-span-2"></textarea>' +
        '</div>' +
        '<div class="flex items-center gap-2">' +
        '<button class="btn btn-accent text-xs" onclick="installMcp()">Install MCP</button>' +
        '<div id="mcp-install-status" class="text-xs font-mono"></div>' +
        '</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Skill domains</div>' +
        '<div id="settings-skills" class="toggles-loading text-xs font-mono text-gray-400">Loading skill domains...</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Plugins</div>' +
        '<div id="settings-plugins" class="toggles-loading text-xs font-mono text-gray-400">Loading plugins...</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Environment scopes</div>' +
        '<div class="flex items-center gap-2">' +
        '<button id="scope-btn-global" class="btn btn-accent text-xs" onclick="switchSettingsScope(\'global\')">Global</button>' +
        '<button id="scope-btn-project" class="btn btn-ghost text-xs" onclick="switchSettingsScope(\'project\')">Project</button>' +
        '</div>' +
        '<div id="settings-scope-global">' +
        '<div id="settings-global-env" class="toggles-loading text-xs font-mono text-gray-400">Loading global env...</div>' +
        '</div>' +
        '<div id="settings-scope-project" style="display:none">' +
        '<div id="settings-project-env" class="toggles-loading text-xs font-mono text-gray-400">Loading project env...</div>' +
        '</div>' +
        '</div>' +
        '<div class="rounded-xl border border-gray-800 bg-black/20 p-4 space-y-4">' +
        '<div class="text-sm font-semibold text-gray-100">Hooks</div>' +
        '<div id="settings-global-hooks" class="toggles-loading text-xs font-mono text-gray-400">Loading hooks...</div>' +
        '<div class="grid grid-cols-1 gap-2 md:grid-cols-2">' +
        '<select id="hook-add-event" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono">' +
        '<option value="on_start">on_start</option>' +
        '<option value="on_end">on_end</option>' +
        '<option value="on_tool_call">on_tool_call</option>' +
        '<option value="on_tool_result">on_tool_result</option>' +
        '<option value="on_error">on_error</option>' +
        '</select>' +
        '<input id="hook-add-matcher" type="text" placeholder="matcher (optional)" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono">' +
        '<input id="hook-add-cmd" type="text" placeholder="command" class="px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono md:col-span-2">' +
        '</div>' +
        '<div class="flex items-center gap-2">' +
        '<button class="btn btn-accent text-xs" onclick="addHook()">Add hook</button>' +
        '<div id="hook-add-status" class="text-xs font-mono"></div>' +
        '</div>' +
        '</div>' +
        '</div>';
    }

    _settingsPanelsRendered = true;
  }
}

export async function loadSettings(): Promise<void> {
  try {
    _renderSettingsPanels();
    await loadSettingsProjects();
    const res = await fetch('/api/settings');
    _settingsData = await res.json();
    _renderSettingsAgent();
    _renderSettingsEnv();
    _renderSettingsHooks();
    await loadLocalLlmStatus();
  } catch (e) {
    console.error('Failed to load settings', e);
  }
}

interface Project {
  id: number;
  name: string;
  path?: string;
}

export async function loadSettingsProjects(): Promise<void> {
  // Project scope selector removed — settings are now global only
}

export function switchActiveProject(_projectId: string): void {
  // No-op: project scope selector removed
}

function _inp(id: string, val: unknown, placeholder?: string): string {
  const strVal = String(val).replace(/"/g, '&quot;');
  const strPlaceholder = (placeholder || '').replace(/"/g, '&quot;');
  return (
    '<input id="' +
    id +
    '" type="text" value="' +
    strVal +
    '"' +
    ' placeholder="' +
    strPlaceholder +
    '"' +
    ' class="flex-1 px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none font-mono">'
  );
}

function _renderSettingsAgent(): void {
  const s = (_settingsData && _settingsData.settings) || {};
  const p = s.proxy || {};
  const el = $('settings-agent-form');
  if (!el) return;

  let h = '';
  h +=
    '<div class="flex items-center gap-3">' +
    '<span class="text-xs text-gray-400 w-40 shrink-0">agent</span>' +
    _inp('st-agent', s.agent || '', 'e.g. cybersec-agent') +
    '</div>';
  h +=
    '<div class="flex items-center gap-3">' +
    '<span class="text-xs text-gray-400 w-40 shrink-0">proxy.default_strategy</span>' +
    _inp('st-proxy-strategy', p.default_strategy || '', 'e.g. cost-optimized') +
    '</div>';
  h +=
    '<div class="flex items-center gap-3">' +
    '<span class="text-xs text-gray-400 w-40 shrink-0">proxy.enabled</span>' +
    '<select id="st-proxy-enabled" class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg">' +
    '<option value="true"' +
    (p.enabled !== false ? ' selected' : '') +
    '>true</option>' +
    '<option value="false"' +
    (p.enabled === false ? ' selected' : '') +
    '>false</option>' +
    '</select></div>';

  el.innerHTML = h;
}

function _renderSettingsEnv(): void {
  const env = ((_settingsData && _settingsData.settings && _settingsData.settings.env) || {}) as Record<
    string,
    string
  >;
  const rows = Object.entries(env);
  const el = $('settings-env-rows');
  if (!el) return;

  let h = '';
  rows.forEach(([k, v], i) => {
    h +=
      '<div class="flex items-center gap-2" id="env-row-' +
      i +
      '">' +
      '<input class="env-key flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" value="' +
      k.replace(/"/g, '&quot;') +
      '">' +
      '<input class="env-val flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" value="' +
      String(v).replace(/"/g, '&quot;') +
      '">' +
      '<button onclick="this.closest(\'[id^=env-row]\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>' +
      '</div>';
  });
  el.innerHTML = h;
}

export function settingsAddEnvRow(): void {
  const wrap = $('settings-env-rows');
  if (!wrap) return;
  const idx = wrap.children.length;
  const div = document.createElement('div');
  div.id = 'env-row-' + idx;
  div.className = 'flex items-center gap-2';
  div.innerHTML =
    '<input class="env-key flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" placeholder="KEY">' +
    '<input class="env-val flex-1 px-3 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded-lg font-mono" placeholder="VALUE">' +
    '<button onclick="this.closest(\'[id^=env-row]\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>';
  wrap.appendChild(div);
}

function _renderSettingsHooks(): void {
  const hooks =
    ((_settingsData && _settingsData.settings && _settingsData.settings.hooks) ||
      {}) as Record<string, Array<{ command: string; matcher?: string }>>;
  const rows = Object.entries(hooks).map(([event, entries]) => {
    const cmds = (entries || [])
      .map((e) => e.command || '')
      .join('\n');
    return { event, commands: cmds };
  });
  renderTable(
    'settings-hooks-table',
    [
      { key: 'event', label: 'Event', type: 'string' },
      { key: 'commands', label: 'Commands', type: 'string' },
    ],
    rows
  );
}

export async function saveSettingsAgent(): Promise<void> {
  const status = $('settings-agent-status');
  if (!status) return;

  try {
    const agentEl = $('st-agent') as HTMLInputElement | null;
    const strategyEl = $('st-proxy-strategy') as HTMLInputElement | null;
    const enabledEl = $('st-proxy-enabled') as HTMLSelectElement | null;

    const agent = (agentEl?.value || '').trim();
    const strategy = (strategyEl?.value || '').trim();
    const enabled = (enabledEl?.value || 'true') === 'true';
    const current = ((_settingsData && _settingsData.settings && _settingsData.settings.proxy) || {}) as Record<
      string,
      unknown
    >;

    const res = await fetch('/api/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, proxy: { ...current, default_strategy: strategy, enabled } }),
    });
    const data = await res.json();

    if ((data as any).error) {
      status.textContent = '✗ ' + (data as any).error;
      status.style.color = '#f87171';
    } else {
      status.textContent = '✓ Saved';
      status.style.color = '#34d399';
      setTimeout(() => {
        status.textContent = '';
      }, 3000);
    }
    await loadSettings();
  } catch (e) {
    status.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
    status.style.color = '#f87171';
  }
}

export async function saveSettingsEnv(): Promise<void> {
  const status = $('settings-env-status');
  if (!status) return;

  try {
    const env: Record<string, string> = {};
    document.querySelectorAll('[id^="env-row-"]').forEach((row) => {
      const kEl = row.querySelector('.env-key') as HTMLInputElement | null;
      const vEl = row.querySelector('.env-val') as HTMLInputElement | null;
      const k = (kEl?.value || '').trim();
      const v = vEl?.value || '';
      if (k) env[k] = v;
    });

    const res = await fetch('/api/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ env }),
    });
    const data = await res.json();

    if ((data as any).error) {
      status.textContent = '✗ ' + (data as any).error;
      status.style.color = '#f87171';
    } else {
      status.textContent = '✓ Saved';
      status.style.color = '#34d399';
      setTimeout(() => {
        status.textContent = '';
      }, 3000);
    }
    await loadSettings();
  } catch (e) {
    status.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
    status.style.color = '#f87171';
  }
}

export function switchSettingsScope(scope: string): void {
  const isGlobal = scope === 'global';
  const globalEl = $('settings-scope-global');
  const projectEl = $('settings-scope-project');
  const globalBtnEl = $('scope-btn-global');
  const projectBtnEl = $('scope-btn-project');

  if (globalEl) globalEl.style.display = isGlobal ? '' : 'none';
  if (projectEl) projectEl.style.display = isGlobal ? 'none' : '';
  if (globalBtnEl) globalBtnEl.className = 'btn ' + (isGlobal ? 'btn-accent' : 'btn-ghost');
  if (projectBtnEl) projectBtnEl.className = 'btn ' + (isGlobal ? 'btn-ghost' : 'btn-accent');
  if (globalBtnEl) globalBtnEl.style.fontSize = '12px';
  if (projectBtnEl) projectBtnEl.style.fontSize = '12px';
}

export async function loadSettingsToggles(): Promise<void> {
  try {
    _renderSettingsPanels();
    const [mcpRes, skillRes, pluginRes, globalRes, globalMcpRes, globalEnvRes, projectEnvRes] = await Promise.all([
      fetch('/api/settings/mcps')
        .then((r) => r.json())
        .catch(() => ({ servers: [] })),
      fetch('/api/settings/skills')
        .then((r) => r.json())
        .catch(() => ({ domains: [] })),
      fetch('/api/settings/plugins')
        .then((r) => r.json())
        .catch(() => ({ plugins: [] })),
      fetch('/api/settings/global')
        .then((r) => r.json())
        .catch(() => ({ global: {} })),
      fetch('/api/settings/global-mcps')
        .then((r) => r.json())
        .catch(() => ({ servers: [] })),
      fetch('/api/settings/global-env')
        .then((r) => r.json())
        .catch(() => ({ env: {} })),
      fetch('/api/settings/project-env')
        .then((r) => r.json())
        .catch(() => ({ env: {} })),
    ]);

    _renderMcpToggles((mcpRes as any).servers || []);
    _renderSkillToggles((skillRes as any).domains || []);
    _renderPluginToggles((pluginRes as any).plugins || []);
    _renderGlobalSummary((globalRes as any).global || {});
    _renderGlobalMcpToggles((globalMcpRes as any).servers || []);
    _renderEnvTable('settings-global-env', (globalEnvRes as any).env || {});
    _renderEnvTable('settings-project-env', (projectEnvRes as any).env || {});
    await loadGlobalHooks();
  } catch (e) {
    console.error('loadSettingsToggles:', e);
  }
}

function _toggleSwitch(id: string, checked: boolean, onchange: string): string {
  return (
    '<label class="toggle-switch" title="' +
    id +
    '">' +
    '<input type="checkbox" ' +
    (checked ? 'checked' : '') +
    ' onchange="' +
    onchange +
    '">' +
    '<span class="toggle-slider"></span>' +
    '</label>'
  );
}

function _renderMcpToggles(servers: MCPServer[]): void {
  const el = $('settings-mcps');
  if (!el) return;
  if (!servers.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No MCP servers found in mcp.json</span>';
    return;
  }
  el.innerHTML = servers
    .map(
      (s) =>
        '<div class="toggle-row">' +
        '<div><div class="toggle-label">' +
        s.name +
        '</div>' +
        '<div class="toggle-sub">' +
        (s.command || '') +
        '</div></div>' +
        _toggleSwitch('mcp-' + s.name, !!s.enabled, 'toggleMcp("' + s.name + '",this.checked)') +
        '</div>'
    )
    .join('');
}

export async function toggleMcp(name: string, enabled: boolean): Promise<void> {
  try {
    await fetch('/api/settings/mcps', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, enabled }),
    });
  } catch (e) {
    console.error('toggleMcp:', e);
  }
}

function _renderGlobalMcpToggles(servers: MCPServer[]): void {
  const el = $('settings-global-mcps');
  if (!el) return;
  if (!servers.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No MCP servers in ~/.claude/settings.json</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = servers
    .map(
      (s) =>
        '<div class="toggle-row">' +
        '<div style="flex:1"><div class="toggle-label">' +
        s.name +
        '</div>' +
        '<div class="toggle-sub">' +
        (s.command || '') +
        '</div></div>' +
        _toggleSwitch('gmcp-' + s.name, !!s.enabled, 'toggleGlobalMcp("' + s.name + '",this.checked)') +
        '<button class="btn btn-ghost" style="font-size:10px;padding:2px 8px;margin-left:8px" ' +
        'onclick="removeMcp(\'' +
        s.name +
        '\')" title="Remove from ~/.claude/settings.json">&#x2715;</button>' +
        '</div>'
    )
    .join('');
}

export async function toggleGlobalMcp(name: string, enabled: boolean): Promise<void> {
  try {
    await fetch('/api/settings/global-mcps', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, enabled }),
    });
  } catch (e) {
    console.error('toggleGlobalMcp:', e);
  }
}

function _renderEnvTable(elId: string, env: Record<string, unknown>): void {
  const el = $(elId);
  if (!el) return;
  const entries = Object.entries(env);
  if (!entries.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No env vars set</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML =
    '<div class="space-y-1">' +
    entries
      .map(
        ([k, v]) =>
          '<div style="display:flex;align-items:flex-start;gap:12px;padding:4px 0;border-bottom:1px solid var(--border)">' +
          '<span class="text-xs font-mono" style="color:var(--cyan);min-width:280px;flex-shrink:0">' +
          k +
          '</span>' +
          '<span class="text-xs font-mono" style="color:var(--text-muted);word-break:break-all">' +
          String(v) +
          '</span>' +
          '</div>'
      )
      .join('') +
    '</div>';
}

function _renderSkillToggles(domains: Array<{ name: string; skills?: number; enabled?: boolean }>): void {
  const el = $('settings-skills');
  if (!el) return;
  if (!domains.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No skill domains found</span>';
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = domains
    .map(
      (d) =>
        '<div class="toggle-row">' +
        '<div><div class="toggle-label">' +
        d.name +
        '</div>' +
        '<div class="toggle-sub">' +
        (d.skills || 0) +
        ' skills</div></div>' +
        _toggleSwitch('skill-' + d.name, !!d.enabled, 'toggleSkillDomain("' + d.name + '",this.checked)') +
        '</div>'
    )
    .join('');
}

export async function toggleSkillDomain(name: string, enabled: boolean): Promise<void> {
  try {
    await fetch('/api/settings/skills', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, enabled }),
    });
  } catch (e) {
    console.error('toggleSkillDomain:', e);
  }
}

function _renderPluginToggles(plugins: Plugin[]): void {
  const el = $('settings-plugins');
  if (!el) return;
  if (!plugins.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No plugins installed</span>';
    return;
  }
  el.innerHTML = plugins
    .map(
      (p) =>
        '<div class="toggle-row">' +
        '<div><div class="toggle-label">' +
        p.id.split('@')[0] +
        '</div>' +
        '<div class="toggle-sub">v' +
        p.version +
        ' · ' +
        p.scope +
        '</div></div>' +
        _toggleSwitch('plugin-' + p.id, !!p.enabled, 'togglePlugin("' + JSON.stringify(p.id).replace(/"/g, "'") + '",this.checked)') +
        '</div>'
    )
    .join('');
}

export async function togglePlugin(id: string, enabled: boolean): Promise<void> {
  try {
    await fetch('/api/settings/plugins', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, enabled }),
    });
  } catch (e) {
    console.error('togglePlugin:', e);
  }
}

function _renderGlobalSummary(g: GlobalSettings): void {
  const el = $('settings-global');
  if (!el) return;
  const rows = [
    { k: 'Effort Level', v: g.effortLevel || '—' },
    { k: 'Codemoss Provider', v: g.codemossProviderId ? g.codemossProviderId.substring(0, 16) + '…' : '—' },
    { k: 'Active MCP Servers', v: (g.mcpServers || []).join(', ') || '—' },
    { k: 'Marketplaces', v: (g.extraKnownMarketplaces || []).join(', ') || '—' },
    { k: 'Active Hooks', v: (g.hooks || []).join(', ') || '—' },
  ];
  el.innerHTML =
    '<div class="space-y-1">' +
    rows
      .map(
        (r) =>
          '<div style="display:flex;align-items:center;gap:12px;padding:4px 0;border-bottom:1px solid var(--border)">' +
          '<span class="text-xs font-mono" style="color:var(--text-muted);min-width:140px;flex-shrink:0">' +
          r.k +
          '</span>' +
          '<span class="text-xs font-mono" style="color:var(--text-primary)">' +
          r.v +
          '</span>' +
          '</div>'
      )
      .join('') +
    '</div>';
  el.classList.remove('toggles-loading');
}

export async function installMcp(): Promise<void> {
  const nameEl = $('mcp-install-name') as HTMLInputElement | null;
  const cmdEl = $('mcp-install-cmd') as HTMLInputElement | null;
  const argsEl = $('mcp-install-args') as HTMLInputElement | null;
  const envEl = $('mcp-install-env') as HTMLInputElement | null;
  const st = $('mcp-install-status');

  const name = (nameEl?.value || '').trim();
  const cmd = (cmdEl?.value || '').trim();
  const argsStr = (argsEl?.value || '').trim();
  const envStr = (envEl?.value || '').trim();

  if (!name || !cmd) {
    if (st) {
      st.textContent = '✗ Name and command are required';
      st.style.color = 'var(--red)';
    }
    return;
  }

  const args = argsStr
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  const env: Record<string, string> = {};
  if (envStr) {
    envStr.split('\n').forEach((line) => {
      const eqIdx = line.indexOf('=');
      if (eqIdx > 0) {
        const k = line.slice(0, eqIdx).trim();
        const v = line.slice(eqIdx + 1).trim();
        if (k) env[k] = v;
      }
    });
  }

  if (st) {
    st.textContent = 'Installing…';
    st.style.color = 'var(--text-muted)';
  }

  try {
    const d = await fetch('/api/settings/install-mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, command: cmd, args, env }),
    }).then((r) => r.json());

    if ((d as any).error) {
      if (st) {
        st.textContent = '✗ ' + (d as any).error;
        st.style.color = 'var(--red)';
      }
      return;
    }

    if (st) {
      st.textContent = '✓ Installed: ' + name;
      st.style.color = 'var(--success)';
    }

    ['mcp-install-name', 'mcp-install-cmd', 'mcp-install-args', 'mcp-install-env'].forEach((id) => {
      const el = $(id) as HTMLInputElement | null;
      if (el) el.value = '';
    });

    const globalRes = await fetch('/api/settings/global-mcps').then((r) => r.json());
    _renderGlobalMcpToggles((globalRes as any).servers || []);
  } catch (e) {
    if (st) {
      st.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
      st.style.color = 'var(--red)';
    }
  }
}

export async function removeMcp(name: string): Promise<void> {
  if (!confirm('Remove MCP server "' + name + '" from ~/.claude/settings.json?')) return;
  try {
    const d = await fetch('/api/settings/remove-mcp', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }).then((r) => r.json());

    if ((d as any).error) {
      alert('Error: ' + (d as any).error);
      return;
    }

    const globalRes = await fetch('/api/settings/global-mcps').then((r) => r.json());
    _renderGlobalMcpToggles((globalRes as any).servers || []);
  } catch (e) {
    alert('Error: ' + (e instanceof Error ? e.message : String(e)));
  }
}

export async function loadGlobalHooks(): Promise<void> {
  try {
    const d = await fetch('/api/settings/hooks').then((r) => r.json());
    _renderHooksList((d as any).hooks || {});
  } catch (e) {
    console.error('loadGlobalHooks:', e);
  }
}

function _renderHooksList(
  hooks: Record<string, Array<{ command: string; matcher?: string }>>
): void {
  const el = $('settings-global-hooks');
  if (!el) return;
  const events = Object.keys(hooks);
  if (!events.length) {
    el.innerHTML = '<span class="text-xs font-mono" style="color:var(--text-muted)">No hooks defined in ~/.claude/settings.json</span>';
    el.classList.remove('toggles-loading');
    return;
  }
  el.classList.remove('toggles-loading');
  el.innerHTML = events
    .map(
      (event) =>
        '<div style="margin-bottom:12px">' +
        '<div style="font-size:11px;font-weight:600;font-family:var(--font-mono);color:var(--cyan);margin-bottom:6px">' +
        event +
        '</div>' +
        (hooks[event] || [])
          .map(
            (h) =>
              '<div class="toggle-row" style="padding:6px 0">' +
              '<div>' +
              '<div class="toggle-label" style="font-size:11px">' +
              h.command +
              '</div>' +
              (h.matcher ? '<div class="toggle-sub">matcher: ' + h.matcher + '</div>' : '') +
              '</div>' +
              '<button class="btn btn-ghost" style="font-size:10px;padding:2px 8px" ' +
              'onclick="removeHook(\'' +
              event +
              "','" +
              h.command.replace(/\\/g, '\\\\').replace(/'/g, "\\'") +
              '\')">' +
              '✕ Remove</button>' +
              '</div>'
          )
          .join('') +
        '</div>'
    )
    .join('');
}

export async function addHook(): Promise<void> {
  const eventEl = $('hook-add-event') as HTMLSelectElement | null;
  const matcherEl = $('hook-add-matcher') as HTMLInputElement | null;
  const cmdEl = $('hook-add-cmd') as HTMLInputElement | null;
  const st = $('hook-add-status');

  const event = eventEl?.value || '';
  const matcher = (matcherEl?.value || '').trim();
  const command = (cmdEl?.value || '').trim();

  if (!command) {
    if (st) {
      st.textContent = '✗ Command required';
      st.style.color = 'var(--red)';
    }
    return;
  }

  if (st) {
    st.textContent = 'Adding…';
    st.style.color = 'var(--text-muted)';
  }

  try {
    const d = await fetch('/api/settings/hooks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, command, matcher: matcher || undefined }),
    }).then((r) => r.json());

    if ((d as any).error) {
      if (st) {
        st.textContent = '✗ ' + (d as any).error;
        st.style.color = 'var(--red)';
      }
      return;
    }

    if (st) {
      st.textContent = '✓ Hook added';
      st.style.color = 'var(--success)';
    }

    if (cmdEl) cmdEl.value = '';
    if (matcherEl) matcherEl.value = '';

    await loadGlobalHooks();
  } catch (e) {
    if (st) {
      st.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
      st.style.color = 'var(--red)';
    }
  }
}

export async function removeHook(event: string, command: string): Promise<void> {
  if (!confirm('Remove hook from ' + event + '?')) return;
  try {
    const d = await fetch('/api/settings/hooks', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, command }),
    }).then((r) => r.json());

    if ((d as any).error) {
      alert('Error: ' + (d as any).error);
      return;
    }

    await loadGlobalHooks();
  } catch (e) {
    alert('Error: ' + (e instanceof Error ? e.message : String(e)));
  }
}


/* ── Local LLM management ── */

interface LocalLlmProvider {
  id: string;
  name: string;
  base_url: string;
  reachable: boolean;
  models: string[];
}

interface LocalLlmStatus {
  providers: LocalLlmProvider[];
  active_model: string | null;
  default_model: string;
}

export async function loadLocalLlmStatus(): Promise<void> {
  const container = document.getElementById('local-llm-providers');
  const select = document.getElementById('local-llm-model') as HTMLSelectElement | null;
  const statusEl = document.getElementById('local-llm-status');
  if (!container) return;

  try {
    const resp = await fetch('/api/local-llm/status');
    const data: LocalLlmStatus = await resp.json();

    if (!data.providers || data.providers.length === 0) {
      container.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No local LLM providers configured.</span>';
      return;
    }

    let html = '';
    for (const p of data.providers) {
      const dot = p.reachable ? '🟢' : '🔴';
      html += `<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:13px">`
        + `${dot} <strong>${p.name}</strong> <span style="color:var(--text-muted)">${p.base_url}</span>`
        + ` <span style="color:var(--text-muted)">(${p.models.length} models)</span></div>`;
    }
    container.innerHTML = html;

    // Populate model dropdown
    if (select) {
      const prev = select.value;
      select.innerHTML = '<option value="">Select a local model...</option>';
      for (const p of data.providers) {
        for (const m of p.models) {
          const opt = document.createElement('option');
          opt.value = m;
          opt.textContent = `${m} (${p.id})`;
          select.appendChild(opt);
        }
      }
      if (prev) select.value = prev;
    }

    if (statusEl) {
      if (data.active_model) {
        statusEl.innerHTML = `Active model: <strong style="color:var(--accent)">${data.active_model}</strong>`;
      } else if (data.default_model) {
        statusEl.innerHTML = `Default: <strong>${data.default_model}</strong> (cloud)`;
      } else {
        statusEl.textContent = 'Using cloud default';
      }
    }
  } catch (e) {
    container.innerHTML = '<span style="color:#f87171;font-size:12px">Failed to load local LLM status</span>';
  }
}

export async function activateLocalLlm(): Promise<void> {
  const select = document.getElementById('local-llm-model') as HTMLSelectElement | null;
  const model = select?.value;
  if (!model) {
    alert('Select a model first');
    return;
  }

  try {
    const resp = await fetch('/api/local-llm/activate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model }),
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      await loadLocalLlmStatus();
    } else {
      alert('Error: ' + (data.error || 'Unknown'));
    }
  } catch (e) {
    alert('Failed to activate: ' + (e instanceof Error ? e.message : String(e)));
  }
}

export async function deactivateLocalLlm(): Promise<void> {
  try {
    const resp = await fetch('/api/local-llm/activate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: '' }),
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      await loadLocalLlmStatus();
    } else {
      alert('Error: ' + (data.error || 'Unknown'));
    }
  } catch (e) {
    alert('Failed to deactivate: ' + (e instanceof Error ? e.message : String(e)));
  }
}
