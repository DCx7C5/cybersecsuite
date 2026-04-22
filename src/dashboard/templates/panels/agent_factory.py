"""Marketplace Agent Factory panel — umbrella-keyword driven agent generator.

Renders the 'marketplace-factory' dashboard tab with an input form that POSTs
to /api/marketplace/generate-agent and displays the generated frontmatter.

Referenz:
    plan.md T038 — Dashboard Agent Factory UI tab
    src/dashboard/api/marketplace.py — /api/marketplace/generate-agent stub
    src/dashboard/templates/panels/advanced.py — _agent_factory() pattern
    src/dashboard/templates/_tabs.py — tab registration
"""
from __future__ import annotations


def _marketplace_agent_factory() -> str:
    """Render the Marketplace Agent Factory tab panel HTML.

    Returns:
        HTML string for the ``tab-marketplace-factory`` panel.
    """
    _inp = (
        "width:100%;padding:7px 10px;"
        "background:var(--surface-2);border:1px solid var(--border);"
        "border-radius:var(--radius);color:var(--text-primary);font-size:13px;"
        "font-family:var(--font-mono)"
    )
    _lbl = (
        "font-size:11px;font-weight:600;letter-spacing:.02em;"
        "color:var(--text-muted);display:block;margin-bottom:4px;"
        "font-family:var(--font-mono)"
    )
    _btn_accent = (
        "padding:7px 18px;background:var(--accent);color:#000;"
        "border:none;border-radius:var(--radius);font-size:13px;"
        "font-weight:600;cursor:pointer"
    )

    js = """<script>
(function () {
  async function mktGenerateAgent() {
    const keyword = document.getElementById('mkt-keyword').value.trim();
    const mode    = document.getElementById('mkt-mode').value;
    const status  = document.getElementById('mkt-af-status');
    const output  = document.getElementById('mkt-af-output');
    if (!keyword) { status.textContent = 'Enter an umbrella keyword first.'; return; }
    status.textContent = 'Generating…';
    output.textContent = '';
    try {
      const resp = await fetch('/api/marketplace/generate-agent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({keyword, mode}),
      });
      const data = await resp.json();
      if (data.status === 'not_implemented') {
        status.textContent = '⚠ ' + data.message;
        output.textContent = JSON.stringify(data, null, 2);
      } else if (data.frontmatter) {
        status.textContent = '✓ Generated';
        output.textContent = data.frontmatter;
      } else {
        status.textContent = 'Unexpected response';
        output.textContent = JSON.stringify(data, null, 2);
      }
    } catch (err) {
      status.textContent = 'Error: ' + err.message;
    }
  }
  window.mktGenerateAgent = mktGenerateAgent;
})();
</script>"""

    return (
        '<div id="tab-marketplace-factory" class="card" style="display:none">\n'
        '  <h3 style="font-size:1rem;font-weight:600;margin-bottom:4px">&#x2295; Marketplace Agent Factory</h3>\n'
        '  <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px">'
        "Generate provider-ready agent frontmatter from an umbrella keyword. "
        "Requires the <strong>agent-factory</strong> skill to be installed."
        "</p>\n"
        # ── Keyword input ──────────────────────────────────────────────────
        '  <div style="margin-bottom:12px">\n'
        f'    <label style="{_lbl}">Umbrella Keyword</label>\n'
        f'    <input id="mkt-keyword" placeholder="e.g. ransomware, phishing, osint…" style="{_inp}">\n'
        "  </div>\n"
        # ── Team mode selector ─────────────────────────────────────────────
        '  <div style="margin-bottom:16px">\n'
        f'    <label style="{_lbl}">Team Mode</label>\n'
        f'    <select id="mkt-mode" style="{_inp}">\n'
        '      <option value="blue">Blue (Defensive)</option>\n'
        '      <option value="red">Red (Offensive)</option>\n'
        '      <option value="purple">Purple (Collaborative)</option>\n'
        "    </select>\n"
        "  </div>\n"
        # ── Generate button + status ───────────────────────────────────────
        '  <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">\n'
        f'    <button onclick="mktGenerateAgent()" style="{_btn_accent}">&#x2699; Generate Agent</button>\n'
        '    <span id="mkt-af-status" style="font-size:12px;color:var(--text-muted)"></span>\n'
        "  </div>\n"
        # ── Output area ────────────────────────────────────────────────────
        '  <div>\n'
        f'    <label style="{_lbl}">Generated Frontmatter</label>\n'
        '    <pre id="mkt-af-output" style="'
        "min-height:120px;padding:12px;"
        "background:var(--surface-2);border:1px solid var(--border);"
        "border-radius:var(--radius);font-size:11px;"
        "font-family:var(--font-mono);white-space:pre-wrap;"
        'word-break:break-word;color:var(--text-primary)">(output will appear here)</pre>\n'
        "  </div>\n"
        # ── Marketplace browser link ───────────────────────────────────────
        '  <p style="font-size:12px;color:var(--text-muted);margin-top:16px">'
        '&#x1f4e6; Browse available items: '
        '<a href="#" onclick="showTab(\'marketplace\')" '
        'style="color:var(--accent);text-decoration:none">Marketplace</a>'
        "</p>\n"
        + js
        + "</div>\n"
    )
