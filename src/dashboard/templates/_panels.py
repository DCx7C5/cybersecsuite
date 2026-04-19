"""All 23 dashboard tab panels."""
from ._components import (
    mini_card,
    mini_grid,
    section_h4,
    simple_panel,
    stat_card,
    stat_grid,
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
        '  <div id="health-content" class="loading">Checking health...</div>\n'
        "</div>\n"
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


def _team_builder() -> str:
    return (
        '<div id="tab-team-builder" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-4">&#x1f3d7; Team Builder</h3>\n'

        # ── Agent Browser ────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Agent Browser</h4>\n'
        '  <div class="flex items-center gap-3 mb-3">\n'
        '    <input id="tb-agent-q" type="text" placeholder="Search agents..." oninput="tbFilterAgents(this.value)"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:240px">\n'
        '    <span id="tb-agent-count" class="text-xs text-gray-500"></span>\n'
        '  </div>\n'
        '  <div id="tb-agents-table" class="mb-6"></div>\n'

        # ── Skill Browser ────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Skill Browser</h4>\n'
        '  <div class="flex items-center gap-3 mb-3">\n'
        '    <select id="tb-skill-domain" onchange="tbLoadSkills()"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '      <option value="">All domains</option>\n'
        '    </select>\n'
        '    <input id="tb-skill-q" type="text" placeholder="Search skills..." oninput="tbLoadSkills()"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:200px">\n'
        '    <span id="tb-skill-count" class="text-xs text-gray-500"></span>\n'
        '  </div>\n'
        '  <div id="tb-skills-table" class="mb-6"></div>\n'

        # ── Team Composer ────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Team Composer</h4>\n'
        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Team Name</label>\n'
        '    <input id="tb-team-name" type="text" placeholder="my-team"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:300px">\n'
        '  </div>\n'
        '  <div id="tb-phases" class="space-y-2 mb-3"></div>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <button onclick="tbAddPhase()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">+ Add Phase</button>\n'
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


def _agent_craft() -> str:
    return (
        '<div id="tab-agent-craft" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-4">&#x1f527; Agent Craft</h3>\n'
        '  <p class="text-xs text-gray-500 mb-4">Create, edit, and delete custom agent definitions. Changes are saved to <code>.claude/agents/</code>.</p>\n'

        # ── Create Form ──────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Create Agent</h4>\n'
        '  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Name</label>\n'
        '      <input id="ac-name" type="text" placeholder="my-analyst"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none font-mono" />\n'
        '    </div>\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Model</label>\n'
        '      <select id="ac-model"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="sonnet">sonnet</option>\n'
        '        <option value="haiku">haiku</option>\n'
        '        <option value="opus">opus</option>\n'
        '      </select>\n'
        '    </div>\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Max Turns</label>\n'
        '      <input id="ac-maxturns" type="number" value="25" min="1" max="100"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" />\n'
        '    </div>\n'
        '  </div>\n'

        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Description</label>\n'
        '    <textarea id="ac-desc" rows="2" placeholder="What this agent specializes in..."\n'
        '      class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none resize-y"></textarea>\n'
        '  </div>\n'

        '  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Tools <span class="text-gray-600">(check to include)</span></label>\n'
        '      <div id="ac-tools" class="flex flex-wrap gap-2">\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Read" checked> Read</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Write" checked> Write</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Edit" checked> Edit</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Bash" checked> Bash</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Glob" checked> Glob</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Grep" checked> Grep</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="WebSearch"> WebSearch</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="WebFetch"> WebFetch</label>\n'
        '        <label class="inline-flex items-center gap-1 text-xs"><input type="checkbox" value="Task"> Task</label>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div>\n'
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">MCP Servers <span class="text-gray-600">(comma-sep)</span></label>\n'
        '      <input id="ac-mcp" type="text" value="cybersec" placeholder="cybersec, dystopian"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none font-mono" />\n'
        '    </div>\n'
        '  </div>\n'

        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Instructions <span class="text-gray-600">(markdown body)</span></label>\n'
        '    <textarea id="ac-instructions" rows="6" placeholder="## Role\\nYou are a specialist that..."\n'
        '      class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none resize-y font-mono"></textarea>\n'
        '  </div>\n'

        '  <div class="flex items-center gap-3 mb-6">\n'
        '    <button onclick="acCreateAgent()"\n'
        '      class="px-4 py-2 bg-green-700 hover:bg-green-600 text-sm rounded-lg font-semibold transition-colors">&#x2795; Create Agent</button>\n'
        '    <span id="ac-status" class="text-xs"></span>\n'
        '  </div>\n'

        # ── Existing Agents ──────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Existing Agents</h4>\n'
        '  <div class="flex items-center gap-3 mb-3">\n'
        '    <input id="ac-filter" type="text" placeholder="Filter agents..." oninput="acFilterAgents()"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:240px">\n'
        '    <button onclick="acLoadAgents()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">&#x21bb; Refresh</button>\n'
        '    <span id="ac-count" class="text-xs text-gray-500"></span>\n'
        '  </div>\n'
        '  <div id="ac-agents-table"></div>\n'

        # ── Edit Modal ───────────────────────────────────────────────────────
        '  <div id="ac-edit-modal" style="display:none" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">\n'
        '    <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">\n'
        '      <h4 class="text-lg font-semibold mb-3">Edit Agent: <span id="ac-edit-name" class="text-cyan-400"></span></h4>\n'
        '      <div class="grid grid-cols-2 gap-3 mb-3">\n'
        '        <div><label class="text-xs text-gray-400 block mb-1">Model</label>\n'
        '          <select id="ac-edit-model" class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg">\n'
        '            <option value="sonnet">sonnet</option><option value="haiku">haiku</option><option value="opus">opus</option>\n'
        '          </select></div>\n'
        '        <div><label class="text-xs text-gray-400 block mb-1">Max Turns</label>\n'
        '          <input id="ac-edit-maxturns" type="number" class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg" /></div>\n'
        '      </div>\n'
        '      <div class="mb-3"><label class="text-xs text-gray-400 block mb-1">Description</label>\n'
        '        <textarea id="ac-edit-desc" rows="2" class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg resize-y"></textarea></div>\n'
        '      <div class="mb-3"><label class="text-xs text-gray-400 block mb-1">Instructions</label>\n'
        '        <textarea id="ac-edit-instructions" rows="8" class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg resize-y font-mono"></textarea></div>\n'
        '      <div class="flex items-center gap-3">\n'
        '        <button onclick="acSaveEdit()" class="px-4 py-2 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold">Save</button>\n'
        '        <button onclick="acCloseEdit()" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-sm rounded-lg">Cancel</button>\n'
        '        <span id="ac-edit-status" class="text-xs"></span>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'

        # ── Factory Mode ─────────────────────────────────────────────────────
        '  <details id="ac-factory-details" style="margin-top:24px;border-top:1px solid var(--border);padding-top:20px">\n'
        '    <summary style="cursor:pointer;font-size:13px;font-weight:600;color:var(--accent);letter-spacing:.02em;user-select:none;list-style:none;display:flex;align-items:center;gap:8px">'
        '<span>&#x2604; Generate with Agent Factory</span>'
        '<span style="font-size:10px;font-weight:400;color:var(--text-muted)">(AI-powered from template)</span>'
        '</summary>\n'
        '    <div style="margin-top:16px">\n'

        '      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px">\n'
        '        <div>\n'
        '          <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Agent Type</label>\n'
        '          <select id="af-type" style="width:100%;padding:7px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:13px">\n'
        '            <option value="specialist">Specialist</option>\n'
        '            <option value="orchestrator">Orchestrator</option>\n'
        '            <option value="team-mode">Team Mode</option>\n'
        '          </select>\n'
        '        </div>\n'
        '        <div>\n'
        '          <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Model</label>\n'
        '          <select id="af-model" style="width:100%;padding:7px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:13px">\n'
        '            <option value="sonnet">Claude Sonnet</option>\n'
        '            <option value="haiku">Claude Haiku</option>\n'
        '            <option value="opus">Claude Opus</option>\n'
        '          </select>\n'
        '        </div>\n'
        '        <div>\n'
        '          <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Max Turns</label>\n'
        '          <input type="number" id="af-maxturns" value="30" min="1" max="200" style="width:100%;padding:7px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:13px">\n'
        '        </div>\n'
        '      </div>\n'

        '      <div style="margin-bottom:16px">\n'
        '        <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:8px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Base Templates <span style="color:var(--text-faint)">(from .claude/agents/templates/)</span></label>\n'
        '        <div id="af-templates" style="display:flex;flex-wrap:wrap;gap:8px;min-height:32px;padding:8px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius)">'
        '<span style="color:var(--text-faint);font-size:11px;font-family:var(--font-mono)">Loading templates…</span>'
        '</div>\n'
        '      </div>\n'

        '      <div style="margin-bottom:16px">\n'
        '        <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:8px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Research Sections <span style="color:var(--text-faint)">(WebFetch on generate)</span></label>\n'
        '        <div style="display:flex;flex-wrap:wrap;gap:8px">\n'
        '          <label class="af-check"><input type="checkbox" id="af-r-mitre" value="mitre"> MITRE ATT&amp;CK</label>\n'
        '          <label class="af-check"><input type="checkbox" id="af-r-cve" value="cve"> CVE Database</label>\n'
        '          <label class="af-check"><input type="checkbox" id="af-r-tools" value="tools"> Tool Docs</label>\n'
        '          <label class="af-check"><input type="checkbox" id="af-r-api" value="api"> API Reference</label>\n'
        '        </div>\n'
        '      </div>\n'

        '      <div style="margin-bottom:16px;display:flex;align-items:center;gap:24px">\n'
        '        <label class="af-check" style="font-size:13px">\n'
        '          <input type="checkbox" id="af-project-ctx"> Include project context (.claude/)</label>\n'
        '        <label class="af-check" style="font-size:13px">\n'
        '          <input type="checkbox" id="af-save-file" checked> Save to .claude/agents/</label>\n'
        '      </div>\n'

        '      <div style="margin-bottom:8px">\n'
        '        <label class="text-xs" style="color:var(--text-muted);display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:.08em;font-family:var(--font-mono)">Extra Instructions <span style="color:var(--text-faint)">(appended to factory prompt)</span></label>\n'
        '        <textarea id="af-extra" rows="3" placeholder="Focus on XYZ domain. Must include T1055 detection. Report format: ..." '
        'style="width:100%;padding:8px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px;font-family:var(--font-mono);resize:vertical"></textarea>\n'
        '      </div>\n'

        '      <div style="display:flex;align-items:center;gap:12px;margin-top:4px">\n'
        '        <button onclick="afGenerate()" class="btn btn-accent">&#x2604; Generate Agent</button>\n'
        '        <span id="af-status" style="font-size:11px;font-family:var(--font-mono);color:var(--text-muted)"></span>\n'
        '      </div>\n'

        '      <pre id="af-preview" style="display:none;margin-top:16px;padding:14px;background:var(--bg-deep);border:1px solid var(--border);border-radius:var(--radius);font-size:11px;font-family:var(--font-mono);color:var(--text-primary);white-space:pre-wrap;max-height:400px;overflow-y:auto"></pre>\n'
        '    </div>\n'
        '  </details>\n'

        "</div>\n"
    )


def _workflows() -> str:
    return (
        '<div id="tab-workflows" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-4">&#x1f504; Workflow Builder</h3>\n'
        '  <p class="text-xs text-gray-500 mb-4">Create multi-step agent pipelines. Steps run in dependency order; use <code>{{step_id}}</code> in prompts to reference prior results.</p>\n'

        # ── Create Workflow ───────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">New Workflow</h4>\n'
        '  <div class="mb-3">\n'
        '    <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Workflow Name</label>\n'
        '    <input id="wf-name" type="text" placeholder="my-investigation"\n'
        '      class="px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none" style="width:300px">\n'
        '  </div>\n'
        '  <div id="wf-steps" class="space-y-3 mb-3"></div>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <button onclick="wfAddStep()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">+ Add Step</button>\n'
        '    <button onclick="wfExecute()"\n'
        '      class="px-4 py-1.5 bg-green-700 hover:bg-green-600 text-sm rounded-lg font-semibold transition-colors">&#x25b6; Execute</button>\n'
        '    <button onclick="wfClear()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">Clear</button>\n'
        '    <span id="wf-status" class="text-xs"></span>\n'
        '  </div>\n'

        # ── Results ──────────────────────────────────────────────────────────
        '  <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">History</h4>\n'
        '  <div id="wf-history" class="space-y-4"></div>\n'
        "</div>\n"
    )



def _settings() -> str:
    # Scope badge helper
    def scope_badge(label: str, color: str) -> str:
        return (
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;'
            f'padding:2px 8px;border-radius:4px;'
            f'background:{color}1a;color:{color};border:1px solid {color}33">'
            f'{label}</span>'
        )

    global_badge = scope_badge("🌐 Global ~/.claude", "#38bdf8")
    project_badge = scope_badge("📁 Project .claude/", "#6366f1")

    return (
        '<div id="tab-settings" class="card" style="display:none">\n'
        '  <div class="panel-header">'
        '<div class="panel-accent-bar"></div>'
        '<span class="panel-title">&#x2699;&#xfe0f; Claude Settings</span>'
        '</div>\n'

        # ── Scope tabs ──
        '  <div style="display:flex;gap:8px;margin-bottom:24px;border-bottom:1px solid var(--border);padding-bottom:16px">\n'
        '    <button id="scope-btn-global" onclick="switchSettingsScope(\'global\')" '
        '      class="btn btn-accent" style="font-size:12px">🌐 Global ~/.claude</button>\n'
        '    <button id="scope-btn-project" onclick="switchSettingsScope(\'project\')" '
        '      class="btn btn-ghost" style="font-size:12px">📁 Project .claude/</button>\n'
        '  </div>\n'

        # ══ GLOBAL SCOPE PANE ══
        '  <div id="settings-scope-global">\n'
        f'    <div style="margin-bottom:20px">{global_badge}</div>\n'

        # Global MCPs
        '    <div class="mb-6">\n'
        '      <div class="section-h3">MCP Servers</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">'
        'MCP servers in ~/.claude/settings.json. Toggle to enable/disable globally.</p>\n'
        '      <div id="settings-global-mcps" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # MCP Installer
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Install New MCP Server</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">Add a new MCP server to ~/.claude/settings.json. Restart Claude Code to activate.</p>\n'
        '      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">\n'
        '        <div>\n'
        '          <label>Server Name</label>\n'
        '          <input type="text" id="mcp-install-name" placeholder="e.g. my-mcp-server" />\n'
        '        </div>\n'
        '        <div>\n'
        '          <label>Command</label>\n'
        '          <input type="text" id="mcp-install-cmd" placeholder="e.g. uvx, npx, node" />\n'
        '        </div>\n'
        '      </div>\n'
        '      <div style="margin-bottom:12px">\n'
        '        <label>Args (comma-separated)</label>\n'
        '        <input type="text" id="mcp-install-args" placeholder="e.g. @modelcontextprotocol/server-filesystem, /tmp" />\n'
        '      </div>\n'
        '      <div style="margin-bottom:12px">\n'
        '        <label>Env Vars (KEY=VALUE, one per line)</label>\n'
        '        <textarea id="mcp-install-env" rows="3" placeholder="API_KEY=xxx&#10;DEBUG=1"></textarea>\n'
        '      </div>\n'
        '      <div class="flex items-center gap-3">\n'
        '        <button onclick="installMcp()" class="btn btn-accent">+ Install MCP</button>\n'
        '        <span id="mcp-install-status" class="text-xs font-mono"></span>\n'
        '      </div>\n'
        '    </div>\n'

        # Global Plugins
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Plugins</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">'
        'Plugins installed in ~/.claude. Toggle writes to ~/.claude/settings.json.</p>\n'
        '      <div id="settings-plugins" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Global Env (read-only)
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Environment Variables <span style="font-weight:400;font-size:11px;color:var(--text-muted)">(read-only)</span></div>\n'
        '      <div id="settings-global-env" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Global summary (hooks, etc.)
        '    <div class="mb-4">\n'
        '      <div class="section-h3">Summary</div>\n'
        '      <div id="settings-global" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Hooks Manager
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Hooks Manager</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">Manage Claude Code hooks in ~/.claude/settings.json.</p>\n'
        '      <div id="settings-global-hooks" class="toggles-loading">Loading…</div>\n'
        '      <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">\n'
        '        <div class="section-h4">Add New Hook</div>\n'
        '        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">\n'
        '          <div>\n'
        '            <label>Event</label>\n'
        '            <select id="hook-add-event">\n'
        '              <option value="PreToolUse">PreToolUse</option>\n'
        '              <option value="PostToolUse">PostToolUse</option>\n'
        '              <option value="Stop">Stop</option>\n'
        '              <option value="SessionStart">SessionStart</option>\n'
        '              <option value="UserPromptSubmit">UserPromptSubmit</option>\n'
        '              <option value="SubagentStart">SubagentStart</option>\n'
        '              <option value="SubagentStop">SubagentStop</option>\n'
        '              <option value="TeammateIdle">TeammateIdle</option>\n'
        '              <option value="PreCompact">PreCompact</option>\n'
        '              <option value="PostCompact">PostCompact</option>\n'
        '              <option value="Notification">Notification</option>\n'
        '            </select>\n'
        '          </div>\n'
        '          <div>\n'
        '            <label>Matcher (regex, optional)</label>\n'
        '            <input type="text" id="hook-add-matcher" placeholder=".*" />\n'
        '          </div>\n'
        '        </div>\n'
        '        <div style="margin-bottom:12px">\n'
        '          <label>Command</label>\n'
        '          <input type="text" id="hook-add-cmd" placeholder="e.g. python3 /path/to/hook.py" />\n'
        '        </div>\n'
        '        <div class="flex items-center gap-3">\n'
        '          <button onclick="addHook()" class="btn btn-accent">+ Add Hook</button>\n'
        '          <span id="hook-add-status" class="text-xs font-mono"></span>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'

        '  </div>\n'

        # ══ PROJECT SCOPE PANE ══
        '  <div id="settings-scope-project" style="display:none">\n'
        f'    <div style="margin-bottom:20px">{project_badge}</div>\n'

        # Project Agent & Proxy settings
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Agent &amp; Proxy</div>\n'
        '      <div id="settings-agent-form" class="space-y-3"></div>\n'
        '      <div class="flex items-center gap-3 mt-3">\n'
        '        <button onclick="saveSettingsAgent()" class="btn btn-accent">Save</button>\n'
        '        <span id="settings-agent-status" class="text-xs font-mono"></span>\n'
        '      </div>\n'
        '    </div>\n'

        # Project MCPs
        '    <div class="mb-6">\n'
        '      <div class="section-h3">MCP Servers</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">'
        'MCP servers from project mcp.json. Toggle stores state in .claude/settings.json.</p>\n'
        '      <div id="settings-mcps" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Project Skill Domains
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Skill Domains</div>\n'
        '      <p class="text-xs font-mono mb-3" style="color:var(--text-muted)">'
        'Enable or disable skill domain libraries from .claude/skills/.</p>\n'
        '      <div id="settings-skills" class="toggle-grid toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Project Env (read-only)
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Environment Variables <span style="font-weight:400;font-size:11px;color:var(--text-muted)">(read-only)</span></div>\n'
        '      <div id="settings-project-env" class="toggles-loading">Loading…</div>\n'
        '    </div>\n'

        # Project Hooks (read-only)
        '    <div class="mb-4">\n'
        '      <div class="section-h4">Hooks <span style="font-weight:400;text-transform:none">(read-only)</span></div>\n'
        '      <div id="settings-hooks-table"></div>\n'
        '    </div>\n'

        # Project Env Editor
        '    <div class="mb-6">\n'
        '      <div class="section-h3">Custom Env Overrides</div>\n'
        '      <div id="settings-env-rows" class="space-y-2 mb-3"></div>\n'
        '      <div class="flex items-center gap-3">\n'
        '        <button onclick="settingsAddEnvRow()" class="btn btn-ghost">+ Add Variable</button>\n'
        '        <button onclick="saveSettingsEnv()" class="btn btn-accent">Save Env</button>\n'
        '        <span id="settings-env-status" class="text-xs font-mono"></span>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'

        "</div>\n"
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
        '    <h3 class="text-lg font-semibold">&#x1f50d; OpenSearch</h3>\n'
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


def all_panels() -> str:
    return "".join([
        _health(),
        _usage(),
        _telemetry(),
        _routing(),
        _crypto(),
        _agent_craft(),
        _team_builder(),
        _agent_query(),
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
        _settings(),
    ])
