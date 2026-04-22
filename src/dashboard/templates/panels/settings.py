"""Settings & Configuration panels."""
from .._components import (
    simple_panel,
    tab_panel,
)


def _settings() -> str:
    return tab_panel(
        "settings",
        "&#x1f4c4; Claude SDK Settings",
        '<div id="settings-content" style="padding:16px;color:var(--text-muted)">Loading settings...</div>',
    )


def _settings_cybersecsuite() -> str:
    return tab_panel(
        "settings-cybersecsuite",
        "&#x1f6e0; CyberSecSuite Settings",
        '<div id="settings-cs-content" style="padding:16px;color:var(--text-muted)">Loading CyberSecSuite settings...</div>',
    )


def _crypto() -> str:
    return simple_panel("crypto", "&#x1f512; Artifact Signing", "crypto-content", "Loading crypto stats...")


def _qol_controls() -> str:
    return tab_panel(
        "qol-controls",
        "&#x229E; QoL Output Controls",
        """<div style="padding:16px;max-width:720px">
  <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px">
    Server-side behaviour directives injected into every outbound LLM request.
    Toggle on to add, toggle off to remove. Changes apply to the next request.
  </p>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
    <label style="font-size:12px;color:var(--text-muted)">Scope:</label>
    <select id="qol-scope-select" onchange="loadQolControls()"
      style="font-size:12px;padding:4px 8px;background:var(--surface-2);color:var(--text-primary);border:1px solid var(--border);border-radius:4px">
      <option value="session">session</option>
      <option value="project">project</option>
      <option value="global">global</option>
    </select>
    <button onclick="qolReset()"
      style="font-size:11px;padding:4px 10px;background:var(--surface-2);color:var(--text-muted);border:1px solid var(--border);border-radius:4px;cursor:pointer;margin-left:auto">
      ↺ Reset
    </button>
  </div>
  <div id="qol-toggles" style="margin-bottom:20px">
    <span style="color:var(--text-muted);font-size:12px">Loading toggles...</span>
  </div>
  <div style="margin-bottom:20px">
    <div style="font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Presets</div>
    <div id="qol-presets"><span style="color:var(--text-muted);font-size:12px">Loading presets...</span></div>
  </div>
  <div>
    <div style="font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Injection Preview</div>
    <pre id="qol-preview"
      style="font-size:11px;font-family:var(--font-mono);background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:10px;white-space:pre-wrap;word-break:break-word;color:var(--text-muted);min-height:36px">
(no active toggles — no injection)</pre>
  </div>
  <div id="qol-status" style="font-size:11px;color:var(--red);margin-top:8px"></div>
</div>""",
    )

