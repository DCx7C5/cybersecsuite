"""Bootstrap modal — first-run database seeding prompt."""
from __future__ import annotations


def bootstrap_modal_html() -> str:
    """Return the hidden first-run bootstrap modal overlay HTML."""
    return """\
<!-- ═══════════════════════════════════════════════════════
     FIRST-RUN BOOTSTRAP MODAL
     Shown only if /api/bootstrap/status returns done=false.
     Hidden by default (display:none on #bootstrap-overlay).
═══════════════════════════════════════════════════════ -->
<style>
#bootstrap-overlay {
  display: none;
  position: fixed; inset: 0; z-index: 99999;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(4px);
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
}
#bootstrap-overlay.visible { display: flex; }
#bootstrap-modal {
  background: var(--bg-deep);
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 36px 40px 32px;
  max-width: 620px;
  width: 90%;
  box-shadow: 0 0 60px var(--accent-glow), 0 0 0 1px var(--border-glow);
  animation: modal-in 0.3s ease-out;
}
@keyframes modal-in {
  from { transform: translateY(-24px); opacity: 0; }
  to   { transform: translateY(0);     opacity: 1; }
}
#bootstrap-modal .bm-glyph {
  font-size: 32px; color: var(--accent); margin-bottom: 12px;
  text-shadow: 0 0 12px var(--border-glow);
}
#bootstrap-modal h2 {
  font-family: var(--font-ui, 'Space Grotesk', sans-serif);
  font-size: 20px; font-weight: 700; color: var(--text-primary);
  margin: 0 0 8px; letter-spacing: 0.02em;
}
#bootstrap-modal .bm-sub {
  font-size: 12px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.6;
}
#bootstrap-modal .bm-checklist {
  list-style: none; padding: 0; margin: 0 0 24px;
  display: flex; flex-direction: column; gap: 6px;
}
#bootstrap-modal .bm-checklist li {
  font-size: 12px; color: var(--text-muted);
  display: flex; align-items: center; gap: 8px;
}
#bootstrap-modal .bm-checklist li::before {
  content: '▸'; color: var(--accent); font-size: 10px;
}
#bootstrap-log-wrap {
  display: none;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 4px; padding: 10px 12px;
  max-height: 160px; overflow-y: auto;
  margin-bottom: 20px;
  font-size: 11px; color: var(--text-muted); line-height: 1.7;
}
#bootstrap-log-wrap.visible { display: block; }
#bootstrap-log-wrap .log-line { color: var(--text-muted); }
#bootstrap-log-wrap .log-line.ok { color: var(--success); }
#bootstrap-log-wrap .log-line.err { color: var(--red); }
#bootstrap-modal .bm-actions {
  display: flex; gap: 12px; justify-content: flex-end; align-items: center;
}
#bootstrap-modal .bm-btn {
  border: none; border-radius: 4px; cursor: pointer;
  font-family: inherit; font-size: 12px; font-weight: 600;
  padding: 8px 20px; transition: all 0.15s;
  letter-spacing: 0.05em; text-transform: uppercase;
}
#bootstrap-modal .bm-btn-primary {
  background: var(--accent); color: var(--bg-deep);
  box-shadow: 0 0 16px var(--accent-glow);
}
#bootstrap-modal .bm-btn-primary:hover:not(:disabled) {
  background: var(--accent-dim); box-shadow: 0 0 24px var(--accent-glow);
}
#bootstrap-modal .bm-btn-primary:disabled {
  opacity: 0.5; cursor: not-allowed;
}
#bootstrap-modal .bm-btn-ghost {
  background: transparent; color: var(--text-muted);
  border: 1px solid var(--border);
}
#bootstrap-modal .bm-btn-ghost:hover { color: var(--text-primary); border-color: var(--accent); }
#bootstrap-modal .bm-spinner {
  display: none; width: 14px; height: 14px;
  border: 2px solid var(--accent-glow);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
#bootstrap-modal .bm-spinner.visible { display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
#bootstrap-status-text {
  font-size: 11px; color: var(--text-muted); margin-right: auto;
}
</style>

<div id="bootstrap-overlay" role="dialog" aria-modal="true" aria-labelledby="bootstrap-title">
  <div id="bootstrap-modal">
    <div class="bm-glyph">⬡</div>
    <h2 id="bootstrap-title">Initialize Intelligence Database</h2>
    <p class="bm-sub">
      This appears to be the first run. The database needs to be seeded with
      threat intelligence before investigations can start.
    </p>
    <ul class="bm-checklist">
      <li>NIST Cybersecurity Framework 2.0 controls</li>
      <li>NIST AI Risk Management Framework 1.0</li>
      <li>MITRE ATT&amp;CK technique taxonomy</li>
      <li>CVE / CWE / CAPEC cross-references</li>
    </ul>

    <div id="bootstrap-log-wrap">
      <div id="bootstrap-log"></div>
    </div>

    <div class="bm-actions">
      <span id="bootstrap-status-text"></span>
      <div id="bootstrap-spinner" class="bm-spinner"></div>
      <button class="bm-btn bm-btn-ghost" id="bootstrap-skip-btn" onclick="window._bootstrapSkip()">
        Skip for now
      </button>
      <button class="bm-btn bm-btn-primary" id="bootstrap-run-btn" onclick="window._bootstrapRun()">
        ⬡ Bootstrap DB
      </button>
    </div>
  </div>
</div>
"""
