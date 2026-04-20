"""
DESIGN DIRECTION: Cyber Operations Command Console — Industrial Terminal
TYPOGRAPHY: Space Grotesk (headings/UI) / JetBrains Mono (data/code)
COLOR PALETTE: #0d1117 base · #00ff41 phosphor-green accent · #f59e0b amber (warn) · #ef4444 threat-red · #00d4ff info-cyan
MOTION: Staggered card entrance (opacity+translateY), scanline sweep, sidebar item hover slide
LAYOUT: Fixed left sidebar (260px) + scrollable main content; sidebar groups tabs into 5 categories
"""

_FONT_LINKS = """\
<link rel="preconnect" href="https://fonts.bunny.net">
<link href="https://fonts.bunny.net/css?family=space-grotesk:400,500,600,700|jetbrains-mono:400,500,600" rel="stylesheet">
"""

_CSS = '<link rel="stylesheet" href="/static/css/dashboard.css">\n'

_TOAST_CSS = """\
<style>
#toast-container { position: fixed; bottom: 40px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; max-width: 360px; }
.toast { padding: 12px 16px; border-radius: 6px; font-size: 13px; font-family: var(--font-mono); display: flex; align-items: center; gap: 10px; animation: toast-in 0.3s ease-out; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.toast.toast-info { background: #0c4a6e; border-left: 3px solid #00d4ff; color: #e0f2fe; }
.toast.toast-success { background: #052e16; border-left: 3px solid #00ff41; color: #dcfce7; }
.toast.toast-warning { background: #451a03; border-left: 3px solid #f59e0b; color: #fef3c7; }
.toast.toast-error { background: #450a0a; border-left: 3px solid #ef4444; color: #fee2e2; }
.toast button { background: none; border: none; color: inherit; cursor: pointer; margin-left: auto; opacity: 0.7; }
.toast button:hover { opacity: 1; }
@keyframes toast-in { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
.toast.toast-out { animation: toast-out 0.3s ease-in forwards; }
@keyframes toast-out { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
</style>
"""

_TOAST_JS = """\
<script>
(function() {
  window.toast = function(msg, type, duration, action) {
    type = type || 'info'; duration = duration || 4000;
    var container = document.getElementById('toast-container');
    if (!container) { container = document.createElement('div'); container.id = 'toast-container'; document.body.appendChild(container); }
    var toast = document.createElement('div'); toast.className = 'toast toast-' + type;
    var icon = {info:'ℹ️', success:'✅', warning:'⚠️', error:'❌'}[type] || 'ℹ️';
    toast.innerHTML = '<span>' + icon + ' ' + msg + '</span>';
    if (action && action.label) {
      var btn = document.createElement('button'); btn.textContent = action.label;
      btn.onclick = function() { action.fn && action.fn(); container.removeChild(toast); };
      toast.appendChild(btn);
    }
    var close = document.createElement('button'); close.innerHTML = '×';
    close.onclick = function() { container.removeChild(toast); };
    toast.appendChild(close);
    container.appendChild(toast);
    if (duration > 0) { setTimeout(function() { if (toast.parentNode) { toast.className += ' toast-out'; setTimeout(function() { toast.remove(); }, 300); } }, duration); }
  };
})();
</script>
"""


def head() -> str:
    return (
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>CyberSecSuite // Command Console</title>\n"
        '<script src="https://cdn.tailwindcss.com"></script>\n'
        + _FONT_LINKS
        + _CSS
        + _TOAST_CSS
        + "\n</head>\n"
    )


def header() -> str:
    """Top bar: tab breadcrumb + refresh/uptime. Includes bottom status bar."""
    return (
        '<div id="topbar">\n'
        '  <div id="topbar-title" id="topbar-crumb">&#x25b6; PROVIDERS</div>\n'
        '  <div id="topbar-actions">\n'
        '    <span id="uptime"></span>\n'
        '    <button class="btn btn-ghost" onclick="refresh()">&#x21bb; REFRESH</button>\n'
        '  </div>\n'
        '</div>\n'
        '<div id="statusbar" style="'
        'position: fixed; bottom: 0; left: var(--sidebar-w); right: 0;'
        'height: 24px; background: var(--accent);'
        'display: flex; align-items: center; padding: 0 16px; gap: 16px;'
        'font-family: var(--font-mono); font-size: 10px; color: rgba(255,255,255,0.85);'
        'z-index: 200; border-top: 1px solid var(--border-glow);'
        '">\n'
        '  <span id="sb-tab">&#x2B21; PROVIDERS</span>\n'
        '  <span style="margin-left:auto" id="sb-time"></span>\n'
        '</div>\n'
    )


def context_bar() -> str:
    """Dynamic context bar between topbar and content — updated by JS per tab."""
    return (
        '<div id="context-bar" style="'
        'display:none;'
        'background:var(--bg-deep);'
        'border-bottom:1px solid var(--border);'
        'padding:8px 24px;'
        'align-items:center;gap:20px;'
        'font-family:var(--font-mono);font-size:11px;'
        '">\n'
        '  <span id="ctx-label" style="color:var(--text-faint);letter-spacing:.08em;text-transform:uppercase;font-size:9px;margin-right:4px"></span>\n'
        '  <span id="ctx-s1" class="ctx-stat" style="display:none"></span>\n'
        '  <span id="ctx-s2" class="ctx-stat" style="display:none"></span>\n'
        '  <span id="ctx-s3" class="ctx-stat" style="display:none"></span>\n'
        '  <span id="ctx-s4" class="ctx-stat" style="display:none"></span>\n'
        '  <span id="ctx-s5" class="ctx-stat" style="display:none"></span>\n'
        '</div>\n'
        '<style>\n'
        '.ctx-stat { color:var(--text-muted); }\n'
        '.ctx-stat strong { color:var(--accent); font-weight:600; margin-right:3px; }\n'
        '.ctx-stat + .ctx-stat::before { content:"·"; color:var(--text-faint); margin-right:16px; }\n'
        '.af-check { display:inline-flex;align-items:center;gap:5px;padding:4px 8px;'
        'background:var(--surface);border:1px solid var(--border);border-radius:4px;'
        'cursor:pointer;font-size:11px;font-family:var(--font-mono);color:var(--text-muted); }\n'
        '.af-check:hover { border-color:var(--accent); }\n'
        '.af-check input { accent-color:var(--accent); }\n'
        '</style>\n'
    )


def stats_row() -> str:
    return ""


def tiers_row() -> str:
    return ""
