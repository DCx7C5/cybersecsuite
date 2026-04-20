"""Platform & System panels."""
from .._components import (
    panel_section,
    simple_panel,
    stat_card,
    stat_grid,
    table_slot,
    tab_panel,
)
from ..panel_helpers import (
    health_latency_section,
    health_service_cards,
    health_stat_row,
    usage_chart_section,
)


def _providers() -> str:
    return tab_panel(
        "providers",
        "&#x1f310; Provider Registry",
        '<div id="providers-table"><div class="loading" style="color:var(--text-muted)">Loading providers...</div></div>',
        hidden=False,
    )


def _usage() -> str:
    return tab_panel(
        "usage",
        "&#x1f4c8; Recent Requests",
        table_slot("usage-table", loading=True, loading_text="Loading usage..."),
        usage_chart_section(),
    )


def _health() -> str:
    return (
        '<div id="tab-health" class="card" style="display:none">\n'
        '  <h2>&#x2764; System Health</h2>\n'
        '  <div id="health-error" class="health-error-banner"></div>\n'
        + health_service_cards()
        + health_stat_row()
        + '  <div id="health-content"></div>\n'
        + health_latency_section()
        + '\n</div>\n'
    )


def _telemetry() -> str:
    return tab_panel(
        "telemetry",
        "&#x1f4ca; Telemetry",
        stat_grid(
            stat_card("telemetry-calls", "API Calls"),
            stat_card("telemetry-errors", "Errors"),
            stat_card("telemetry-latency", "p95 Latency"),
            stat_card("telemetry-providers", "Providers"),
        ),
        '<div id="telemetry-content"></div>',
    )


def _providers_hub() -> str:
    return (
        '<div id="tab-providers-hub" class="card panel-enter" style="display:none">\n'
        '  <div class="panel-header">\n'
        '    <h2>&#x229e; Provider Hub</h2>\n'
        '    <div>\n'
        '      <input id="ph-search" type="text" placeholder="Search providers..." class="form-input" style="width:200px"'
        ' oninput="phFilterProviders(this.value)">\n'
        '      <span id="ph-stats" style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted); margin-left:12px"></span>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div id="ph-list">\n'
        '    <div style="color:var(--text-muted); font-size:13px">Loading providers...</div>\n'
        '  </div>\n'
        '  <div id="ph-modal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0;'
        ' background:rgba(0,0,0,0.6); z-index:1000; align-items:center; justify-content:center;">\n'
        '    <div class="card" style="width:420px; position:relative">\n'
        '      <button onclick="phCloseModal()" style="position:absolute;top:12px;right:12px;background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:16px">&#x2715;</button>\n'
        '      <h3 id="ph-modal-title" style="margin-bottom:16px; font-size:14px; color:var(--accent)">Add Account</h3>\n'
        '      <input type="hidden" id="ph-modal-provider">\n'
        '      <div id="ph-modal-body"></div>\n'
        '      <div id="ph-modal-status" class="status-line" style="margin-top:8px; min-height:20px; font-size:12px; font-family:var(--font-mono)"></div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
    )
