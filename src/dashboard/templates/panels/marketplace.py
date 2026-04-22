"""Marketplace browser panel — catalog listing, search, and install controls.

Renders the 'marketplace' dashboard tab with a card grid of available items,
provider/kind filters, install/uninstall buttons, and a search field.

Referenz:
    plan.md T034 — REST endpoints
    plan.md T038 — Agent Factory UI
    src/dashboard/api/marketplace.py — /api/marketplace endpoints
    src/dashboard/templates/panels/advanced.py — panel pattern
"""
from __future__ import annotations


def _marketplace() -> str:
    """Render the Marketplace browser tab panel HTML.

    Returns:
        HTML string for the ``tab-marketplace`` panel.
    """
    _inp = (
        "padding:7px 10px;"
        "background:var(--surface-2);border:1px solid var(--border);"
        "border-radius:var(--radius);color:var(--text-primary);font-size:13px"
    )
    _sel = _inp + ";cursor:pointer"
    _btn_sm = (
        "padding:4px 12px;background:var(--surface-2);"
        "border:1px solid var(--border);border-radius:var(--radius);"
        "font-size:12px;color:var(--text-primary);cursor:pointer"
    )
    _btn_accent_sm = (
        "padding:4px 12px;background:var(--accent);color:#000;"
        "border:none;border-radius:var(--radius);"
        "font-size:12px;font-weight:600;cursor:pointer"
    )

    js = r"""<script>
(function () {
  let _mktItems = [];

  async function mktLoad() {
    const q        = document.getElementById('mkt-search').value.trim();
    const kind     = document.getElementById('mkt-filter-kind').value;
    const provider = document.getElementById('mkt-filter-provider').value;
    const status   = document.getElementById('mkt-filter-status').value;
    const params   = new URLSearchParams();
    if (q)        params.set('q', q);
    if (kind)     params.set('kind', kind);
    if (provider) params.set('provider', provider);
    if (status)   params.set('status', status);
    try {
      const resp = await fetch('/api/marketplace?' + params.toString());
      const data = await resp.json();
      _mktItems = data.items || [];
      _mktRender(_mktItems);
      document.getElementById('mkt-count').textContent = `${_mktItems.length} item(s)`;
    } catch (err) {
      document.getElementById('mkt-grid').innerHTML =
        '<span style="color:var(--red)">Error loading marketplace: ' + err.message + '</span>';
    }
  }

  function _mktRender(items) {
    const grid = document.getElementById('mkt-grid');
    if (!items.length) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:13px">No items found.</span>';
      return;
    }
    grid.innerHTML = items.map(item => {
      const installed = item.status === 'installed';
      const badge = `<span style="
        font-size:10px;padding:2px 6px;border-radius:3px;font-weight:600;
        background:${installed ? 'var(--accent)' : 'var(--surface-2)'};
        color:${installed ? '#000' : 'var(--text-muted)'};
        border:1px solid ${installed ? 'transparent' : 'var(--border)'}
      ">${item.status.replace('_', ' ')}</span>`;
      const tags = (item.tags || []).map(t =>
        `<span style="font-size:10px;padding:1px 5px;border-radius:3px;background:var(--surface-2);border:1px solid var(--border);color:var(--text-muted)">${t}</span>`
      ).join(' ');
      const action = installed
        ? `<button onclick="mktUninstall('${item.id}')" style="${_btn_uninstall}">&#x2715; Uninstall</button>`
        : `<button onclick="mktInstall('${item.id}')" style="${_btn_install}">&#x2b07; Install</button>`;
      return `<div style="
        background:var(--surface-2);border:1px solid var(--border);
        border-radius:var(--radius);padding:14px;display:flex;
        flex-direction:column;gap:6px
      ">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          <span style="font-size:13px;font-weight:600;color:var(--text-primary)">${item.name}</span>
          ${badge}
          <span style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono)">${item.provider} / ${item.kind}</span>
        </div>
        <div style="font-size:12px;color:var(--text-muted)">${item.description}</div>
        <div style="display:flex;flex-wrap:wrap;gap:4px">${tags}</div>
        <div style="display:flex;gap:8px;margin-top:4px">${action}</div>
      </div>`;
    }).join('\n');
  }

  const _btn_install   = "padding:4px 12px;background:var(--accent);color:#000;border:none;border-radius:var(--radius);font-size:12px;font-weight:600;cursor:pointer";
  const _btn_uninstall = "padding:4px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);font-size:12px;color:var(--text-muted);cursor:pointer";

  async function mktInstall(id) {
    try {
      const resp = await fetch(`/api/marketplace/${id}/install`, {method:'POST'});
      if (resp.ok) mktLoad(); else alert('Install failed: ' + (await resp.text()));
    } catch (err) { alert('Install error: ' + err.message); }
  }

  async function mktUninstall(id) {
    try {
      const resp = await fetch(`/api/marketplace/${id}/install`, {method:'DELETE'});
      if (resp.ok) mktLoad(); else alert('Uninstall failed: ' + (await resp.text()));
    } catch (err) { alert('Uninstall error: ' + err.message); }
  }

  // Auto-load when tab becomes visible.
  document.addEventListener('DOMContentLoaded', () => {
    const obs = new MutationObserver(() => {
      const el = document.getElementById('tab-marketplace');
      if (el && el.style.display !== 'none' && !_mktItems.length) mktLoad();
    });
    const panel = document.getElementById('tab-marketplace');
    if (panel) obs.observe(panel, {attributes: true, attributeFilter: ['style']});
    mktLoad();
  });

  window.mktLoad     = mktLoad;
  window.mktInstall  = mktInstall;
  window.mktUninstall = mktUninstall;
})();
</script>"""

    return (
        '<div id="tab-marketplace" class="card" style="display:none">\n'
        '  <h3 style="font-size:1rem;font-weight:600;margin-bottom:4px">&#x1f4e6; Marketplace</h3>\n'
        '  <p style="font-size:12px;color:var(--text-muted);margin-bottom:14px">'
        "Provider-agnostic agent/skill/combo catalog. "
        "Install items to make them available in the agent registry."
        "</p>\n"
        # ── Filter bar ─────────────────────────────────────────────────────
        '  <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;align-items:center">\n'
        f'    <input id="mkt-search" placeholder="Search…" oninput="mktLoad()" style="{_inp};flex:1;min-width:160px">\n'
        f'    <select id="mkt-filter-kind" onchange="mktLoad()" style="{_sel}">\n'
        '      <option value="">All kinds</option>\n'
        '      <option value="agent">Agent</option>\n'
        '      <option value="skill">Skill</option>\n'
        '      <option value="combo">Combo</option>\n'
        '      <option value="template">Template</option>\n'
        '    </select>\n'
        f'    <select id="mkt-filter-provider" onchange="mktLoad()" style="{_sel}">\n'
        '      <option value="">All providers</option>\n'
        '      <option value="claude">Claude</option>\n'
        '      <option value="copilot">Copilot</option>\n'
        '      <option value="cursor">Cursor</option>\n'
        '      <option value="openai">OpenAI</option>\n'
        '      <option value="gemini">Gemini</option>\n'
        '      <option value="grok">Grok</option>\n'
        '      <option value="universal">Universal</option>\n'
        '    </select>\n'
        f'    <select id="mkt-filter-status" onchange="mktLoad()" style="{_sel}">\n'
        '      <option value="">All statuses</option>\n'
        '      <option value="available">Available</option>\n'
        '      <option value="installed">Installed</option>\n'
        '      <option value="update_available">Update Available</option>\n'
        '      <option value="deprecated">Deprecated</option>\n'
        '    </select>\n'
        f'    <button onclick="mktLoad()" style="{_btn_sm}">&#x21bb; Refresh</button>\n'
        '    <span id="mkt-count" style="font-size:12px;color:var(--text-muted);white-space:nowrap"></span>\n'
        "  </div>\n"
        # ── Item grid ──────────────────────────────────────────────────────
        '  <div id="mkt-grid" style="'
        "display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));"
        'gap:12px;margin-bottom:16px">\n'
        '    <span style="color:var(--text-muted);font-size:13px">Loading marketplace…</span>\n'
        "  </div>\n"
        # ── Factory link ───────────────────────────────────────────────────
        '  <p style="font-size:12px;color:var(--text-muted)">'
        '&#x2295; Generate custom agents: '
        '<a href="#" onclick="showTab(\'marketplace-factory\')" '
        'style="color:var(--accent);text-decoration:none">Agent Factory</a>'
        "</p>\n"
        + js
        + "</div>\n"
    )
