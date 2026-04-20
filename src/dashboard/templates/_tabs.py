"""Sidebar navigation — grouped vertical tabs with dropdown support."""

# Each entry is either:
#   (name, label, icon, group)               — standard tab
#   {"dropdown": True, "group": ...,          — collapsible dropdown
#    "id": ..., "label": ..., "icon": ...,
#    "children": [(name, label, icon), ...]}

_NAV: list = [
    # PLATFORM
    ("health",        "Health",           "♡", "platform"),
    ("usage",         "Usage & Cost",     "◈", "platform"),
    ("telemetry",     "Telemetry",        "◉", "platform"),
    # AI PROXY
    ("routing",       "Routing",          "⇄", "proxy"),
    # AGENTS
    ("agent-factory", "Agent Factory",    "⊞", "agents"),
    ("agent-crafter", "Agent Crafter",   "✎", "agents"),
    ("team-builder",  "Team Builder",     "⊟", "agents"),
    ("agent-query",   "Agent Query",      "⇒", "agents"),
    ("chat",          "Chat",             "💬", "agents"),
    ("workflows",     "Workflows",        "⇌", "agents"),
    ("flowgraph",     "Flowgraph",        "⬡", "agents"),
    ("prompts",       "Prompts",          "⊘", "agents"),
    ("sdk-lab",       "SDK Lab",          "⊗", "agents"),
    # OPERATIONS
    ("cases",         "Cases",            "⊡", "ops"),
    ("tasks",         "Tasks",            "⊛", "ops"),
    ("pocs",          "PoCs",             "⊕", "ops"),
    ("a2a",           "A2A Proto",        "⇋", "ops"),
    # FORENSICS
    ("investigations","Investigations",   "◉", "forensics"),
    ("findings",      "Findings",         "⊘", "forensics"),
    ("iocs",          "IOCs",             "◈", "forensics"),
    ("yara",          "YARA Rules",       "⊛", "forensics"),
    ("network",       "Network",          "⊡", "forensics"),
    ("intel",         "Intel Feed",       "◎", "forensics"),
    ("audit",         "Audit Log",        "⊕", "forensics"),
    ("compliance",    "Compliance",       "⊗", "forensics"),
    # DATA
    ("dbcounts",      "DB Counts",        "◉", "data"),
    ("opensearch",    "OpenObserve",       "⊘", "data"),
    ("explorer",      "Explorer",         "⊡", "data"),
    ("templates",    "Templates",         "◫", "data"),
    # SETTINGS — collapsible dropdown
    {
        "dropdown": True,
        "group": "settings",
        "id": "navd-settings",
        "label": "Claude SDK",
        "icon": "⊛",
        "children": [
            ("settings",              "Claude",         "◈"),
            ("settings-cybersecsuite","CyberSecSuite",  "◉"),
        ],
    },
]

_GROUPS = {
    "platform":   "PLATFORM",
    "proxy":      "AI PROXY",
    "agents":     "AGENTS",
    "ops":        "OPERATIONS",
    "forensics":  "FORENSICS",
    "data":       "DATA",
    "settings":   "SETTINGS",
}

# Inline CSS + JS injected once inside <nav>
_NAV_DROPDOWN_STYLE = """\
<style>
.nav-dropdown-header {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 16px; cursor: pointer;
  font-size: 12px; font-weight: 500; color: var(--text-muted);
  border-left: 2px solid transparent;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  user-select: none;
}
.nav-dropdown-header:hover {
  background: var(--accent-glow); color: var(--text-primary);
  border-left-color: var(--border-glow);
}
.nav-dropdown-header.open { color: var(--accent); }
.nav-dropdown-arrow {
  margin-left: auto; font-size: 10px;
  transition: transform 0.2s;
}
.nav-dropdown-header.open .nav-dropdown-arrow { transform: rotate(180deg); }
.nav-dropdown-body { overflow: hidden; max-height: 0; transition: max-height 0.25s ease; }
.nav-dropdown-body.open { max-height: 200px; }
.nav-sub-tab { padding-left: 36px !important; font-size: 11px !important; }
</style>
<script>
function toggleNavDropdown(id) {
  var hdr = document.getElementById(id + '-hdr');
  var body = document.getElementById(id + '-body');
  if (!hdr || !body) return;
  var open = body.classList.toggle('open');
  hdr.classList.toggle('open', open);
}
</script>
"""


def tab_bar() -> str:
    """Build grouped sidebar navigation HTML."""
    lines = [_NAV_DROPDOWN_STYLE, '<nav id="sidebar-nav">']
    current_group = None

    for entry in _NAV:
        # ── dropdown entry ────────────────────────────────────────────────
        if isinstance(entry, dict) and entry.get("dropdown"):
            group = entry["group"]
            if group != current_group:
                current_group = group
                lines.append(f'  <div class="nav-group-label">{_GROUPS[group]}</div>')
            did = entry["id"]
            lines.append(
                f'  <div class="nav-dropdown">\n'
                f'    <div class="nav-dropdown-header" id="{did}-hdr"'
                f' onclick="toggleNavDropdown(\'{did}\')">\n'
                f'      <span class="tab-icon">{entry["icon"]}</span>'
                f'{entry["label"]}'
                f'<span class="nav-dropdown-arrow">▾</span>\n'
                f'    </div>\n'
                f'    <div class="nav-dropdown-body" id="{did}-body">'
            )
            for name, label, icon in entry["children"]:
                lines.append(
                    f'      <div class="tab nav-sub-tab" onclick="showTab(\'{name}\')" id="nav-{name}">'
                    f'<span class="tab-icon">{icon}</span>{label}</div>'
                )
            lines.append('    </div>\n  </div>')
        # ── standard tab ─────────────────────────────────────────────────
        else:
            name, label, icon, group = entry
            if group != current_group:
                current_group = group
                lines.append(f'  <div class="nav-group-label">{_GROUPS[group]}</div>')
            lines.append(
                f'  <div class="tab" onclick="showTab(\'{name}\')" id="nav-{name}">'
                f'<span class="tab-icon">{icon}</span>{label}</div>'
            )

    lines.append("</nav>")
    return "\n".join(lines) + "\n"


def first_tab() -> str:
    """Return name of the default tab (first standard entry in nav list)."""
    for entry in _NAV:
        if isinstance(entry, tuple):
            return entry[0]
    return "health"
