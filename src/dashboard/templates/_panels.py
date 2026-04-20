"""All 23 dashboard tab panels."""
from ._components import (
    action_bar,
    btn,
    code_preview,
    divider,
    filter_bar,
    form_field,
    form_input,
    form_label,
    form_select,
    form_textarea,
    grid,
    info_box,
    loading_slot,
    mini_card,
    mini_grid,
    modal_overlay,
    panel_section,
    section_badge,
    section_h4,
    simple_panel,
    stat_card,
    stat_grid,
    status_span,
    tab_panel,
    table_slot,
)


def _providers() -> str:
    return tab_panel(
        "providers",
        "&#x1f310; Provider Registry",
        '<div id="providers-table"><div class="loading text-gray-500">Loading providers...</div></div>',
        hidden=False,
    )


def _usage() -> str:
    return simple_panel("usage", "&#x1f4c8; Recent Requests", "usage-table", "Loading usage...")


def _health() -> str:
    return (
        '<div id="tab-health" class="card" style="display:none">\n'
        '  <h2>&#x2764; System Health</h2>\n'
        '  <div id="health-error" class="health-error-banner"></div>\n'
        '  <div class="health-services">\n'
        '    <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-db-dot"></span>'
        '<span class="svc-name">Database</span>'
        '<span class="svc-detail" id="health-db-detail">—</span></div>\n'
        '    <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-redis-dot"></span>'
        '<span class="svc-name">Redis</span>'
        '<span class="svc-detail" id="health-redis-detail">—</span></div>\n'
        '    <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-oo-dot"></span>'
        '<span class="svc-name">OpenObserve</span>'
        '<span class="svc-detail" id="health-oo-detail">—</span></div>\n'
        '    <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-proxy-dot"></span>'
        '<span class="svc-name">AI Proxy</span>'
        '<span class="svc-detail" id="health-proxy-detail">—</span></div>\n'
        '  </div>\n'
        '  <div class="stat-row">\n'
        '    <div class="stat-box"><span id="health-tables">—</span><br><small>Tables</small></div>\n'
        '    <div class="stat-box"><span id="health-providers">—</span><br><small>Providers On</small></div>\n'
        '    <div class="stat-box"><span id="health-providers-free">—</span><br><small>Free</small></div>\n'
        '    <div class="stat-box"><span id="health-uptime">—</span><br><small>Uptime</small></div>\n'
        '    <div class="stat-box"><span id="health-intel">—</span><br><small>Intel</small></div>\n'
        '    <div class="stat-box"><span id="health-local-llm">—</span><br><small>Local LLM</small></div>\n'
        '  </div>\n'
        '  <div id="health-content"></div>\n'
        '</div>\n'
    )


def _agents() -> str:
    return simple_panel("agents", "&#x1f916; Agent Registry", "agents-content", "Loading agents...")


def _routing() -> str:
    return simple_panel("routing", "&#x1f500; Routing Engine", "routing-content", "Loading routing...")


def _factory() -> str:
    return simple_panel("factory", "&#x1f3ed; Agent Factory", "factory-content", "Loading factory...")


def _prompts() -> str:
    return simple_panel("prompts", "&#x1f4dd; Prompts &amp; Templates", "prompts-content", "Loading prompts...")


def _crypto() -> str:
    return simple_panel("crypto", "&#x1f512; Artifact Signing", "crypto-content", "Loading crypto stats...")


def _a2a() -> str:
    return simple_panel("a2a", "&#x1f916; A2A Agent Tasks", "a2a-content", "Loading A2A stats...")


def _investigations() -> str:
    return simple_panel(
        "investigations", "&#x1f50d; Investigations", "inv-content", "Loading investigation stats..."
    )


def _dbcounts() -> str:
    return simple_panel("dbcounts", "&#x1f4ca; Database Table Counts", "db-content", "Loading DB counts...")


def _cases() -> str:
    counters = mini_grid(
        mini_card("cases-total", "Total Cases"),
        mini_card("cases-open", "Open", "text-green-400"),
        mini_card("cases-closed", "Closed", "text-gray-400"),
        cols=3,
    )
    return tab_panel(
        "cases",
        "&#x1f4c2; Phase 0 Case Intake",
        counters,
        table_slot("cases-table", loading=True, loading_text="Loading cases..."),
    )


def _tasks() -> str:
    counters = mini_grid(
        mini_card("tasks-total", "Total"),
        mini_card("tasks-submitted", "Submitted", "text-blue-400"),
        mini_card("tasks-working", "Working", "text-yellow-400"),
        mini_card("tasks-completed", "Done", "text-green-400"),
        mini_card("tasks-failed", "Failed", "text-red-400"),
        cols=5,
    )
    return tab_panel(
        "tasks",
        "&#x23f1; Task Management",
        counters,
        table_slot("tasks-table", loading=True, loading_text="Loading tasks..."),
    )


