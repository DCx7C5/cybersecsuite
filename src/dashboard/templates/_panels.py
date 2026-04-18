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
        '  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">\n'
        "    <div>\n"
        '      <label class="text-xs text-gray-400 uppercase tracking-wide block mb-1">Agent</label>\n'
        '      <select id="aq-agent"\n'
        '        class="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none">\n'
        '        <option value="cybersec">cybersec (orchestrator)</option>\n'
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
        '  <div id="tb-phases" class="space-y-2 mb-3"></div>\n'
        '  <div class="flex items-center gap-3 mb-4">\n'
        '    <button onclick="tbAddPhase()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">+ Add Phase</button>\n'
        '    <button onclick="tbGenerateTeam()"\n'
        '      class="px-4 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors">Generate JSON</button>\n'
        '    <button onclick="tbCopyTeam()"\n'
        '      class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">Copy</button>\n'
        '  </div>\n'
        '  <pre id="tb-team-json" class="bg-gray-900 border border-gray-700 rounded-lg p-4 text-xs font-mono text-gray-300 whitespace-pre-wrap" style="display:none;max-height:300px;overflow-y:auto"></pre>\n'
        "</div>\n"
    )


def _settings() -> str:
    return (
        '<div id="tab-settings" class="card" style="display:none">\n'
        '  <h3 class="text-lg font-semibold mb-4">&#x2699;&#xfe0f; Settings</h3>\n'

        # Agent & Proxy section
        '  <div class="mb-6">\n'
        '    <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Agent &amp; Proxy</h4>\n'
        '    <div id="settings-agent-form" class="space-y-3"></div>\n'
        '    <div class="flex items-center gap-3 mt-3">\n'
        '      <button onclick="saveSettingsAgent()"\n'
        '        class="px-4 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors">Save</button>\n'
        '      <span id="settings-agent-status" class="text-xs"></span>\n'
        '    </div>\n'
        '  </div>\n'

        # Env Variables section
        '  <div class="mb-6">\n'
        '    <h4 class="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-3">Environment Variables</h4>\n'
        '    <div id="settings-env-rows" class="space-y-2 mb-3"></div>\n'
        '    <div class="flex items-center gap-3">\n'
        '      <button onclick="settingsAddEnvRow()"\n'
        '        class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-xs rounded-lg transition-colors">+ Add Variable</button>\n'
        '      <button onclick="saveSettingsEnv()"\n'
        '        class="px-4 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-sm rounded-lg font-semibold transition-colors">Save</button>\n'
        '      <span id="settings-env-status" class="text-xs"></span>\n'
        '    </div>\n'
        '  </div>\n'

        # Hooks section (read-only)
        '  <div class="mb-4">\n'
        '    <h4 class="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Hooks <span class="text-gray-600 normal-case font-normal">(read-only)</span></h4>\n'
        '    <div id="settings-hooks-table"></div>\n'
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
        _providers(),
        _usage(),
        _health(),
        _agents(),
        _routing(),
        _factory(),
        _prompts(),
        _crypto(),
        _a2a(),
        _investigations(),
        _dbcounts(),
        _cases(),
        _tasks(),
        _pocs(),
        _findings(),
        _iocs(),
        _yara(),
        _network(),
        _intel(),
        _audit(),
        _compliance(),
        _agent_query(),
        _settings(),
        _team_builder(),
        _telemetry(),
        _explorer(),
    ])
