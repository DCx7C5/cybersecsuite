"""Advanced Features panels (Chat, Workflows, etc)."""
from .._components import (
    simple_panel,
    tab_panel,
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
        '      <label class="text-xs uppercase tracking-wide block mb-1" style="color:var(--text-muted)">Agent</label>\n'
        '      <select id="chat-agent"\n'
        '        class="w-full px-3 py-2 text-sm rounded-lg outline-none"'
        ' style="background:var(--surface-2);border:1px solid var(--border);color:var(--text-primary)">\n'
        '        <option value="cybersec-agent">cybersec-agent</option>\n'
        '      </select>\n'
        '    </div>\n'
        '    <div>\n'
        '      <label class="text-xs uppercase tracking-wide block mb-1" style="color:var(--text-muted)">Model</label>\n'
        '      <select id="chat-model"\n'
        '        class="w-full px-3 py-2 text-sm rounded-lg outline-none"'
        ' style="background:var(--surface-2);border:1px solid var(--border);color:var(--text-primary)">\n'
        '        <option value="">Auto</option>\n'
        '      </select>\n'
        '    </div>\n'
        '    <div style="display:flex;align-items:flex-end;gap:8px">\n'
        '      <button class="btn btn-accent flex-1" onclick="acChatSend()">Send</button>\n'
        '      <button class="btn btn-ghost flex-1" onclick="acChatClear()">Clear</button>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div id="chat-messages" class="space-y-3 mb-3" style="height:400px;overflow-y:auto;border:1px solid var(--border);border-radius:8px;padding:12px"></div>\n'
        '  <textarea id="chat-input" placeholder="Message\u2026" class="w-full px-3 py-2 text-sm rounded-lg outline-none"'
        ' style="background:var(--surface-2);border:1px solid var(--border);color:var(--text-primary)" rows="3"></textarea>\n'
        '</div>\n'
    )


def _team_builder() -> str:
    return tab_panel(
        "team-builder",
        "&#x1f465; Team Builder",
        '<div id="team-builder-content" style="padding:16px;color:var(--text-muted)">Loading team builder...</div>',
    )


def _agent_crafter() -> str:
    return tab_panel(
        "agent-crafter",
        "&#x1f9d9; Agent Crafter",
        '<div id="agent-crafter-content" style="padding:16px;color:var(--text-muted)">Loading agent crafter...</div>',
    )


def _agent_factory() -> str:
    return tab_panel(
        "agent-factory",
        "&#x1f4ed; Agent Factory",
        '<div id="agent-factory-content" style="padding:16px;color:var(--text-muted)">Loading agent factory...</div>',
    )


def _workflows() -> str:
    return tab_panel(
        "workflows",
        "&#x1f501; Workflows",
        '<div id="workflows-content" style="padding:16px;color:var(--text-muted)">Loading workflows...</div>',
    )


def _flowgraph() -> str:
    return tab_panel(
        "flowgraph",
        "&#x2b61; Flowgraph",
        '<div id="flowgraph-container" style="display:flex;gap:16px;height:calc(100vh - 200px)">'
        '<div id="flowgraph-palette" style="width:180px;border:1px solid var(--border);border-radius:6px;padding:8px;overflow-y:auto">'
        '<div style="font-size:11px;color:var(--text-muted);margin-bottom:8px">Drag agents to canvas</div>'
        '<div id="fg-agent-list" style="display:flex;flex-direction:column;gap:4px"></div>'
        '</div>'
        '<div id="drawflow" style="flex:1;border:1px solid var(--border);border-radius:6px;background:var(--surface-2);position:relative;overflow:hidden"></div>'
        '</div>'
        '<div id="flowgraph-log" class="space-y-2" style="margin-top:16px;max-height:120px;overflow-y:auto;border:1px solid var(--border);padding:8px;border-radius:6px;font-family:var(--font-mono);font-size:10px"></div>'
        '<style>'
        '#drawflow { background-image: '
        'linear-gradient(0deg, transparent 23px, var(--border) 24px), '
        'linear-gradient(90deg, transparent 23px, var(--border) 24px); '
        'background-size: 24px 24px; }'
        '.drawflow-node { background: var(--surface); border: 1px solid var(--accent); }'
        '.drawflow-node.selected { background: var(--accent-glow); border-color: var(--accent); }'
        '</style>',
    )


