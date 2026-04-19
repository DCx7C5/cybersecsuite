// Team builder and manager

import { $ } from './core.js';
import { renderTable } from './table.js';

export interface TeamMember {
  name?: string;
  role?: string;
  agents?: string[];
}

export interface SavedTeam {
  name: string;
  role?: string;
  description?: string;
}

interface AgentData {
  name?: string;
  source_dir?: string;
  description?: string;
  model?: string;
  maxTurns?: number;
  tools?: string[] | string;
}

let _tbAgents: AgentData[] = [];
let _tbAgentNames: string[] = [];
let _tbSubAgentNames: string[] = [];

export async function loadTeamBuilder(): Promise<void> {
  try {
    const [agRes, teRes] = await Promise.all([
      fetch('/api/team-agents').then((r) => r.json()),
      fetch('/api/teams').then((r) => r.json()),
    ]);

    _tbAgents = (agRes as any).agents || [];
    _tbAgentNames = [
      ...new Set(
        _tbAgents
          .map((a) => a.name)
          .filter(Boolean)
          .filter((x): x is string => typeof x === 'string')
      ),
    ].sort();
    _tbSubAgentNames = [
      ...new Set(
        _tbAgents
          .filter((a) => a.source_dir === 'sub_agents')
          .map((a) => a.name)
          .filter(Boolean)
          .filter((x): x is string => typeof x === 'string')
      ),
    ].sort();

    if (!_tbSubAgentNames.length) _tbSubAgentNames = _tbAgentNames;
    tbFilterAgents('');

    document.querySelectorAll('.tb-agent-select').forEach((s) => _tbPopulateAgentSelect(s as HTMLSelectElement));
  } catch (e) {
    console.error('Team builder load error', e);
  }
}

export function tbFilterAgents(q: string): void {
  const ql = q.toLowerCase();
  const filtered = ql
    ? _tbAgents.filter(
        (a) =>
          (a.name || '').toLowerCase().includes(ql) ||
          (a.description || '').toLowerCase().includes(ql) ||
          (a.model || '').toLowerCase().includes(ql)
      )
    : _tbAgents;

  const countEl = $('tb-agent-count');
  if (countEl) countEl.textContent = filtered.length + ' agents';

  renderTable(
    'tb-agents-table',
    [
      { key: 'name', label: 'Agent', type: 'string' },
      { key: 'model', label: 'Model', type: 'string' },
      { key: 'maxTurns', label: 'MaxTurns', type: 'number' },
      { key: 'tools_str', label: 'Tools', type: 'string' },
      { key: 'description', label: 'Description', type: 'string' },
    ],
    filtered.map((a) => ({
      name: '<strong>' + (a.name || '') + '</strong>',
      model: a.model || '—',
      maxTurns: a.maxTurns || '—',
      tools_str: Array.isArray(a.tools) ? a.tools.join(', ') : (a.tools || '—'),
      description: a.description || '—',
    })),
    { pageSize: 15 }
  );
}

export async function tbLoadSkills(): Promise<void> {
  const domainEl = $('tb-skill-domain') as HTMLSelectElement | null;
  const qEl = $('tb-skill-q') as HTMLInputElement | null;
  const tableEl = $('tb-skills-table');

  const domain = domainEl?.value || '';
  const q = qEl?.value || '';

  try {
    const params = new URLSearchParams();
    if (domain) params.set('domain', domain);
    if (q) params.set('q', q);

    if (tableEl) tableEl.innerHTML = '<div class="text-xs text-gray-500">Loading...</div>';

    const res = await fetch('/api/skills?' + params.toString());
    const data = await res.json();
    tbRenderSkills((data as any).skills || []);
  } catch (e) {
    if (tableEl) tableEl.innerHTML = '<div class="text-red-400">Error: ' + (e instanceof Error ? e.message : String(e)) + '</div>';
  }
}

function tbRenderSkills(skills: any[]): void {
  const countEl = $('tb-skill-count');
  if (countEl) countEl.textContent = skills.length + ' skills';

  renderTable(
    'tb-skills-table',
    [
      { key: 'name', label: 'Skill', type: 'string' },
      { key: 'domain', label: 'Domain', type: 'string' },
      { key: 'subdomain', label: 'Subdomain', type: 'string' },
      { key: 'description', label: 'Description', type: 'string' },
      { key: 'tags_str', label: 'Tags', type: 'string' },
      { key: 'mitre_str', label: 'MITRE', type: 'string' },
    ],
    skills.map((s) => ({
      name: '<strong>' + s.name + '</strong>',
      domain: s.domain || '—',
      subdomain: s.subdomain || '—',
      description: s.description || '—',
      tags_str: Array.isArray(s.tags) ? s.tags.join(', ') : '—',
      mitre_str: Array.isArray(s.mitre_attack) ? s.mitre_attack.join(', ') : '—',
    })),
    { pageSize: 20 }
  );
}

function _tbPopulateAgentSelect(sel: HTMLSelectElement): void {
  const current = sel.value;
  while (sel.options.length > 1) sel.remove(1);
  _tbSubAgentNames.forEach((n) => {
    const opt = document.createElement('option');
    opt.value = n;
    opt.textContent = n;
    sel.appendChild(opt);
  });
  if (current && _tbSubAgentNames.includes(current)) sel.value = current;
}