def _pocs() -> str:
    return simple_panel("pocs", "&#x1f4a3; Proof-of-Concept Exploits", "pocs-content", "Loading PoC data...")


def _findings() -> str:
    return tab_panel(
        "findings",
        "&#x1f6a8; Security Findings",
        stat_grid(
            stat_card("findings-total", "Total"),
            stat_card("findings-critical", "Critical"),
            stat_card("findings-high", "High"),
            stat_card("findings-24h", "Last 24h"),
        ),
        table_slot("findings-table"),
    )


def _iocs() -> str:
    return tab_panel(
        "iocs",
        "&#x1f4cc; Indicators of Compromise",
        stat_grid(
            stat_card("iocs-total", "Total IOCs"),
            stat_card("iocs-active", "Active"),
            stat_card("iocs-high-conf", "High Conf"),
            stat_card("iocs-types", "Types"),
        ),
        table_slot("iocs-table"),
    )


def _yara() -> str:
    return tab_panel(
        "yara",
        "&#x1f9ec; YARA Rules",
        stat_grid(
            stat_card("yara-total", "Total Rules"),
            stat_card("yara-active", "Active"),
            stat_card("yara-detections", "Detections"),
            stat_card("yara-sources", "Sources"),
        ),
        table_slot("yara-table"),
    )


def _network() -> str:
    return tab_panel(
        "network",
        "&#x1f5a7; Network Assets",
        stat_grid(
            stat_card("net-hosts", "Hosts"),
            stat_card("net-compromised", "Compromised"),
            stat_card("net-ips", "IP Addresses"),
            stat_card("net-countries", "Countries"),
        ),
        section_h4("Recent Hosts"),
        table_slot("network-hosts-table"),
        section_h4("Recent IPs"),
        table_slot("network-ips-table"),
    )


def _intel() -> str:
    return tab_panel(
        "intel",
        "&#x1f9e0; Threat Intelligence",
        stat_grid(
            stat_card("intel-techniques", "MITRE Techniques"),
            stat_card("intel-cve", "CVEs"),
            stat_card("intel-cwe", "CWEs"),
            stat_card("intel-capec", "CAPECs"),
        ),
        section_h4("Recent MITRE Techniques"),
        table_slot("intel-mitre-table"),
        section_h4("Recent CVEs"),
        table_slot("intel-cve-table"),
    )


def _audit() -> str:
    return tab_panel(
        "audit",
        "&#x1f4cb; Audit Log",
        stat_grid(
            stat_card("audit-total", "Total Events"),
            stat_card("audit-last-hour", "Last Hour"),
            stat_card("audit-agents", "Active Agents"),
            cols=3,
        ),
        table_slot("audit-table"),
    )


def _compliance() -> str:
    return tab_panel(
        "compliance",
        "&#x2705; Compliance Rules",
        stat_grid(
            stat_card("comp-total", "Total Rules"),
            stat_card("comp-critical", "Critical"),
            stat_card("comp-frameworks", "Frameworks"),
            stat_card("comp-high", "High"),
        ),
        table_slot("compliance-table"),
    )


def _agent_query() -> str:
    return (
        '<div id="tab-agent-query" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-3">&#x1f916; Interactive Agent Query</h3>\n'
        '  <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">\n'
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Search</label>\n'
        '      <input id="aq-agent-search" type="text" placeholder="Filter agents..." oninput="_aqApplyAgentFilters()"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" />\n'
        "    </div>\n"
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Source</label>\n'
        '      <select id="aq-source" onchange="_aqApplyAgentFilters()"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="">All sources</option>\n'
        "      </select>\n"
        "    </div>\n"
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Role</label>\n'
        '      <select id="aq-role" onchange="_aqApplyAgentFilters()"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="">All roles</option>\n'
        "      </select>\n"
        "    </div>\n"
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Model</label>\n'
        '      <select id="aq-model" onchange="_aqApplyAgentFilters()"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="">All models</option>\n'
        "      </select>\n"
        "    </div>\n"
        "  </div>\n"
        '  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Agent</label>\n'
        '      <select id="aq-agent"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="cybersec-agent">cybersec-agent</option>\n'
        "      </select>\n"
        "    </div>\n"
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Context Table (optional)</label>\n'
        '      <select id="aq-context-table"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="">None</option>\n'
        "      </select>\n"
        "    </div>\n"
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Row IDs (comma-sep)</label>\n'
        '      <input id="aq-row-ids" type="text" placeholder="e.g. 1,2,3"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" />\n'
        "    </div>\n"
        "  </div>\n"
        '  <p id="aq-agent-help" class="text-xs text-gray-500 mb-3">Loading agent options...</p>\n'
        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Prompt <span class="text-gray-600">(Ctrl+Enter to send)</span></label>\n'
        '    <textarea id="aq-prompt" rows="4" placeholder="Ask the agent anything&hellip;"\n'
        '      class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none resize-y font-mono"\n'
        "      onkeydown=\"if(event.ctrlKey&&event.key==='Enter'){event.preventDefault();runAgentQuery();}\"></textarea>\n"
        "  </div>\n"
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <button onclick="runAgentQuery()"\n'
        '      class="px-4 py-2 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors"\n'
        '      id="aq-submit">&#x25b6; Run Query</button>\n'
        '    <button onclick="clearAgentHistory()"\n'
        '      class="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-xs rounded-lg transition-colors">Clear History</button>\n'
        '    <span id="aq-status" class="text-xs text-gray-500"></span>\n'
        "  </div>\n"
        '  <div id="aq-history" class="space-y-4"></div>\n'
        "</div>\n"
    )