def _sdk_lab() -> str:
    """TypeScript SDK Lab panel — streaming, tools, structured, thinking, memory."""
    _S = 'background:var(--surface-2);border:1px solid var(--border);color:var(--text-primary)'
    _PRE = f'style="{_S};border-radius:8px;padding:12px;min-height:100px;font-size:11px;white-space:pre-wrap;overflow-y:auto;max-height:260px"'
    _AREA = f'class="w-full px-3 py-2 text-sm rounded-lg outline-none" style="{_S}"'
    _INP = f'class="w-full px-3 py-2 text-sm rounded-lg outline-none mb-2" style="{_S}"'
    _LBL = 'class="text-xs uppercase tracking-wide block mb-1" style="color:var(--text-muted)"'
    _ST = 'style="font-size:11px;min-height:1.2em;margin-top:4px" '
    return (
        '<div id="tab-sdk-lab" class="card" style="display:none">\n'
        f'  <div class="flex items-center justify-between mb-3">\n'
        f'    <h3 class="text-lg font-semibold">&#x2297; SDK Lab</h3>\n'
        f'    <span id="sdk-api-health" {_ST}style="color:var(--text-muted);font-size:11px;cursor:pointer" onclick="sdkApiHealth()">TS API (click to check)</span>\n'
        f'  </div>\n'
        # Sub-tab nav
        f'  <div id="sdk-sub-tabs" class="flex gap-2 mb-4 flex-wrap">\n'
        f'    <button class="btn btn-accent text-xs" onclick="sdkSubTab(\'stream\')">Stream</button>\n'
        f'    <button class="btn btn-ghost text-xs" onclick="sdkSubTab(\'tools\')">Tools</button>\n'
        f'    <button class="btn btn-ghost text-xs" onclick="sdkSubTab(\'structured\')">Structured</button>\n'
        f'    <button class="btn btn-ghost text-xs" onclick="sdkSubTab(\'thinking\')">Thinking</button>\n'
        f'    <button class="btn btn-ghost text-xs" onclick="sdkSubTab(\'memory\')">Memory</button>\n'
        f'  </div>\n'
        # Stream
        f'  <div id="sdk-sub-stream" class="sdk-sub">\n'
        f'    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        f'      <div class="md:col-span-2"><label {_LBL}>Prompt</label>\n'
        f'        <textarea id="sdk-stream-input" rows="3" {_AREA} placeholder="Streaming prompt…">Explain XSS attacks in 3 sentences.</textarea></div>\n'
        f'      <div><label {_LBL}>Actions</label>\n'
        f'        <button class="btn btn-accent w-full text-xs mb-2" onclick="sdkStreamRun()">&#x25B6; Stream</button>\n'
        f'        <div id="sdk-stream-status" {_ST}style="color:var(--text-muted)"></div></div>\n'
        f'    </div>\n'
        f'    <pre id="sdk-stream-output" {_PRE}></pre>\n'
        f'  </div>\n'
        # Tools
        f'  <div id="sdk-sub-tools" class="sdk-sub" style="display:none">\n'
        f'    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        f'      <div class="md:col-span-2"><label {_LBL}>Prompt</label>\n'
        f'        <textarea id="sdk-tools-input" rows="3" {_AREA} placeholder="Tool use prompt…">Search for recent CVEs in OpenSSL.</textarea></div>\n'
        f'      <div><label {_LBL}>Actions</label>\n'
        f'        <button class="btn btn-accent w-full text-xs mb-2" onclick="sdkToolsRun()">&#x25B6; Run Tools</button>\n'
        f'        <div id="sdk-tools-status" {_ST}style="color:var(--text-muted)"></div></div>\n'
        f'    </div>\n'
        f'    <label {_LBL}>Tools JSON (optional override)</label>\n'
        f'    <textarea id="sdk-tools-config" rows="2" {_AREA} placeholder="[]"></textarea>\n'
        f'    <pre id="sdk-tools-output" {_PRE} style="margin-top:8px"></pre>\n'
        f'  </div>\n'
        # Structured
        f'  <div id="sdk-sub-structured" class="sdk-sub" style="display:none">\n'
        f'    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        f'      <div class="md:col-span-2"><label {_LBL}>Text to parse</label>\n'
        f'        <textarea id="sdk-struct-input" rows="3" {_AREA} placeholder="Text to extract IOCs from…">The malware connected to 192.168.1.1 and dropped evil.exe, also visited https://malware.example.com.</textarea></div>\n'
        f'      <div><label {_LBL}>Schema</label>\n'
        f'        <select id="sdk-struct-schema" {_INP}>\n'
        f'          <option value="ioc_extraction">IOC Extraction</option>\n'
        f'          <option value="finding_classification">Finding Classification</option>\n'
        f'          <option value="threat_actor">Threat Actor</option>\n'
        f'          <option value="cve_context">CVE Context</option>\n'
        f'          <option value="generic_json">Generic JSON</option>\n'
        f'        </select>\n'
        f'        <button class="btn btn-accent w-full text-xs mb-2" onclick="sdkStructuredRun()">&#x25B6; Extract</button>\n'
        f'        <div id="sdk-struct-status" {_ST}style="color:var(--text-muted)"></div></div>\n'
        f'    </div>\n'
        f'    <pre id="sdk-struct-output" {_PRE}></pre>\n'
        f'  </div>\n'
        # Thinking
        f'  <div id="sdk-sub-thinking" class="sdk-sub" style="display:none">\n'
        f'    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        f'      <div class="md:col-span-2"><label {_LBL}>Complex prompt</label>\n'
        f'        <textarea id="sdk-think-input" rows="3" {_AREA} placeholder="Complex reasoning prompt…">Analyse the attack chain: initial access via spear-phishing, lateral movement using PsExec, ransomware deployment. What TTPs?</textarea></div>\n'
        f'      <div><label {_LBL}>Budget tokens</label>\n'
        f'        <input id="sdk-think-budget" type="number" value="8000" min="1024" max="32000" step="1024" {_INP} />\n'
        f'        <button class="btn btn-accent w-full text-xs mb-2" onclick="sdkThinkingRun()">&#x25B6; Think</button>\n'
        f'        <div id="sdk-think-status" {_ST}style="color:var(--text-muted)"></div></div>\n'
        f'    </div>\n'
        f'    <label {_LBL}>Thinking</label>\n'
        f'    <pre id="sdk-think-thinking" {_PRE} style="opacity:0.6;max-height:120px"></pre>\n'
        f'    <label {_LBL} style="margin-top:8px">Answer</label>\n'
        f'    <pre id="sdk-think-answer" {_PRE} style="margin-top:4px"></pre>\n'
        f'  </div>\n'
        # Memory
        f'  <div id="sdk-sub-memory" class="sdk-sub" style="display:none">\n'
        f'    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">\n'
        f'      <div class="md:col-span-2"><label {_LBL}>Prompt (memory-aware)</label>\n'
        f'        <textarea id="sdk-mem-input" rows="3" {_AREA} placeholder="Memory-aware prompt…">Remember that APT29 uses Cobalt Strike. Then tell me what you know about APT29.</textarea></div>\n'
        f'      <div style="display:flex;flex-direction:column;gap:8px">\n'
        f'        <button class="btn btn-accent text-xs" onclick="sdkMemoryRun()">&#x25B6; Run + Store</button>\n'
        f'        <button class="btn btn-ghost text-xs" onclick="sdkMemoryRead()">&#x1f4c4; Read Memories</button>\n'
        f'        <div id="sdk-mem-status" {_ST}style="color:var(--text-muted)"></div></div>\n'
        f'    </div>\n'
        f'    <pre id="sdk-mem-output" {_PRE}></pre>\n'
        f'    <label {_LBL} style="margin-top:8px">Memory store content</label>\n'
        f'    <pre id="sdk-mem-content" {_PRE} style="margin-top:4px;opacity:0.8"></pre>\n'
        f'  </div>\n'
        f'</div>\n'
    )


