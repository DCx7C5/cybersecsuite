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
