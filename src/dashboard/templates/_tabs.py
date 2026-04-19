"""Sidebar navigation — grouped vertical tabs replacing the 29-item horizontal bar."""

# (name, label, icon, group)
_NAV = [
    # OVERVIEW
    ("providers",   "Providers",      "⬡", "overview"),
    ("usage",       "Usage & Cost",   "◈", "overview"),
    ("health",      "Health",         "♡", "overview"),
    # AI PROXY
    ("routing",     "Routing",        "⇄", "proxy"),
    ("crypto",      "Crypto",         "⊗", "proxy"),
    # AGENTS
    ("agents",      "Agents",         "◎", "agents"),
    ("agent-craft", "Agent Craft",    "⊞", "agents"),
    ("team-builder","Team Builder",   "⊟", "agents"),
    ("agent-query", "Agent Query",    "⇒", "agents"),
    ("factory",     "Factory",        "⊕", "agents"),
    ("prompts",     "Prompts",        "⊘", "agents"),
    # OPS CENTER
    ("cases",       "Cases",          "⊡", "ops"),
    ("tasks",       "Tasks",          "⊛", "ops"),
    ("pocs",        "PoCs",           "⊕", "ops"),
    ("workflows",   "Workflows",      "⇌", "ops"),
    ("a2a",         "A2A Proto",      "⇋", "ops"),
    # FORENSICS
    ("investigations","Investigations","◉","forensics"),
    ("findings",    "Findings",       "⊘", "forensics"),
    ("iocs",        "IOCs",           "◈", "forensics"),
    ("yara",        "YARA Rules",     "⊛", "forensics"),
    ("network",     "Network",        "⊡", "forensics"),
    ("intel",       "Intel Feed",     "◎", "forensics"),
    ("audit",       "Audit Log",      "⊕", "forensics"),
    ("compliance",  "Compliance",     "⊗", "forensics"),
    # DATA
    ("dbcounts",    "DB Counts",      "◉", "data"),
    ("telemetry",   "Telemetry",      "◎", "data"),
    ("opensearch",  "OpenSearch",     "⊘", "data"),
    ("explorer",    "Explorer",       "⊡", "data"),
    # SETTINGS
    ("settings",    "Settings",       "⊛", "settings"),
]

_GROUPS = {
    "overview":   "OVERVIEW",
    "proxy":      "AI PROXY",
    "agents":     "AGENTS",
    "ops":        "OPS CENTER",
    "forensics":  "FORENSICS",
    "data":       "DATA",
    "settings":   "SETTINGS",
}


def tab_bar() -> str:
    """Build grouped sidebar navigation HTML."""
    lines = ['<nav id="sidebar-nav">']
    current_group = None
    for name, label, icon, group in _NAV:
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
    """Return name of the default tab (first in nav list)."""
    return _NAV[0][0]
