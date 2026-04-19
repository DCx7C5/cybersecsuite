// Agent factory builder

import { $ } from './core.js';

export interface AgentTemplate {
  name: string;
}

export interface SkillOption {
  name: string;
}

let _afTemplates: string[] = [];
let _afSkills: string[] = [];
let _afTplIdx = 1;
let _afSkillIdx = 1;

export async function afLoadTemplates(): Promise<void> {
  try {
    const d = await fetch('/api/settings/agent-agents').then((r) => r.json());
    _afTemplates = (d as any).agents || [];

    const sel = $('af-tpl-0') as HTMLSelectElement | null;
    if (sel) {
      while (sel.options.length > 1) sel.remove(1);
      _afTemplates.forEach((t) => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = t.replace('.md', '');
        sel.appendChild(opt);
      });
    }
  } catch (e) {
    console.error('afLoadTemplates', e);
  }
}

export function afAddTemplate(): void {
  const i = _afTplIdx++;
  const row = document.createElement('div');
  row.style.cssText = 'display:flex;align-items:center;gap:6px';

  const sel = document.createElement('select');
  sel.id = 'af-tpl-' + i;
  sel.style.cssText =
    'flex:1;padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono)';
  sel.innerHTML =
    '<option value="">— none —</option>' +
    _afTemplates.map((t) => '<option value="' + t + '">' + t.replace('.md', '') + '</option>').join('');

  const rm = document.createElement('button');
  rm.textContent = '✕';
  rm.className = 'btn';
  rm.style.cssText = 'font-size:11px;padding:3px 8px';
  rm.onclick = () => row.remove();

  row.appendChild(sel);
  row.appendChild(rm);

  const rowsEl = $('af-tpl-rows');
  if (rowsEl) rowsEl.appendChild(row);
}

export async function afLoadSkillOptions(): Promise<void> {
  if (_afSkills.length) return;
  try {
    const d = await fetch('/api/skills').then((r) => r.json());
    _afSkills = ((d as any).skills || [])
      .map((s: { name?: string }) => s.name)
      .filter(Boolean)
      .sort();
  } catch (e) {
    console.error('afLoadSkillOptions', e);
  }
}

export async function afAddSkill(): Promise<void> {
  await afLoadSkillOptions();
  const i = _afSkillIdx++;
  const row = document.createElement('div');
  row.style.cssText = 'display:flex;align-items:center;gap:6px';

  const sel = document.createElement('select');
  sel.id = 'af-skill-' + i;
  sel.style.cssText =
    'flex:1;padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono)';
  sel.innerHTML =
    '<option value="">— none —</option>' +
    _afSkills.map((s) => '<option value="' + s + '">' + s + '</option>').join('');

  const rm = document.createElement('button');
  rm.textContent = '✕';
  rm.className = 'btn';
  rm.style.cssText = 'font-size:11px;padding:3px 8px';
  rm.onclick = () => row.remove();

  const sk0 = $('af-skill-0') as HTMLSelectElement | null;
  if (sk0 && sk0.options.length <= 1) {
    sk0.innerHTML =
      '<option value="">— none —</option>' +
      _afSkills.map((s) => '<option value="' + s + '">' + s + '</option>').join('');
  }

  row.appendChild(sel);
  row.appendChild(rm);

  const rowsEl = $('af-skill-rows');
  if (rowsEl) rowsEl.appendChild(row);
}

export function setupTypeHints(): void {
  const hints: Record<string, string> = {
    specialist: 'Focused expert — executes tasks, returns results.',
    'team-leader': 'Claude team orchestrator — manages a cohesive multi-agent claude team.',
    orchestrator: 'Inter-API orchestrator — routes across multiple API providers and teams.',
  };

  document.addEventListener('change', function (e) {
    const target = e.target as HTMLSelectElement | null;
    if (target && target.id === 'af-type') {
      const h = $('af-type-hint');
      if (h) h.textContent = hints[target.value] || '';
    }
  });
}

export async function afGenerate(): Promise<void> {
  const st = $('af-status');
  const preview = $('af-preview') as HTMLElement | null;
  const typeEl = $('af-type') as HTMLSelectElement | null;
  const modelEl = $('af-model') as HTMLSelectElement | null;
  const maxturnsEl = $('af-maxturns') as HTMLInputElement | null;
  const nameEl = $('af-name') as HTMLInputElement | null;
  const descEl = $('af-desc') as HTMLTextAreaElement | null;
  const extraEl = $('af-extra') as HTMLTextAreaElement | null;
  const saveFileEl = $('af-save-file') as HTMLInputElement | null;
  const projectCtxEl = $('af-project-ctx') as HTMLInputElement | null;

  const type = (typeEl?.value || 'specialist').trim();
  const model = (modelEl?.value || 'sonnet').trim();
  const maxTurns = parseInt(maxturnsEl?.value || '30', 10);
  const name = (nameEl?.value || '').trim();
  const description = (descEl?.value || '').trim();
  const extra = (extraEl?.value || '').trim();
  const saveFile = saveFileEl?.checked !== false;
  const projectCtx = projectCtxEl?.checked || false;

  const tools: string[] = [];
  document.querySelectorAll('#af-tools input[type=checkbox]:checked').forEach((c) => {
    const checkbox = c as HTMLInputElement;
    tools.push(checkbox.value);
  });

  const agents: string[] = [];
  document.querySelectorAll('[id^="af-tpl-"]').forEach((s) => {
    const sel = s as HTMLSelectElement;
    if (sel.value) agents.push(sel.value);
  });

  const skills: string[] = [];
  document.querySelectorAll('[id^="af-skill-"]').forEach((s) => {
    const sel = s as HTMLSelectElement;
    if (sel.value) skills.push(sel.value);
  });

  const research: string[] = [];
  document.querySelectorAll('[id^="af-r-"]:checked').forEach((c) => {
    const checkbox = c as HTMLInputElement;
    research.push(checkbox.value);
  });

  if (!name) {
    if (st) {
      st.textContent = '✗ Name required';
      st.style.color = 'var(--red)';
    }
    return;
  }

  if (st) {
    st.textContent = '⟳ Generating…';
    st.style.color = 'var(--text-muted)';
  }
  if (preview) preview.style.display = 'none';

  try {
    const resp = await fetch('/api/agents/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        name,
        description,
        model,
        maxTurns,
        tools,
        agents,
        skills,
        research,
        project_context: projectCtx,
        extra_instructions: extra,
        save: saveFile,
      }),
    });
    const d = await resp.json();

    if ((d as any).error) {
      if (st) {
        st.textContent = '✗ ' + (d as any).error;
        st.style.color = 'var(--red)';
      }
      return;
    }

    if (st) {
      st.textContent = '✓ Generated' + (saveFile ? ' & saved to .claude/agents/' : '');
      st.style.color = 'var(--success)';
    }

    if (preview) {
      preview.textContent = (d as any).content || '';
      preview.style.display = '';
    }
  } catch (e) {
    if (st) {
      st.textContent = '✗ ' + (e instanceof Error ? e.message : String(e));
      st.style.color = 'var(--red)';
    }
  }
}

export function setupAgentFactoryLoader(): void {
  document.addEventListener('click', function (e) {
    const tab = (e.target as Element).closest('.tab');
    if (tab && (tab as any).id === 'nav-agent-factory') {
      afLoadTemplates();
    }
  });
}
