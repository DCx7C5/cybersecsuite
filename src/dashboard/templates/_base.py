"""
DESIGN DIRECTION: Cyber Operations Command Console — Industrial Terminal
TYPOGRAPHY: Space Grotesk (headings/UI) / JetBrains Mono (data/code)
COLOR PALETTE: centralized via CSS vars (base neutrals + mode accent + amber/red/success/cyan semantic tones)
MOTION: Staggered card entrance (opacity+translateY), scanline sweep, sidebar item hover slide
LAYOUT: Fixed left sidebar (260px) + scrollable main content; sidebar groups tabs into 5 categories
"""

from ._tabs import topbar_nav_menu

_FONT_LINKS = """\
<link rel="preconnect" href="https://fonts.bunny.net">
<link href="https://fonts.bunny.net/css?family=space-grotesk:400,500,600,700|jetbrains-mono:400,500,600" rel="stylesheet">
"""

_CSS = (
    '<link rel="stylesheet" href="/static/css/dashboard.css">\n'
    '<link rel="stylesheet" href="/static/css/themes.css">\n'
)

# CDN: Chart.js 4, Apache ECharts 5, Drawflow
_CDN_SCRIPTS = (
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>\n'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/drawflow@0.0.59/dist/drawflow.min.css">\n'
    '<script src="https://cdn.jsdelivr.net/npm/drawflow@0.0.59/dist/drawflow.min.js"></script>\n'
)

_TOAST_CSS = """\
<style>
#toast-container { position: fixed; bottom: 40px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; max-width: 360px; }
.toast { padding: 12px 16px; border-radius: 6px; font-size: 13px; font-family: var(--font-mono); display: flex; align-items: center; gap: 10px; animation: toast-in 0.3s ease-out; background: var(--surface-2); color: var(--text-primary); border: 1px solid var(--border); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.toast.toast-info { border-left: 3px solid var(--cyan); }
.toast.toast-success { border-left: 3px solid var(--success); }
.toast.toast-warning { border-left: 3px solid var(--amber); }
.toast.toast-error { border-left: 3px solid var(--red); }
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
        + _CDN_SCRIPTS
        + "\n</head>\n"
    )


def header() -> str:
    """Top bar: tab breadcrumb + refresh/uptime + sidebar toggle + mode toggle. Includes bottom status bar."""
    plugin_checker_js = """
    <script>
    (function() {
      const pluginStatus = document.getElementById('plugin-status');
      
      async function checkPluginStatus() {
        try {
          const res = await fetch('/api/plugin/status', { timeout: 2000 });
          if (res.ok) {
            const data = await res.json();
            if (data.active) {
              pluginStatus.style.display = 'flex';
            } else {
              pluginStatus.style.display = 'none';
            }
          } else {
            pluginStatus.style.display = 'none';
          }
        } catch (e) {
          pluginStatus.style.display = 'none';
        }
      }
      
      // Check on load and every 5 seconds
      checkPluginStatus();
      setInterval(checkPluginStatus, 5000);
    })();
    </script>
    """
    
    return (
        '<div id="topbar">\n'
        '  <div style="display:flex;align-items:center;gap:8px">\n'
        '    <button id="sidebar-toggle" class="btn btn-ghost" onclick="toggleSidebar()" style="width:40px;height:40px" title="Collapse sidebar" aria-label="Collapse sidebar" aria-controls="sidebar" aria-expanded="true">&#x25c4;</button>\n'
        f'{topbar_nav_menu()}'
        '    <div id="topbar-title" id="topbar-crumb">&#x25b6; PROVIDERS</div>\n'
        '  </div>\n'
        '  <div id="topbar-actions" style="display:flex;align-items:center;gap:12px">\n'
        '    <div id="plugin-status" style="display:none;align-items:center;gap:6px;padding:4px 12px;background:rgba(34,197,94,0.1);border:1px solid rgb(34,197,94);border-radius:4px;font-size:11px;font-family:var(--font-mono);color:rgb(34,197,94)">\n'
        '      <span style="width:6px;height:6px;background:rgb(34,197,94);border-radius:50%;display:inline-block;animation:pulse-led 2s infinite"></span>\n'
        '      <span id="plugin-status-text">Plugin Active</span>\n'
        '    </div>\n'
        '    <div style="display:flex;gap:4px;padding:0 8px;border-right:1px solid var(--border)">\n'
        '      <button id="mode-btn-blue" class="mode-button active" onclick="setThemeMode(\'blue\')" title="Blue Team">🔵</button>\n'
        '      <button id="mode-btn-purple" class="mode-button" onclick="setThemeMode(\'purple\')" title="Purple Team">🟣</button>\n'
        '      <button id="mode-btn-red" class="mode-button" onclick="setThemeMode(\'red\')" title="Red Team">🔴</button>\n'
        '    </div>\n'
        '    <span id="uptime"></span>\n'
        '    <button class="btn btn-ghost" onclick="refresh()">&#x21bb; REFRESH</button>\n'
        '  </div>\n'
        '</div>\n'
        '<style>\n'
        '@keyframes pulse-led { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }\n'
        '#plugin-status { display:flex; }\n'
        '.topbar-nav { position:relative; display:none; }\n'
        '.topbar-nav-menu { position:absolute; top:calc(100% + 8px); left:0; min-width:260px; max-height:70vh; overflow:auto; display:none; padding:8px 0; background:var(--surface-2); border:1px solid var(--border); border-radius:8px; box-shadow:0 12px 30px rgba(0,0,0,0.35); z-index:120; }\n'
        '.topbar-nav.open .topbar-nav-menu { display:block; }\n'
        '.topbar-nav-group { padding:10px 14px 4px; font-family:var(--font-mono); font-size:10px; letter-spacing:.12em; color:var(--text-faint); text-transform:uppercase; }\n'
        '.topbar-nav-item { width:100%; display:flex; align-items:center; gap:8px; padding:7px 14px; border:0; background:transparent; color:var(--text-muted); font:inherit; cursor:pointer; text-align:left; }\n'
        '.topbar-nav-item:hover { background:var(--accent-glow); color:var(--text-primary); }\n'
        'body.sidebar-collapsed .topbar-nav { display:block; }\n'
        '</style>\n'
        + plugin_checker_js +
        '<div id="statusbar" style="'
        'position: fixed; bottom: 0; right: 0;'
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
