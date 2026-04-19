"""
DESIGN DIRECTION: Cyber Operations Command Console — Industrial Terminal
TYPOGRAPHY: Space Grotesk (headings/UI) / JetBrains Mono (data/code)
COLOR PALETTE: #0d1117 base · #00ff41 phosphor-green accent · #f59e0b amber (warn) · #ef4444 threat-red · #00d4ff info-cyan
MOTION: Staggered card entrance (opacity+translateY), scanline sweep, sidebar item hover slide
LAYOUT: Fixed left sidebar (260px) + scrollable main content; sidebar groups tabs into 5 categories
"""

_CSS = """\
<link rel="preconnect" href="https://fonts.bunny.net">
<link href="https://fonts.bunny.net/css?family=space-grotesk:400,500,600,700|jetbrains-mono:400,500,600" rel="stylesheet">
<style>
/* ── Design tokens ── */
:root {
  --bg:          #0d1117;
  --bg-deep:     #080b10;
  --surface:     #111820;
  --surface-2:   #161d28;
  --border:      #1e2d3d;
  --border-glow: rgba(99,102,241,0.35);
  --accent:      #6366f1;
  --accent-dim:  #4f46e5;
  --accent-glow: rgba(99,102,241,0.12);
  --cyan:        #38bdf8;
  --cyan-glow:   rgba(56,189,248,0.12);
  --amber:       #f59e0b;
  --amber-glow:  rgba(245,158,11,0.12);
  --red:         #ef4444;
  --red-glow:    rgba(239,68,68,0.12);
  --violet:      #a78bfa;
  --success:      #10b981;
  --success-glow: rgba(16,185,129,0.12);
  --text-primary:  #e2eaf4;
  --text-muted:    #64748b;
  --text-faint:    #374151;
  --font-ui:   'Space Grotesk', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --sidebar-w: 260px;
  --header-h:  56px;
  --radius:    8px;
  --radius-lg: 12px;
}

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 14px;
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Subtle grid texture */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(99,102,241,0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99,102,241,0.015) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* Scanline overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.04) 2px,
    rgba(0,0,0,0.04) 4px
  );
  pointer-events: none;
  z-index: 0;
}

/* ── Layout shell ── */
#shell {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* ── Sidebar ── */
#sidebar {
  width: var(--sidebar-w);
  min-height: 100vh;
  background: var(--bg-deep);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 100;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}

#sidebar-logo {
  padding: 18px 20px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

#sidebar-logo .logo-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--accent);
  text-shadow: 0 0 20px var(--border-glow);
  display: flex;
  align-items: center;
  gap: 8px;
}

#sidebar-logo .logo-sub {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 2px;
  letter-spacing: 0.05em;
}

#sidebar-status {
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--accent); }
  50%       { opacity: 0.6; box-shadow: 0 0 4px var(--accent); }
}

#sidebar-nav { flex: 1; padding: 8px 0 20px; }

.nav-group-label {
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-faint);
  padding: 16px 20px 4px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  border-left: 2px solid transparent;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab:hover {
  background: rgba(99,102,241,0.05);
  color: var(--text-primary);
  border-left-color: rgba(99,102,241,0.3);
}

.tab.active {
  background: var(--accent-glow);
  color: var(--accent);
  border-left-color: var(--accent);
  font-weight: 600;
}

.tab.active .tab-icon { filter: drop-shadow(0 0 4px var(--accent)); }

.tab-icon { font-size: 14px; flex-shrink: 0; width: 18px; text-align: center; }

/* ── Main content ── */
#main {
  margin-left: var(--sidebar-w);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ── Top header bar ── */
#topbar {
  height: var(--header-h);
  background: rgba(13,17,23,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

#topbar-title {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  text-transform: uppercase;
}

#topbar-actions { display: flex; align-items: center; gap: 12px; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius);
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.btn-ghost {
  background: transparent;
  border-color: var(--border);
  color: var(--text-muted);
}

.btn-ghost:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-glow);
}

.btn-accent {
  background: var(--accent-glow);
  border-color: var(--accent);
  color: var(--accent);
}

.btn-accent:hover {
  background: rgba(99,102,241,0.2);
  box-shadow: 0 0 12px var(--border-glow);
}

#uptime {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-faint);
}

/* ── Content area ── */
#content { padding: 24px; flex: 1; }

/* ── Stats row ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-pill {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  text-align: center;
  transition: border-color 0.2s, box-shadow 0.2s;
  animation: enter-up 0.4s cubic-bezier(0.22,1,0.36,1) both;
}

.stat-pill:nth-child(1) { animation-delay: 0.05s; }
.stat-pill:nth-child(2) { animation-delay: 0.10s; }
.stat-pill:nth-child(3) { animation-delay: 0.15s; }
.stat-pill:nth-child(4) { animation-delay: 0.20s; }
.stat-pill:nth-child(5) { animation-delay: 0.25s; }
.stat-pill:nth-child(6) { animation-delay: 0.30s; }

.stat-pill:hover {
  border-color: var(--accent-dim);
  box-shadow: 0 0 16px var(--accent-glow);
}

.stat-pill .val {
  font-family: var(--font-mono);
  font-size: 22px;
  font-weight: 600;
  color: var(--accent);
  line-height: 1;
}

.stat-pill .lbl {
  font-size: 10px;
  font-family: var(--font-mono);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ── Tier row ── */
.tiers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.tier-pill {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  text-align: center;
  animation: enter-up 0.4s cubic-bezier(0.22,1,0.36,1) both;
}

.tier-pill:nth-child(1) { animation-delay: 0.35s; }
.tier-pill:nth-child(2) { animation-delay: 0.40s; }
.tier-pill:nth-child(3) { animation-delay: 0.45s; }
.tier-pill:nth-child(4) { animation-delay: 0.50s; }

.tier-pill .tier-val {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 600;
  margin-top: 6px;
}

@keyframes enter-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Cards / panels ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: border-color 0.2s;
}

.card:hover { border-color: var(--border-glow); }

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  flex: 1;
}

.panel-accent-bar {
  width: 3px;
  height: 18px;
  background: var(--accent);
  border-radius: 2px;
  box-shadow: 0 0 8px var(--accent);
  flex-shrink: 0;
}

/* ── Stat cards (forensic panels) ── */
.stat-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  text-align: center;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 22px;
  font-weight: 600;
  color: var(--cyan);
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ── Mini cards ── */
.mini-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 12px;
  text-align: center;
}

/* ── Tables ── */
table { width: 100%; border-collapse: collapse; font-size: 13px; }

thead tr {
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: 8px 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  cursor: pointer;
  white-space: nowrap;
}

th:hover { color: var(--accent); }

td {
  padding: 8px 10px;
  border-bottom: 1px solid rgba(30,45,61,0.5);
  font-family: var(--font-mono);
  font-size: 12px;
  vertical-align: middle;
}

tr:last-child td { border-bottom: none; }

tr:hover td {
  background: rgba(99,102,241,0.03);
}

/* Search + filter bar */
.rt-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.rt-search {
  padding: 6px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-primary);
  outline: none;
  width: 220px;
  transition: border-color 0.15s;
}

.rt-search:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }

.rt-count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

/* Pagination */
.rt-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.rt-btn {
  padding: 4px 10px;
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer !important;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  appearance: none;
  -webkit-appearance: none;
}

.rt-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.rt-btn:disabled { opacity: 0.3; cursor: default; }

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.badge-free     { background: rgba(99,102,241,0.12);  color: var(--accent); border: 1px solid rgba(99,102,241,0.3); }
.badge-budget   { background: rgba(56,189,248,0.10);  color: var(--cyan);   border: 1px solid rgba(56,189,248,0.3); }
.badge-standard { background: rgba(167,139,250,0.12); color: var(--violet); border: 1px solid rgba(167,139,250,0.3); }
.badge-premium  { background: rgba(239,68,68,0.12);   color: var(--red);    border: 1px solid rgba(239,68,68,0.3); }
.badge-ok       { background: rgba(16,185,129,0.12);  color: var(--success); border: 1px solid rgba(16,185,129,0.3); }
.badge-err      { background: rgba(239,68,68,0.12);   color: var(--red);    border: 1px solid rgba(239,68,68,0.3); }
.badge-browser  { background: rgba(167,139,250,0.12); color: var(--violet); border: 1px solid rgba(167,139,250,0.3); }
.badge-warn     { background: rgba(245,158,11,0.12);  color: var(--amber);  border: 1px solid rgba(245,158,11,0.3); }

/* ── Progress ── */
.progress { height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--cyan));
  transition: width 0.6s cubic-bezier(0.22,1,0.36,1);
}

/* ── Forms ── */
input[type=text], input[type=number], input[type=email],
textarea, select {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 8px 12px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
}

input:focus, textarea:focus, select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-glow);
}

label {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
  display: block;
  margin-bottom: 4px;
}

/* ── Section headings ── */
.section-h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 2px solid var(--accent);
}

.section-h4 {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 16px 0 8px;
}

/* ── Loading state ── */
@keyframes pulse-glow {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.4; }
}

.loading {
  animation: pulse-glow 1.8s ease-in-out infinite;
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 12px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* ── Section panel enter animation ── */
.panel-enter {
  animation: enter-up 0.35s cubic-bezier(0.22,1,0.36,1) both;
}

/* ── Glow text ── */
.glow-green { color: var(--accent); text-shadow: 0 0 16px rgba(99,102,241,0.5); }
.glow-cyan  { color: var(--cyan);   text-shadow: 0 0 16px rgba(0,212,255,0.5); }

/* ── Responsive ── */
@media (max-width: 1024px) {
  :root { --sidebar-w: 220px; }
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
  .tiers-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ── Toggle switches (settings panel) ── */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid rgba(30,45,61,0.5);
}
.toggle-row:last-child { border-bottom: none; }
.toggle-label { font-family: var(--font-mono); font-size: 12px; color: var(--text-primary); }
.toggle-sub   { font-family: var(--font-mono); font-size: 10px; color: var(--text-muted); margin-top: 2px; }
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}
.toggle-switch input { display: none; }
.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 11px;
  transition: background 0.2s, border-color 0.2s;
}
.toggle-slider::before {
  content: '';
  position: absolute;
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background: var(--text-faint);
  border-radius: 50%;
  transition: transform 0.2s, background 0.2s;
}
.toggle-switch input:checked + .toggle-slider {
  background: var(--accent-glow);
  border-color: var(--accent);
}
.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(18px);
  background: var(--accent);
  box-shadow: 0 0 6px rgba(99,102,241,0.5);
}
.toggle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2px;
}
.toggles-loading { color: var(--text-muted); font-family: var(--font-mono); font-size: 12px; padding: 12px 0; }
</style>"""


