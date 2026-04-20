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
        '<div id="telemetry-content">Loading telemetry...</div>',
    )