let _tbMemberIdx = 0;

export function tbAddMember(): void {
  const i = _tbMemberIdx++;
  const div = document.createElement('div');
  div.id = 'tb-member-' + i;
  div.className = 'flex items-center gap-3 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2';

  div.innerHTML =
    '<span class="text-xs text-gray-400 w-20 shrink-0">Member ' +
    (i + 1) +
    '</span>' +
    '<input class="tb-member-name flex-1 px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded font-mono" placeholder="Role (e.g. Analyst)">' +
    '<select class="tb-agent-select px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded">' +
    '<option value="">— select agent —</option>' +
    _tbSubAgentNames.map((n) => '<option value="' + n + '">' + n + '</option>').join('') +
    '</select>' +
    '<button onclick="document.getElementById(\'tb-member-' +
    i +
    '\').remove()" class="px-2 py-1 text-xs bg-gray-800 hover:bg-red-900 rounded">✕</button>';

  const membersEl = $('tb-members');
  if (membersEl) membersEl.appendChild(div);
}

export function tbGenerateTeam(): void {
  const members: { role: string; agent: string | null }[] = [];
  document.querySelectorAll('[id^="tb-member-"]').forEach((row) => {
    const nameEl = row.querySelector('.tb-member-name') as HTMLInputElement | null;
    const agentEl = row.querySelector('.tb-agent-select') as HTMLSelectElement | null;

    const name = (nameEl?.value || '').trim() || 'Member';
    const agent = agentEl?.value || null;
    members.push({ role: name, agent });
  });

  const team = { team: members, generated_at: new Date().toISOString() };
  const pre = $('tb-team-json');
  if (pre) {
    pre.textContent = JSON.stringify(team, null, 2);
    pre.style.display = '';
  }
}

export function tbCopyTeam(): void {
  const pre = $('tb-team-json');
  if (!pre || !pre.textContent) {
    tbGenerateTeam();
  }
  if (pre && pre.textContent) {
    navigator.clipboard.writeText(pre.textContent).catch(() => {});
  }
}

export async function tbSaveTeam(): Promise<void> {
  const status = $('tb-save-status');
  const nameEl = $('tb-team-name') as HTMLInputElement | null;
  const name = (nameEl?.value || '').trim();

  if (!status) return;

  if (!name) {
    status.textContent = '✗ Enter a team name';
    status.style.color = '#f87171';
    return;
  }

  const members: TeamMember[] = [];
  document.querySelectorAll('[id^="tb-member-"]').forEach((row) => {
    const mnameEl = row.querySelector('.tb-member-name') as HTMLInputElement | null;
    const agentEl = row.querySelector('.tb-agent-select') as HTMLSelectElement | null;

    const mname = (mnameEl?.value || '').trim() || 'Member';
    const agent = agentEl?.value || '';
    members.push({ name: mname, agents: agent ? [agent] : [] });
  });

  if (!members.length) {
    status.textContent = '✗ Add at least one member';
    status.style.color = '#f87171';
    return;
  }

  status.textContent = 'Saving...';
  status.style.color = '#9ca3af';

  try {
    const res = await fetch('/api/teams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phases: members }),
    });
    const data = await res.json();

    if (!res.ok) {
      status.textContent = '✗ ' + ((data as any).error || 'Failed');
      status.style.color = '#f87171';
      return;
    }

    status.textContent = '✓ Saved: ' + (data as any).team;
    status.style.color = '#34d399';
    await tbLoadSavedTeams();
    setTimeout(() => {
      status.textContent = '';
    }, 3000);
  } catch (e) {
    status.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
    status.style.color = '#f87171';
  }
}

export async function tbLoadSavedTeams(): Promise<void> {
  try {
    const res = await fetch('/api/teams');
    const data = await res.json();
    const teams: SavedTeam[] = (data as any).teams || [];
    const el = $('tb-saved-teams');

    if (!el) return;

    if (!teams.length) {
      el.innerHTML = '<div class="text-xs text-gray-500">No saved teams.</div>';
      return;
    }

    renderTable(
      'tb-saved-teams',
      [
        { key: 'name', label: 'Team', type: 'string' },
        { key: 'role', label: 'Role', type: 'string' },
        { key: 'description', label: 'Description', type: 'string' },
        { key: 'actions', label: 'Actions', type: 'string' },
      ],
      teams.map((t) => ({
        name: '<strong>' + (t.name || '') + '</strong>',
        role: t.role || '—',
        description: t.description || '—',
        actions:
          ['blue-team', 'red-team', 'purple-team'].includes(t.name)
            ? '<span class="text-gray-600 text-xs">built-in</span>'
            : '<button onclick="tbDeleteTeam(\'' + t.name + '\')" class="px-2 py-0.5 bg-red-900 hover:bg-red-800 text-xs rounded">Delete</button>',
      })),
      { pageSize: 10 }
    );
  } catch (e) {
    console.error('tbLoadSavedTeams', e);
  }
}

export async function tbDeleteTeam(name: string): Promise<void> {
  if (!confirm('Delete team "' + name + '"?')) return;
  try {
    await fetch('/api/teams/' + encodeURIComponent(name), { method: 'DELETE' });
    await tbLoadSavedTeams();
  } catch (e) {
    console.error(e);
  }
}
