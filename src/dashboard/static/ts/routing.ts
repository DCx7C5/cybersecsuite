// routing.ts — Routing Engine panel

interface CircuitBreaker { provider: string; state: string; failures: number; last_failure: string | null; }
interface BudgetEntry { provider: string; limit: number; spent: number; }
interface RoutingData {
  strategies: string[];
  circuit_breakers: CircuitBreaker[];
  open_circuits: number;
  usage_counts: Record<string, number>;
  budgets: BudgetEntry[];
  error?: string;
}

const _$ = (id: string) => document.getElementById(id);

export async function loadRouting(): Promise<void> {
  try {
    const res = await fetch('/api/routing');
    const data: RoutingData = await res.json();
    if (data.error) return;
    _renderCBTable(data.circuit_breakers || []);
    _renderBudgets(data.budgets || []);
  } catch (e) { console.error('loadRouting:', e); }
}

function _renderCBTable(cbs: CircuitBreaker[]): void {
  const el = _$('routing-cb-table');
  if (!el) return;
  if (!cbs.length) { el.innerHTML = '<p style="font-size:12px;color:var(--text-muted)">No active circuit breakers.</p>'; return; }
  const rows = cbs.map(cb => {
    const c = cb.state === 'open' ? 'var(--red)' : cb.state === 'half_open' ? 'var(--yellow)' : 'var(--green)';
    return `<tr><td style="padding:6px 8px;font-size:12px;font-family:var(--font-mono)">${cb.provider}</td>
      <td style="padding:6px 8px"><span style="color:${c};font-size:11px;font-weight:600">${cb.state.toUpperCase()}</span></td>
      <td style="padding:6px 8px;font-size:12px;text-align:right">${cb.failures}</td></tr>`;
  }).join('');
  el.innerHTML = `<table style="width:100%;border-collapse:collapse">
    <thead><tr style="border-bottom:1px solid var(--border)">
      <th style="text-align:left;padding:6px 8px;font-size:11px;color:var(--text-muted)">Provider</th>
      <th style="text-align:left;padding:6px 8px;font-size:11px;color:var(--text-muted)">State</th>
      <th style="text-align:right;padding:6px 8px;font-size:11px;color:var(--text-muted)">Failures</th>
    </tr></thead><tbody>${rows}</tbody></table>`;
}

function _renderBudgets(budgets: BudgetEntry[]): void {
  const el = _$('routing-budgets');
  if (!el) return;
  if (!budgets.length) { el.textContent = 'No budget guards configured.'; return; }
  el.innerHTML = budgets.map(b => {
    const pct = b.limit > 0 ? Math.min(100, (b.spent / b.limit) * 100) : 0;
    const c = pct > 90 ? 'var(--red)' : pct > 70 ? 'var(--yellow)' : 'var(--green)';
    return `<div style="margin-bottom:8px">
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span>${b.provider}</span><span style="color:${c}">$${b.spent.toFixed(2)} / $${b.limit.toFixed(2)}</span>
      </div>
      <div style="height:4px;background:var(--surface-2);border-radius:2px">
        <div style="height:4px;width:${pct}%;background:${c};border-radius:2px"></div>
      </div></div>`;
  }).join('');
}

export async function routingSetStrategy(): Promise<void> {
  const sel = _$('route-strategy') as HTMLSelectElement;
  if (!sel) return;
  try {
    await fetch('/api/routing/strategy', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ strategy: sel.value }) });
  } catch (e) { console.error('routingSetStrategy:', e); }
}

export async function routingSetResilience(): Promise<void> {
  const sel = _$('route-resilience') as HTMLSelectElement;
  if (!sel) return;
  try {
    await fetch('/api/routing/resilience', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ profile: sel.value }) });
  } catch (e) { console.error('routingSetResilience:', e); }
}

export async function routingSimulate(): Promise<void> {
  const prompt = (_$('route-sim-prompt') as HTMLInputElement)?.value?.trim() || '';
  const task = (_$('route-sim-task') as HTMLSelectElement)?.value || 'general';
  const out = _$('route-sim-result');
  if (!prompt) return;
  if (out) { out.style.display = 'block'; out.textContent = 'Simulating…'; }
  try {
    const res = await fetch('/api/routing/simulate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, task_type: task }),
    });
    const data = await res.json();
    if (out) out.textContent = JSON.stringify(data, null, 2);
  } catch (e) { if (out) out.textContent = String(e); }
}