def _chat() -> str:
    return (
        '<div id="tab-chat" class="card" style="display:none">\n'
        '  <div class="flex items-center justify-between mb-3">\n'
        '    <h3 class="text-lg font-semibold">&#x1f4ac; Agent Chat</h3>\n'
        '    <span id="chat-status" class="text-xs font-mono" style="color:var(--text-muted)">Ready</span>\n'
        "  </div>\n"
        '  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Agent</label>\n'
        '      <select id="chat-agent"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="cybersec-agent">cybersec-agent</option>\n'
        "      </select>\n"
        "    </div>\n"
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Mode</label>\n'
        '      <button id="chat-stream-toggle" onclick="acChatToggleStream()"\n'
        '        class="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 text-xs rounded-lg transition-colors">Streaming: ON</button>\n'
        "    </div>\n"
        '    <div class="flex items-end gap-2">\n'
        '      <button id="chat-export" onclick="acChatExport()" class="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-xs rounded-lg transition-colors">Export</button>\n'
        '      <button id="chat-clear" onclick="acChatClear()" class="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-xs rounded-lg transition-colors">Clear</button>\n'
        "    </div>\n"
        "  </div>\n"
        '  <div id="chat-output"\n'
        '    style="height:360px;overflow-y:auto;padding:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-deep);margin-bottom:12px"></div>\n'
        '  <div>\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Prompt <span class="text-gray-600">(Shift+Enter for newline)</span></label>\n'
        '    <textarea id="chat-input" rows="4" placeholder="Ask the selected agent&hellip;"\n'
        '      class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none resize-y font-mono"></textarea>\n'
        "  </div>\n"
        '  <div class="flex items-center gap-3 mt-3">\n'
        '    <button id="chat-send" onclick="acChatSend()" class="px-4 py-2 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors">&#x25b6; Send</button>\n'
        '    <button id="chat-stop" onclick="acChatStop()" class="px-4 py-2 bg-red-700 hover:bg-red-600 text-sm rounded-lg font-semibold transition-colors" style="display:none">Stop</button>\n'
        "  </div>\n"
        "</div>\n"
    )


def _team_builder() -> str:
    return (
        '<div id="tab-team-builder" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-4">&#x1f3d7; Team Builder</h3>\n'

        # ── Sub-Agent Browser ────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Sub-Agent Browser</h4>\n'
        '  <div class="flex items-center gap-3 mb-3">\n'
        '    <input id="tb-agent-q" type="text" placeholder="Search agents..." oninput="tbFilterAgents(this.value)"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:240px">\n'
        '    <span id="tb-agent-count" class="text-xs text-gray-500"></span>\n'
        '  </div>\n'
        '  <div id="tb-agents-table" class="mb-6"></div>\n'

        # ── Team Composer ────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Team Composer</h4>\n'
        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Team Name</label>\n'
        '    <input id="tb-team-name" type="text" placeholder="my-team"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:300px">\n'
        '  </div>\n'
        '  <div id="tb-members" class="space-y-2 mb-3"></div>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <button onclick="tbAddMember()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">+ Add Member</button>\n'
        '    <button onclick="tbGenerateTeam()"\n'
        '      class="px-4 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors">Preview JSON</button>\n'
        '    <button onclick="tbSaveTeam()"\n'
        '      class="px-4 py-1.5 bg-green-700 hover:bg-green-600 text-sm rounded-lg font-semibold transition-colors">&#x1f4be; Save Team</button>\n'
        '    <button onclick="tbCopyTeam()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">Copy</button>\n'
        '    <span id="tb-save-status" class="text-xs"></span>\n'
        '  </div>\n'

        # ── Saved Teams ──────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Saved Teams</h4>\n'
        '  <div id="tb-saved-teams" class="mb-4"></div>\n'

        '  <pre id="tb-team-json" class="bg-gray-900 border border-gray-700 rounded-lg p-4 text-xs font-mono text-gray-300 whitespace-pre-wrap" style="display:none;max-height:300px;overflow-y:auto"></pre>\n'
        "</div>\n"
    )




