"""Settings & Configuration panels."""
from .._components import (
    panel_section,
    simple_panel,
    tab_panel,
)


def _settings() -> str:
    return tab_panel(
        "settings",
        "&#x1f4c4; Claude SDK Settings",
        '<div id="settings-content" style="padding:16px;color:var(--text-muted)">Loading settings...</div>',
    )


def _settings_cybersecsuite() -> str:
    return tab_panel(
        "settings-cybersecsuite",
        "&#x1f6e0; CyberSecSuite Settings",
        '<div id="settings-cs-content" style="padding:16px;color:var(--text-muted)">Loading CyberSecSuite settings...</div>',
    )


def _crypto() -> str:
    return simple_panel("crypto", "&#x1f512; Artifact Signing", "crypto-content", "Loading crypto stats...")


def _vault_widget() -> str:
    return tab_panel(
        "vault",
        "&#x1f9e0; Memory Vault",
        panel_section(
            "Vault status",
            '<div id="vault-status-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">'
            '<div class="stat-box"><span id="vault-mem-total">—</span><br><small>Memories</small></div>'
            '<div class="stat-box"><span id="vault-wiki-total">—</span><br><small>Wiki files</small></div>'
            '<div class="stat-box"><span id="vault-canvas-total">—</span><br><small>Canvases</small></div>'
            '</div>'
            '<div id="vault-hot-info" style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono)">—</div>',
            desc="Vault root: <code id='vault-path'>—</code>",
        ),
        panel_section(
            "Memory by type",
            '<div id="vault-type-table" style="font-size:12px;font-family:var(--font-mono)">Loading...</div>',
        ),
        panel_section(
            "Canvases",
            '<div id="vault-canvas-list" style="font-size:12px;font-family:var(--font-mono)">Loading...</div>',
        ),
        panel_section(
            "Recent memories",
            '<div id="vault-recent-list" style="font-size:12px;font-family:var(--font-mono)">Loading...</div>',
        ),
        panel_section(
            "Memory-enhanced chat",
            '<p style="font-size:12px;color:var(--text-muted);margin-bottom:8px">'
            'Send a message that Claude will remember in your vault. '
            'Uses <code>memory_20250818</code> beta + <code>BetaAsyncObsidianMemoryTool</code>.</p>'
            '<textarea id="vault-chat-prompt" rows="3" style="width:100%;background:var(--surface-2);'
            'color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:8px;'
            'font-family:var(--font-mono);font-size:12px;resize:vertical" '
            'placeholder="Ask Claude something to remember…"></textarea>'
            '<div style="margin-top:8px;display:flex;gap:8px;align-items:center">'
            '<button class="btn btn-primary" onclick="vaultChatSend()">&#x1f4ac; Send</button>'
            '<input id="vault-chat-model" type="text" value="claude-opus-4-5" '
            'style="background:var(--surface-2);color:var(--text-primary);border:1px solid var(--border);'
            'border-radius:4px;padding:4px 8px;font-size:12px;width:200px" placeholder="model">'
            '<span id="vault-chat-spinner" style="display:none;color:var(--text-muted);font-size:11px">Thinking...</span>'
            '</div>'
            '<div id="vault-chat-result" style="margin-top:10px;padding:10px;background:var(--surface-2);'
            'border:1px solid var(--border);border-radius:4px;font-size:12px;color:var(--text-primary);'
            'font-family:var(--font-mono);white-space:pre-wrap;display:none"></div>',
        ),
    )

