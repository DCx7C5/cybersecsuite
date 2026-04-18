"""Base structural HTML: <head>, header bar, stats row, tiers row."""

_CSS = """\
<style>
  body { background: #0a0e17; color: #e2e8f0; font-family: 'JetBrains Mono', 'Fira Code', monospace; }
  .card { background: #111827; border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1.25rem; }
  .card:hover { border-color: #0ff3; }
  .glow { text-shadow: 0 0 10px #0ff6; }
  .badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
  .badge-free { background: #064e3b; color: #34d399; }
  .badge-budget { background: #1e3a5f; color: #60a5fa; }
  .badge-standard { background: #3b2f63; color: #a78bfa; }
  .badge-premium { background: #5b2130; color: #fb7185; }
  .badge-ok { background: #064e3b; color: #34d399; }
  .badge-err { background: #5b2130; color: #fb7185; }
  .badge-browser { background: #312e81; color: #818cf8; }
  .progress { height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; }
  .progress-bar { height: 100%; background: linear-gradient(90deg, #0ff, #6366f1); transition: width 0.5s; }
  .stat-card { background: #111827; border: 1px solid #1e293b; border-radius: 0.5rem; padding: 0.75rem; text-align: center; }
  .stat-value { font-size: 1.5rem; font-weight: 700; }
  .stat-label { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 0.5rem; border-bottom: 1px solid #1e293b; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }
  td { padding: 0.5rem; border-bottom: 1px solid #1e293b08; font-size: 0.875rem; }
  tr:hover td { background: #1e293b40; }
  .tab { cursor: pointer; padding: 0.5rem 1rem; border-bottom: 2px solid transparent; color: #94a3b8; }
  .tab.active { border-color: #0ff; color: #0ff; }
  .tab:hover { color: #e2e8f0; }
  @keyframes pulse-glow { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
  .loading { animation: pulse-glow 1.5s infinite; }
</style>"""


def head() -> str:
    return (
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>CyberSecSuite Dashboard</title>\n"
        '<script src="https://cdn.tailwindcss.com"></script>\n'
        "<script>tailwindcss_config={theme:{extend:{colors:{cyber:'#0ff',dark:'#0a0e17'}}}}</script>\n"
        + _CSS
        + "\n</head>\n"
    )


def header() -> str:
    return (
        "  <!-- Header -->\n"
        '  <div class="flex items-center justify-between mb-8">\n'
        "    <div>\n"
        '      <h1 class="text-2xl font-bold glow" style="color:#0ff">&#x1f6e1; CyberSecSuite</h1>\n'
        '      <p class="text-sm text-gray-500 mt-1">AI Proxy Dashboard &mdash; Multi-Provider Router</p>\n'
        "    </div>\n"
        '    <div class="flex gap-3">\n'
        '      <button onclick="refresh()" class="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700">&#x21bb; Refresh</button>\n'
        '      <span id="uptime" class="text-xs text-gray-500 self-center"></span>\n'
        "    </div>\n"
        "  </div>\n"
    )


def stats_row() -> str:
    return (
        "  <!-- Stats row -->\n"
        '  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6" id="stats">\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-providers">-</div><div class="text-xs text-gray-500">Providers</div></div>\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-enabled">-</div><div class="text-xs text-gray-500">Enabled</div></div>\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-models">-</div><div class="text-xs text-gray-500">Models</div></div>\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-requests">-</div><div class="text-xs text-gray-500">Requests</div></div>\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-tokens">-</div><div class="text-xs text-gray-500">Tokens</div></div>\n'
        '    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-cost">-</div><div class="text-xs text-gray-500">Cost (USD)</div></div>\n'
        "  </div>\n"
    )


def tiers_row() -> str:
    return (
        "  <!-- Tier breakdown -->\n"
        '  <div class="grid grid-cols-4 gap-4 mb-6" id="tiers">\n'
        '    <div class="card text-center"><span class="badge badge-free">FREE</span><div class="text-xl font-bold mt-2" id="t-free">-</div></div>\n'
        '    <div class="card text-center"><span class="badge badge-budget">BUDGET</span><div class="text-xl font-bold mt-2" id="t-budget">-</div></div>\n'
        '    <div class="card text-center"><span class="badge badge-standard">STANDARD</span><div class="text-xl font-bold mt-2" id="t-standard">-</div></div>\n'
        '    <div class="card text-center"><span class="badge badge-premium">PREMIUM</span><div class="text-xl font-bold mt-2" id="t-premium">-</div></div>\n'
        "  </div>\n"
    )