def _agent_crafter() -> str:
    _models = [
        ("sonnet", "Claude Sonnet"),
        ("haiku",  "Claude Haiku"),
        ("opus",   "Claude Opus"),
    ]
    _tool_names   = ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Task"]
    _default_on   = {"Read", "Write", "Edit", "Bash", "Glob", "Grep"}

    tools_widget = (
        '<div id="ac-tools" style="display:flex;flex-wrap:wrap;gap:6px">\n'
        + "".join(
            f'  <label class="af-check">'
            f'<input type="checkbox" value="{t}"'
            + (" checked" if t in _default_on else "")
            + f"> {t}</label>\n"
            for t in _tool_names
        )
        + "</div>"
    )

    new_agent = panel_section(
        "New Agent",
        grid(
            form_field("Name *",      form_input("ac-name", placeholder="my-analyst",
                                                  extra_style="font-family:var(--font-mono)")),
            form_field("Description", form_input("ac-desc", placeholder="What this agent does…")),
            form_field("Model",       form_select("ac-model", _models)),
            form_field("Max turns",   form_input("ac-maxturns", type="number", value="25")),
            template="1fr 1fr 1fr 100px",
        ),
        grid(
            form_field("Tools", tools_widget),
            form_field("MCP servers",
                       form_input("ac-mcp", value="cybersec", placeholder="cybersec, dystopian",
                                  extra_style="font-family:var(--font-mono);font-size:12px"),
                       hint="comma-separated"),
        ),
        form_field("Instructions",
                   form_textarea("ac-instructions", rows=5,
                                 placeholder="## Role\nYou are a specialist that…", mono=True),
                   hint="markdown body"),
        action_bar(
            btn("+ Create Agent", onclick="acCreateAgent()", cls="btn btn-accent"),
            status_span("ac-status"),
        ),
    )

    edit_modal = modal_overlay(
        "ac-edit-modal",
        (
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">\n'
            '  <h4 class="text-sm font-semibold" style="color:var(--text-primary)">Edit Agent: '
            '<span id="ac-edit-name" style="color:var(--accent);font-family:var(--font-mono)"></span></h4>\n'
            + btn("✕", onclick="acCloseEdit()", cls="",
                  extra_style="background:none;border:none;color:var(--text-muted);font-size:18px;cursor:pointer")
            + "\n</div>"
        ),
        grid(
            form_field("Model",       form_select("ac-edit-model",
                                                   [("sonnet", "Sonnet"), ("haiku", "Haiku"), ("opus", "Opus")])),
            form_field("Max turns",   form_input("ac-edit-maxturns", type="number", value="25")),
            form_field("Description", form_input("ac-edit-desc")),
            cols=3,
        ),
        form_field("Instructions",
                   form_textarea("ac-edit-instructions", rows=10, mono=True)),
        action_bar(
            btn("💾 Save",  onclick="acSaveEdit()",  cls="btn btn-accent"),
            btn("Cancel",  onclick="acCloseEdit()", cls="btn"),
            status_span("ac-edit-status"),
        ),
        width="600px",
    )

    return tab_panel(
        "agent-crafter",
        "✎ Agent Crafter",
        '<p class="text-xs mb-4" style="color:var(--text-muted)">Create, edit and delete agent '
        '<code>.md</code> files in <code>.claude/agents/</code>.</p>',
        filter_bar("ac-filter", "Filter agents…", "acFilterAgents()", "ac-count",
                   btn("↺ Refresh", onclick="acLoadAgents()",
                       extra_style="font-size:11px;padding:4px 12px")),
        table_slot("ac-agents-table"),
        new_agent,
        edit_modal,
    )


