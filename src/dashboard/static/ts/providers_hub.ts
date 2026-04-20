// providers_hub.ts — Provider Hub frontend

import { fetchApi } from './core.js';

interface PhAccount {
  vault_key: string;
  label: string | null;
  auth_method: string;
  email: string | null;
  display_name: string | null;
  subject: string | null;
  tenant: string | null;
  active: boolean;
  test_status: string | null;
}

interface PhProvider {
  id: string;
  name: string;
  base_url: string;
  status: string;
  is_free: boolean;
  auth_type: string;
  models_count: number;
  auth_methods: { auth_method: string; config: Record<string, unknown> }[];
  accounts: PhAccount[];
}

const AUTH_ICONS: Record<string, string> = {
  api_key: '🔑',
  oauth:   '🔐',
  browser: '🌐',
  none:    '🔓',
};

const STATUS_ORDER: Record<string, number> = {
  available:      0,
  no_credentials: 1,
  disabled:       2,
};

let _hubData: PhProvider[] = [];

function esc(s: string | null | undefined): string {
  if (!s) return '';
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function statusDot(status: string): string {
  const color =
    status === 'available'      ? 'var(--success)' :
    status === 'no_credentials' ? 'var(--amber)'   :
                                  'var(--red)';
  return `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};margin-right:6px;flex-shrink:0"></span>`;
}

function authBadge(authType: string): string {
  const icon = AUTH_ICONS[authType] ?? '?';
  return `<span style="font-size:11px;padding:2px 6px;border-radius:4px;background:var(--surface);border:1px solid var(--border);font-family:var(--font-mono)">${icon} ${esc(authType)}</span>`;
}

function accountPills(accounts: PhAccount[]): string {
  if (!accounts.length) return '<span style="color:var(--text-muted);font-size:11px">no accounts</span>';
  return accounts.map((a) => {
    const label = esc(a.email || a.display_name || a.label || a.vault_key);
    const dot = a.active
      ? `<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--success);margin-right:4px"></span>`
      : '';
    return `<span style="display:inline-flex;align-items:center;font-size:11px;padding:2px 6px;border-radius:4px;background:var(--surface);border:1px solid var(--border);margin-right:4px;font-family:var(--font-mono)">${dot}${label}</span>`;
  }).join('');
}

function addButtons(provider: PhProvider): string {
  const methods = provider.auth_methods.length
    ? provider.auth_methods.map((am) => am.auth_method)
    : [provider.auth_type];
  const unique = [...new Set(methods)];
  return unique.map((am) => {
    const icon = AUTH_ICONS[am] ?? '+';
    return `<button class="btn btn-ghost" style="font-size:11px;padding:3px 8px" onclick="phOpenModal('${esc(provider.id)}','${esc(am)}')" title="Add ${esc(am)} account">${icon} Add</button>`;
  }).join(' ');
}

function renderProviderDetail(p: PhProvider): string {
  if (!p.accounts.length) {
    return `<div style="padding:8px 12px;color:var(--text-muted);font-size:12px">No accounts configured.</div>`;
  }
  const rows = p.accounts.map((a) => {
    const statusColor =
      a.test_status === 'ok'    ? 'var(--success)' :
      a.test_status === 'error' ? 'var(--red)'     :
                                  'var(--text-muted)';
    return (
      `<tr>` +
      `<td style="padding:4px 8px;font-family:var(--font-mono);font-size:11px">${esc(a.vault_key)}</td>` +
      `<td style="padding:4px 8px;font-size:11px">${esc(a.label || '—')}</td>` +
      `<td style="padding:4px 8px;font-size:11px">${AUTH_ICONS[a.auth_method] ?? ''} ${esc(a.auth_method)}</td>` +
      `<td style="padding:4px 8px;font-size:11px">${esc(a.email || '—')}</td>` +
      `<td style="padding:4px 8px;font-size:11px"><span style="color:${a.active ? 'var(--success)' : 'var(--text-muted)'}">${a.active ? '● active' : '○ inactive'}</span></td>` +
      `<td style="padding:4px 8px;font-size:11px;color:${statusColor}">${esc(a.test_status || '—')}</td>` +
      `</tr>`
    );
  }).join('');
  return (
    `<div style="padding:0 12px 8px"><table style="width:100%;border-collapse:collapse">` +
    `<thead><tr style="border-bottom:1px solid var(--border)">` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">VAULT KEY</th>` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">LABEL</th>` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">METHOD</th>` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">EMAIL</th>` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">STATUS</th>` +
    `<th style="padding:4px 8px;text-align:left;font-size:10px;color:var(--text-muted);font-weight:500">TEST</th>` +
    `</tr></thead><tbody>${rows}</tbody></table></div>`
  );
}

function renderProviderRow(p: PhProvider): string {
  const truncUrl = p.base_url.length > 40 ? p.base_url.slice(0, 40) + '…' : p.base_url;
  const isEnabled = p.status !== 'disabled';
  const toggleBtn =
    `<button class="btn btn-ghost" id="ph-toggle-${esc(p.id)}" ` +
    `style="font-size:11px;padding:3px 8px;min-width:62px;color:${isEnabled ? 'var(--success)' : 'var(--text-muted)'}" ` +
    `onclick="event.stopPropagation();phSetProviderEnabled('${esc(p.id)}',${!isEnabled})" ` +
    `title="${isEnabled ? 'Disable' : 'Enable'} provider">` +
    `${isEnabled ? '● On' : '○ Off'}</button>`;
  return (
    `<div class="ph-provider-row" data-provider="${esc(p.id)}" data-name="${esc(p.name.toLowerCase())}" style="border-bottom:1px solid var(--border)">` +
    `<div class="ph-row-summary" onclick="document.getElementById('ph-detail-${esc(p.id)}').style.display=document.getElementById('ph-detail-${esc(p.id)}').style.display==='none'?'':'none'" style="display:flex;align-items:center;gap:12px;padding:10px 12px;cursor:pointer;transition:background 0.1s" onmouseenter="this.style.background='var(--accent-glow)'" onmouseleave="this.style.background=''">` +
    `<span style="display:flex;align-items:center">${statusDot(p.status)}</span>` +
    `<span style="font-size:13px;font-weight:500;min-width:140px">${esc(p.name)}</span>` +
    `<span style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis" title="${esc(p.base_url)}">${esc(truncUrl)}</span>` +
    `<span>${authBadge(p.auth_type)}</span>` +
    `<span style="font-size:11px;color:var(--text-muted);min-width:60px;text-align:right;font-family:var(--font-mono)">${p.models_count} models</span>` +
    `<span style="flex:1;min-width:120px">${accountPills(p.accounts)}</span>` +
    `<span onclick="event.stopPropagation()">${addButtons(p)}</span>` +
    `<span onclick="event.stopPropagation()">${toggleBtn}</span>` +
    `<span style="font-size:10px;color:var(--text-muted);margin-left:4px">▾</span>` +
    `</div>` +
    `<div id="ph-detail-${esc(p.id)}" style="display:none;background:var(--surface)">${renderProviderDetail(p)}</div>` +
    `</div>`
  );
}

function renderGroup(label: string, providers: PhProvider[]): string {
  if (!providers.length) return '';
  const rows = providers.map(renderProviderRow).join('');
  return (
    `<div style="margin-bottom:16px">` +
    `<div style="font-size:10px;font-weight:600;color:var(--text-muted);padding:6px 12px;background:var(--surface);border-bottom:1px solid var(--border);letter-spacing:0.08em">${label.toUpperCase()} (${providers.length})</div>` +
    rows +
    `</div>`
  );
}

export async function loadProvidersHub(): Promise<void> {
  const list = document.getElementById('ph-list');
  if (!list) return;

  try {
    const data = await fetchApi('/api/providers/hub') as PhProvider[];
    _hubData = data;

    const available      = data.filter((p) => p.status === 'available');
    const noCredentials  = data.filter((p) => p.status === 'no_credentials');
    const disabled       = data.filter((p) => p.status === 'disabled');

    list.innerHTML =
      renderGroup('Available', available) +
      renderGroup('No Credentials', noCredentials) +
      renderGroup('Disabled', disabled);

    const stats = document.getElementById('ph-stats');
    if (stats) {
      stats.textContent = `${available.length} available · ${noCredentials.length} unconfigured · ${disabled.length} disabled`;
    }
  } catch (err) {
    list.innerHTML = `<div style="color:var(--red);font-size:13px;padding:12px">Failed to load providers: ${esc(String(err))}</div>`;
  }
}

export function phOpenModal(providerId: string, authMethod: string): void {
  const modal = document.getElementById('ph-modal');
  const title = document.getElementById('ph-modal-title');
  const provInput = document.getElementById('ph-modal-provider') as HTMLInputElement | null;
  const body = document.getElementById('ph-modal-body');
  const status = document.getElementById('ph-modal-status');

  if (!modal || !title || !provInput || !body) return;

  const provider = _hubData.find((p) => p.id === providerId);
  const provName = provider ? provider.name : providerId;

  title.textContent = `Add ${provName} — ${AUTH_ICONS[authMethod] ?? ''} ${authMethod}`;
  provInput.value = providerId;
  if (status) status.textContent = '';

  let fields = `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">Label</label><input id="ph-f-label" type="text" class="form-input" style="width:100%" placeholder="e.g. Main Key"></div>`;

  if (authMethod === 'api_key') {
    fields +=
      `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">API Key <span style="color:var(--red)">*</span></label><input id="ph-f-apikey" type="password" class="form-input" style="width:100%" placeholder="sk-..."></div>` +
      `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">Display Name</label><input id="ph-f-display-name" type="text" class="form-input" style="width:100%" placeholder="Optional"></div>`;
  } else if (authMethod === 'oauth') {
    fields +=
      `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">Subject / User ID</label><input id="ph-f-subject" type="text" class="form-input" style="width:100%" placeholder="OAuth subject"></div>` +
      `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">Email</label><input id="ph-f-email" type="email" class="form-input" style="width:100%" placeholder="user@example.com"></div>` +
      `<div style="margin-bottom:12px"><label style="display:block;font-size:11px;color:var(--text-muted);margin-bottom:4px">Tenant / Org (optional)</label><input id="ph-f-tenant" type="text" class="form-input" style="width:100%" placeholder="org name or ID"></div>`;
  }

  fields +=
    `<div style="margin-top:16px;display:flex;justify-content:flex-end;gap:8px">` +
    `<button class="btn btn-ghost" onclick="phCloseModal()">Cancel</button>` +
    `<button class="btn btn-accent" onclick="phSaveAccount()">Save Account</button>` +
    `</div>`;

  // Store auth_method for phSaveAccount
  body.innerHTML = fields;
  body.dataset['authMethod'] = authMethod;

  modal.style.display = 'flex';
}

export async function phSaveAccount(): Promise<void> {
  const provInput = document.getElementById('ph-modal-provider') as HTMLInputElement | null;
  const body = document.getElementById('ph-modal-body');
  const statusEl = document.getElementById('ph-modal-status');

  if (!provInput || !body) return;

  const providerId = provInput.value;
  const authMethod = body.dataset['authMethod'] ?? 'api_key';

  const label       = (document.getElementById('ph-f-label') as HTMLInputElement | null)?.value.trim() || null;
  const apiKey      = (document.getElementById('ph-f-apikey') as HTMLInputElement | null)?.value.trim() || null;
  const displayName = (document.getElementById('ph-f-display-name') as HTMLInputElement | null)?.value.trim() || null;
  const subject     = (document.getElementById('ph-f-subject') as HTMLInputElement | null)?.value.trim() || null;
  const email       = (document.getElementById('ph-f-email') as HTMLInputElement | null)?.value.trim() || null;
  const tenant      = (document.getElementById('ph-f-tenant') as HTMLInputElement | null)?.value.trim() || null;

  if (authMethod === 'api_key' && !apiKey) {
    if (statusEl) { statusEl.textContent = '✗ API key is required'; statusEl.style.color = 'var(--red)'; }
    return;
  }

  if (statusEl) { statusEl.textContent = 'Saving…'; statusEl.style.color = 'var(--text-muted)'; }

  try {
    const payload: Record<string, unknown> = {
      provider_id:  providerId,
      auth_method:  authMethod,
      label:        label,
      display_name: displayName,
      subject:      subject,
      email:        email,
      tenant:       tenant,
    };
    if (apiKey) payload['api_key'] = apiKey;

    const resp = await fetch('/api/accounts', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const result = await resp.json() as Record<string, unknown>;

    if (!resp.ok) {
      const msg = (result['error'] as string) ?? resp.statusText;
      if (statusEl) { statusEl.textContent = `✗ ${msg}`; statusEl.style.color = 'var(--red)'; }
      return;
    }

    if (statusEl) { statusEl.textContent = '✓ Account saved'; statusEl.style.color = 'var(--success)'; }
    setTimeout(() => {
      phCloseModal();
      loadProvidersHub().catch(() => {});
    }, 800);
  } catch (err) {
    if (statusEl) { statusEl.textContent = `✗ ${String(err)}`; statusEl.style.color = 'var(--red)'; }
  }
}

export function phCloseModal(): void {
  const modal = document.getElementById('ph-modal');
  if (modal) modal.style.display = 'none';
}

export async function phSetProviderEnabled(providerId: string, enabled: boolean): Promise<void> {
  const btn = document.getElementById(`ph-toggle-${providerId}`) as HTMLButtonElement | null;
  if (btn) { btn.disabled = true; btn.textContent = '…'; }

  try {
    const resp = await fetch(`/api/providers/${encodeURIComponent(providerId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    if (!resp.ok) {
      const body = await resp.json() as Record<string, unknown>;
      console.error('provider toggle failed:', body['error'] ?? resp.statusText);
      if (btn) { btn.disabled = false; btn.textContent = enabled ? '● On' : '○ Off'; }
      return;
    }
  } catch (err) {
    console.error('provider toggle error:', err);
    if (btn) { btn.disabled = false; }
    return;
  }

  loadProvidersHub().catch(() => {});
}

export function phFilterProviders(query: string): void {
  const q = query.toLowerCase().trim();
  document.querySelectorAll<HTMLElement>('.ph-provider-row').forEach((row) => {
    const name = (row.dataset['name'] ?? '').toLowerCase();
    const id   = (row.dataset['provider'] ?? '').toLowerCase();
    row.style.display = (!q || name.includes(q) || id.includes(q)) ? '' : 'none';
  });
}
