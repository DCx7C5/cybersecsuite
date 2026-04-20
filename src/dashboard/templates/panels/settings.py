"""Settings & Configuration panels."""
from .._components import (
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