def _agent_factory() -> str:
    _models = [
        ("sonnet", "Claude Sonnet"),
        ("haiku",  "Claude Haiku"),
        ("opus",   "Claude Opus"),
    ]
    _tool_names = ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Task"]
    _default_on = {"Read", "Write", "Edit", "Bash", "Glob", "Grep"}

    tools_widget = (
        '<div id="af-tools" style="display:flex;flex-wrap:wrap;gap:6px">\n'
        + "".join(
            f'  <label class="af-check"><input type="checkbox" value="{t}"'
            + (" checked" if t in _default_on else "")
            + f"> {t}</label>\n"
            for t in _tool_names
        )
        + "</div>"
    )

    type_select = (
        form_select("af-type", [
            ("specialist",  "Specialist"),
            ("team-leader", "Team leader"),
            ("orchestrator","Orchestrator"),
        ])
        + '\n<p id="af-type-hint" style="font-size:10px;color:var(--text-faint);'
        'margin-top:3px;font-family:var(--font-mono)">Focused expert — executes tasks, returns results.</p>'
    )

    def labeled_rows(label: str, row_id: str, onclick: str, btn_text: str, hint: str = "") -> str:
        """Flex header row (label left, inline button right) + a collapsible rows container."""
        return (
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">\n'
            f'  {form_label(label, hint=hint)}\n'
            f'  {btn(btn_text, onclick=onclick, extra_style="font-size:11px;padding:3px 10px")}\n'
            '</div>\n'
            f'<div id="{row_id}" style="display:flex;flex-direction:column;gap:6px">\n'
            f'  <div style="display:flex;align-items:center;gap:6px">\n'
            f'    <select id="{row_id}-0" style="flex:1;padding:6px 10px;'
            f'background:var(--surface-2);border:1px solid var(--border);'
            f'border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono)">\n'
            '      <option value="">— none —</option>\n'
            '    </select>\n'
            '  </div>\n'
            '</div>'
        )

    research_checks = (
        '<div style="display:flex;flex-wrap:wrap;gap:8px">\n'
        '  <label class="af-check"><input type="checkbox" id="af-r-mitre" value="mitre"> MITRE ATT&amp;CK</label>\n'
        '  <label class="af-check"><input type="checkbox" id="af-r-cve" value="cve"> CVE database</label>\n'
        '  <label class="af-check"><input type="checkbox" id="af-r-tools" value="tools"> Tool docs</label>\n'
        '  <label class="af-check"><input type="checkbox" id="af-r-api" value="api"> API reference</label>\n'
        '</div>'
    )

    context_toggles = (
        '<div style="display:flex;align-items:center;gap:24px">\n'
        '  <label class="af-check" style="font-size:13px">'
        '<input type="checkbox" id="af-project-ctx"> Include project context (.claude/)</label>\n'
        '  <label class="af-check" style="font-size:13px">'
        '<input type="checkbox" id="af-save-file" checked> Save to .claude/agents/</label>\n'
        '</div>'
    )

    return tab_panel(
        "agent-factory",
        "🏭 Agent Factory",
        '<p class="text-xs mb-5" style="color:var(--text-muted)">Generate production-grade agent definitions '
        'saved to <code>.claude/agents/</code>.</p>',
        grid(
            form_field("Agent type", type_select),
            form_field("Name *",     form_input("af-name", placeholder="my-analyst",
                                                extra_style="font-family:var(--font-mono)")),
            form_field("Model",      form_select("af-model", _models)),
            form_field("Max turns",  form_input("af-maxturns", type="number", value="30")),
            template="1fr 1fr 1fr 110px",
        ),
        form_field("Description",
                   form_textarea("af-desc", rows=2, placeholder="What this agent specialises in...")),
        labeled_rows("Base templates", "af-tpl-rows", "afAddTemplate()", "+ Add template",
                     hint="agents/agents/"),
        labeled_rows("Skills", "af-skill-rows", "afAddSkill()", "+ Add skill"),
        grid(
            form_field("Tools", tools_widget),
            form_field("MCP servers",
                       form_input("af-mcp", value="cybersec", placeholder="cybersec, dystopian",
                                  extra_style="font-family:var(--font-mono);font-size:12px"),
                       hint="comma-separated"),
        ),
        form_field("Instructions",
                   form_textarea("af-instructions", rows=5,
                                 placeholder="## Role\nYou are a specialist that...", mono=True),
                   hint="markdown body"),
        form_field("Research sections", research_checks, hint="WebFetch on generate"),
        context_toggles,
        form_field("Extra instructions",
                   form_textarea("af-extra", rows=3,
                                 placeholder="Focus on XYZ domain. Must include T1055 detection. Report format: ...",
                                 mono=True),
                   hint="appended to factory prompt"),
        action_bar(
            btn("🏭 Generate Agent", onclick="afGenerate()", cls="btn btn-accent"),
            status_span("af-status"),
        ),
        code_preview("af-preview", max_h="400px"),
    )


def _workflows() -> str:
    return tab_panel(
        "workflows",
        "🔄 Workflow Builder",
        '<p class="text-xs mb-4" style="color:var(--text-muted)">Create multi-step agent pipelines. '
        'Steps run in dependency order; use <code>{{step_id}}</code> in prompts to reference prior results.</p>',
        panel_section(
            "New workflow",
            form_field(
                "Workflow name",
                '<input id="wf-name" type="text" placeholder="my-investigation" '
                'class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg '
                'focus:border-cyan-500 outline-none" style="width:300px">',
            ),
            '<div id="wf-steps" class="space-y-3 mb-3"></div>',
            action_bar(
                btn("+ Add step", onclick="wfAddStep()",
                    extra_style="padding:6px 12px;font-size:12px"),
                btn("▶ Execute",  onclick="wfExecute()", cls="btn btn-accent"),
                btn("Clear",      onclick="wfClear()",
                    extra_style="padding:6px 12px;font-size:12px"),
                status_span("wf-status"),
            ),
        ),
        panel_section("History", '<div id="wf-history" class="space-y-4"></div>'),
    )