def head() -> str:
    return (
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>CyberSecSuite // Command Console</title>\n"
        '<script src="https://cdn.tailwindcss.com"></script>\n'
        + _CSS
        + "\n</head>\n"
    )


def header() -> str:
    """Top bar: tab breadcrumb + refresh/uptime."""
    return (
        '<div id="topbar">\n'
        '  <div id="topbar-title" id="topbar-crumb">&#x25b6; PROVIDERS</div>\n'
        '  <div id="topbar-actions">\n'
        '    <span id="uptime"></span>\n'
        '    <button class="btn btn-ghost" onclick="refresh()">&#x21bb; REFRESH</button>\n'
        '  </div>\n'
        '</div>\n'
    )


def stats_row() -> str:
    return (
        '<div class="stats-grid">\n'
        '  <div class="stat-pill"><div class="val" id="s-providers">-</div><div class="lbl">Providers</div></div>\n'
        '  <div class="stat-pill"><div class="val" id="s-enabled">-</div><div class="lbl">Enabled</div></div>\n'
        '  <div class="stat-pill"><div class="val" id="s-models">-</div><div class="lbl">Models</div></div>\n'
        '  <div class="stat-pill"><div class="val" id="s-requests">-</div><div class="lbl">Requests</div></div>\n'
        '  <div class="stat-pill"><div class="val" id="s-tokens">-</div><div class="lbl">Tokens</div></div>\n'
        '  <div class="stat-pill"><div class="val" id="s-cost">-</div><div class="lbl">Cost USD</div></div>\n'
        '</div>\n'
    )


def tiers_row() -> str:
    return (
        '<div class="tiers-grid">\n'
        '  <div class="tier-pill"><span class="badge badge-free">FREE</span><div class="tier-val glow-green" id="t-free">-</div></div>\n'
        '  <div class="tier-pill"><span class="badge badge-budget">BUDGET</span><div class="tier-val glow-cyan" id="t-budget">-</div></div>\n'
        '  <div class="tier-pill"><span class="badge badge-standard">STD</span><div class="tier-val" style="color:var(--violet)" id="t-standard">-</div></div>\n'
        '  <div class="tier-pill"><span class="badge badge-premium">PREMIUM</span><div class="tier-val" style="color:var(--red)" id="t-premium">-</div></div>\n'
        '</div>\n'
    )