def _settings() -> str:
    global_badge  = section_badge("🌐 Global ~/.claude", "#38bdf8")
    project_badge = section_badge("📁 Project .claude/", "#6366f1")

    # ── project selector ────────────────────────────────────────────────────
    project_selector = (
        '<div style="margin-bottom:16px">\n'
        + form_field(
            "Active project",
            '<select id="settings-project-select" onchange="switchActiveProject(this.value)"'
            ' style="width:100%;max-width:300px">'
            '<option value="">None (Global only)</option>'
            '</select>',
        )
        + '\n</div>'
    )

    # ── scope switcher buttons ────────────────────────────────────────────────
    scope_bar = (
        '<div style="display:flex;gap:8px;margin-bottom:24px;'
        'border-bottom:1px solid var(--border);padding-bottom:16px">\n'
        + f'  {btn("🌐 Global ~/.claude", onclick="switchSettingsScope(\'global\')", cls="btn btn-accent", extra_style="font-size:12px")}\n'
        + f'  {btn("📁 Project .claude/", onclick="switchSettingsScope(\'project\')", cls="btn btn-ghost", extra_style="font-size:12px")}\n'
        + '</div>'
    )

    # ── MCP installer form (content only — panel_section wraps it) ────────────
    _hook_events = [
        ("PreToolUse", "PreToolUse"), ("PostToolUse", "PostToolUse"),
        ("Stop", "Stop"), ("SessionStart", "SessionStart"),
        ("UserPromptSubmit", "UserPromptSubmit"), ("SubagentStart", "SubagentStart"),
        ("SubagentStop", "SubagentStop"), ("TeammateIdle", "TeammateIdle"),
        ("PreCompact", "PreCompact"), ("PostCompact", "PostCompact"),
        ("Notification", "Notification"),
    ]
    mcp_installer_content = (
        grid(
            form_field("Server name", form_input("mcp-install-name", placeholder="e.g. my-mcp-server")),
            form_field("Command",     form_input("mcp-install-cmd",  placeholder="e.g. uvx, npx, node")),
            cols=2,
        )
        + form_field("Args (comma-separated)",
                     form_input("mcp-install-args", placeholder="e.g. @modelcontextprotocol/server-filesystem, /tmp"))
        + '\n'
        + form_field("Env vars (KEY=VALUE, one per line)",
                     form_textarea("mcp-install-env", rows=3, placeholder="API_KEY=xxx\nDEBUG=1", mono=True))
        + '\n'
        + action_bar(
            btn("+ Install MCP", onclick="installMcp()", cls="btn btn-accent"),
            status_span("mcp-install-status"),
        )
    )

    hooks_content = (
        loading_slot("settings-global-hooks")
        + '\n'
        + divider(label="Add new hook")
        + section_h4("Add New Hook")
        + grid(
            form_field("Event",                    form_select("hook-add-event", _hook_events)),
            form_field("Matcher (regex, optional)", form_input("hook-add-matcher", placeholder=".*")),
            cols=2,
        )
        + form_field("Command", form_input("hook-add-cmd", placeholder="e.g. python3 /path/to/hook.py"))
        + '\n'
        + action_bar(
            btn("+ Add Hook", onclick="addHook()", cls="btn btn-accent"),
            status_span("hook-add-status"),
        )
    )

    notifications_content = (
        '<label class="flex items-center gap-3 cursor-pointer">\n'
        '  <input type="checkbox" id="settings-dbus-enable" class="toggle"'
        ' onchange="toggleDbusNotifications(this.checked)" />\n'
        '  <span class="text-sm">Enable desktop notifications</span>\n'
        '</label>\n'
        '<div id="dbus-status" class="text-xs mt-2 text-gray-500"></div>'
    )

    ro_label = ' <span style="font-weight:400;font-size:11px;color:var(--text-muted)">(read-only)</span>'

    # ══ GLOBAL SCOPE PANE ══ ────────────────────────────────────────────────
    global_pane = (
        '<div id="settings-scope-global">\n'
        f'  <div style="margin-bottom:20px">{global_badge}</div>\n'
        + panel_section("MCP servers", loading_slot("settings-global-mcps"),
                        desc="MCP servers in ~/.claude/settings.json. Toggle to enable/disable globally.")
        + '\n'
        + panel_section("Install new MCP server", mcp_installer_content,
                        desc="Add a new MCP server to ~/.claude/settings.json. Restart Claude Code to activate.")
        + '\n'
        + panel_section("Plugins", loading_slot("settings-plugins"),
                        desc="Plugins installed in ~/.claude. Toggle writes to ~/.claude/settings.json.")
        + '\n'
        + panel_section("Desktop notifications", notifications_content,
                        desc="Toggle to enable desktop notifications for task completion, findings, etc.")
        + '\n'
        + panel_section(f"Environment variables{ro_label}", loading_slot("settings-global-env"))
        + '\n'
        + panel_section("Summary", loading_slot("settings-global"))
        + '\n'
        + panel_section("Hooks manager", hooks_content,
                        desc="Manage Claude Code hooks in ~/.claude/settings.json.")
        + '\n</div>\n'
    )

    # ══ PROJECT SCOPE PANE ══ ───────────────────────────────────────────────
    agent_proxy_content = (
        '<div id="settings-agent-form" class="space-y-3"></div>\n'
        + action_bar(
            btn("Save", onclick="saveSettingsAgent()", cls="btn btn-accent"),
            status_span("settings-agent-status"),
            gap=3,
        )
    )

    env_editor_content = (
        '<div id="settings-env-rows" class="space-y-2 mb-3"></div>\n'
        + action_bar(
            btn("+ Add variable", onclick="settingsAddEnvRow()", cls="btn btn-ghost"),
            btn("Save env",       onclick="saveSettingsEnv()",   cls="btn btn-accent"),
            status_span("settings-env-status"),
        )
    )

    project_pane = (
        '<div id="settings-scope-project" style="display:none">\n'
        f'  <div style="margin-bottom:20px">{project_badge}</div>\n'
        + panel_section("Agent &amp; Proxy", agent_proxy_content)
        + '\n'
        + panel_section("MCP servers", loading_slot("settings-mcps"),
                        desc="MCP servers from project mcp.json. Toggle stores state in .claude/settings.json.")
        + '\n'
        + panel_section("Skill domains",
                        '<div id="settings-skills" class="toggle-grid toggles-loading">Loading…</div>',
                        desc="Enable or disable skill domain libraries from .claude/skills/.")
        + '\n'
        + panel_section(f"Environment variables{ro_label}", loading_slot("settings-project-env"))
        + '\n'
        + panel_section(
            f"Hooks{ro_label}",
            '<div id="settings-hooks-table"></div>',
            mb=4,
        )
        + '\n'
        + panel_section("Custom env overrides", env_editor_content)
        + '\n</div>\n'
    )

    # ══ LOCAL LLM ══ ────────────────────────────────────────────────────────
    local_llm_content = (
        '<div id="local-llm-providers" style="margin-bottom:12px">'
        '<span class="text-xs text-gray-500">Loading...</span></div>\n'
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">\n'
        '  <select id="local-llm-model" style="flex:1;max-width:300px">'
        '<option value="">Select a local model...</option></select>\n'
        + f'  {btn("Activate",   onclick="activateLocalLlm()",   cls="btn btn-accent", extra_style="font-size:12px")}\n'
        + f'  {btn("Deactivate", onclick="deactivateLocalLlm()", cls="btn btn-ghost",  extra_style="font-size:12px")}\n'
        + '</div>\n'
        + status_span("local-llm-status")
    )

    local_llm = (
        divider()
        + panel_section("🖥️ Local LLM", local_llm_content,
                        desc="Connect to a local Ollama or LM Studio instance for offline AI.")
    )

    return tab_panel(
        "settings",
        "⚙️ Claude Settings",
        project_selector,
        scope_bar,
        global_pane,
        project_pane,
        local_llm,
    )


def _telemetry() -> str:
    return (
        '<div id="tab-telemetry" class="card" style="display:none">\n'
        '  <div class="flex items-center justify-between mb-3">\n'
        '    <h3 class="text-lg font-semibold">&#x1f4ca; Live Telemetry</h3>\n'
        '    <span id="sse-status" class="badge badge-standard">&#x25cf; SSE 0/4</span>\n'
        "  </div>\n"
        '  <p class="text-xs text-gray-500 mb-4">Metrics update every 5 s via SSE. '
        "p50/p95/p99 in milliseconds, rps = requests/second.</p>\n"
        '  <div id="telemetry-content" class="loading">Waiting for telemetry stream...</div>\n'
        "</div>\n"
    )


def _opensearch() -> str:
    return (
        '<div id="tab-opensearch" class="card" style="display:none">\n'
        '  <div class="flex items-center justify-between mb-3">\n'
        '    <h3 class="text-lg font-semibold">&#x1f50d; OpenObserve</h3>\n'
        '    <button onclick="loadOpenSearch()" class="btn btn-sm">&#x21bb; Refresh</button>\n'
        "  </div>\n"
        '  <div id="os-cluster" class="mb-4"></div>\n'
        '  <div id="os-indices"></div>\n'
        "</div>\n"
    )


def _explorer() -> str:
    return (
        '<div id="tab-explorer" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-3">&#x1f50e; Database Explorer</h3>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <select id="explorer-model" onchange="loadExplorerTable()"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '      <option value="">Select a model...</option>\n'
        "    </select>\n"
        '    <span id="explorer-count" class="text-xs text-gray-500"></span>\n'
        "  </div>\n"
        '  <div id="explorer-table"></div>\n'
        "</div>\n"
    )


def _templates() -> str:
    return (
        '<div id="tab-templates" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-3">&#x25ad; Templates</h3>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <select id="template-type" onchange="loadTemplates()"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg">\n'
        '      <option value="">All Types</option>\n'
        '      <option value="agents">Agents</option>\n'
        '      <option value="skills">Skills</option>\n'
        '      <option value="hooks">Hooks</option>\n'
        '      <option value="mcp">MCP</option>\n'
        "    </select>\n"
        '    <input type="text" id="template-search" placeholder="Search..."\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg"\n'
        '      oninput="loadTemplates()">\n'
        '    <button onclick="createTemplate()" class="px-3 py-1.5 text-sm bg-cyan-600 hover:bg-cyan-500 rounded-lg">+ New</button>\n'
        "</div>\n"
        '  <div id="template-list" class="grid gap-2"></div>\n'
        "</div>\n"
    )


def _settings_cybersecsuite() -> str:
    from ._components import (
        section_badge, info_box, form_field, form_input, form_select,
        action_bar, btn, status_span, loading_slot, divider,
    )
    cs_badge = section_badge("⚙ CyberSecSuite", "#00ff41")
    return (
        '<div id="tab-settings-cybersecsuite" class="card" style="display:none">\n'
        '  <div class="panel-header">'
        '<div class="panel-accent-bar"></div>'
        '<span class="panel-title">⚙ CyberSecSuite Settings</span>'
        '</div>\n'
        f'  <div style="margin-bottom:20px">{cs_badge}</div>\n'

        # ── Database ──
        '  <div class="section-h3">Database</div>\n'
        + info_box("PostgreSQL connection used by the forensics backend.")
        + '  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">\n'
        + f'    {form_field("Host", form_input("cs-db-host", placeholder="localhost"))}\n'
        + f'    {form_field("Port", form_input("cs-db-port", placeholder="5432", type="number"))}\n'
        + '  </div>\n'
        + '  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px">\n'
        + f'    {form_field("User", form_input("cs-db-user", placeholder="cybersec"))}\n'
        + f'    {form_field("Password", form_input("cs-db-pass", placeholder="••••••••", type="password"))}\n'
        + f'    {form_field("Database", form_input("cs-db-name", placeholder="cybersec_forensics"))}\n'
        + '  </div>\n'
        + action_bar(
            btn("Test Connection", onclick="csTestDbConnection()", cls="btn btn-ghost", extra_style="font-size:12px"),
            status_span("cs-db-status"),
        )
        + '\n'

        # ── Bootstrap ──
        + divider(label="INTELLIGENCE BOOTSTRAP")
        + '  <div class="section-h3">Database Bootstrap</div>\n'
        + info_box("Seed NIST CSF, MITRE, CWE, CAPEC and PoC data into the database.")
        + '  <div id="cs-bootstrap-status-box" style="margin-bottom:12px"></div>\n'
        + action_bar(
            btn("▶ Run Bootstrap", onclick="window._bootstrapRun && _bootstrapRun()", cls="btn btn-accent", extra_style="font-size:12px"),
            btn("↺ Refresh Status", onclick="csRefreshBootstrap()", cls="btn btn-ghost", extra_style="font-size:12px"),
            status_span("cs-bootstrap-status"),
        )
        + '\n'

        # ── Workspace ──
        + divider(label="WORKSPACE")
        + '  <div class="section-h3">Workspace &amp; Project</div>\n'
        + info_box("Sets the active scope for findings, IOCs, and cases.")
        + '  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">\n'
        + f'    {form_field("Workspace", form_input("cs-workspace", placeholder="default"))}\n'
        + f'    {form_field("Project", form_input("cs-project", placeholder="my-project"))}\n'
        + '  </div>\n'

        # ── Intel Dir ──
        + f'  {form_field("Intel Directory", form_input("cs-intel-dir", placeholder="./data/cybersec-shared/intelligence"))}\n'
        + '  <div style="margin-top:8px">\n'
        + action_bar(
            btn("Save Workspace", onclick="csSaveWorkspace()", cls="btn btn-accent", extra_style="font-size:12px"),
            status_span("cs-workspace-status"),
        )
        + '\n  </div>\n'

        # ── AI Proxy ──
        + divider(label="AI PROXY")
        + '  <div class="section-h3">AI Proxy</div>\n'
        + info_box("ASGI proxy base URL and default routing strategy.")
        + '  <div style="display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-bottom:12px">\n'
        + f'    {form_field("Proxy Base URL", form_input("cs-proxy-url", placeholder="http://localhost:8000/v1"))}\n'
        + f'    {form_field("Routing Strategy", form_select("cs-routing-strategy", [("cost", "Cost"), ("latency", "Latency"), ("quality", "Quality"), ("round_robin", "Round Robin"), ("failover", "Failover")]))}\n'
        + '  </div>\n'
        + loading_slot("cs-proxy-status-box")
        + '\n'

        '</div>\n'
    )


def all_panels() -> str:
    return "".join([
        _providers(),
        _health(),
        _usage(),
        _telemetry(),
        _routing(),
        _agents(),
        _agent_factory(),
        _agent_crafter(),
        _team_builder(),
        _agent_query(),
        _chat(),
        _workflows(),
        _prompts(),
        _cases(),
        _tasks(),
        _pocs(),
        _a2a(),
        _investigations(),
        _findings(),
        _iocs(),
        _yara(),
        _network(),
        _intel(),
        _audit(),
        _compliance(),
        _dbcounts(),
        _opensearch(),
        _explorer(),
        _templates(),
        _settings(),
        _settings_cybersecsuite(),
    ])
