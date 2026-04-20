"""Reusable panel section helpers for dashboard tabs."""
from ._components import panel_section


def usage_chart_section() -> str:
    """Provider breakdown charts (usage tab)."""
    return panel_section(
        "Provider breakdown",
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;height:220px">'
        '<canvas id="chart-provider-share"></canvas>'
        '<canvas id="chart-token-trend"></canvas>'
        '</div>',
    )


def health_service_cards() -> str:
    """Health service status cards."""
    return (
        '<div class="health-services">\n'
        '  <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-db-dot"></span>'
        '<span class="svc-name">Database</span>'
        '<span class="svc-detail" id="health-db-detail">—</span></div>\n'
        '  <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-redis-dot"></span>'
        '<span class="svc-name">Redis</span>'
        '<span class="svc-detail" id="health-redis-detail">—</span></div>\n'
        '  <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-oo-dot"></span>'
        '<span class="svc-name">OpenObserve</span>'
        '<span class="svc-detail" id="health-oo-detail">—</span></div>\n'
        '  <div class="health-svc">'
        '<span class="svc-indicator unknown" id="health-proxy-dot"></span>'
        '<span class="svc-name">AI Proxy</span>'
        '<span class="svc-detail" id="health-proxy-detail">—</span></div>\n'
        '</div>\n'
    )


def health_stat_row() -> str:
    """Health statistics row."""
    return (
        '<div class="stat-row">\n'
        '  <div class="stat-box"><span id="health-tables">—</span><br><small>Tables</small></div>\n'
        '  <div class="stat-box"><span id="health-providers">—</span><br><small>Providers On</small></div>\n'
        '  <div class="stat-box"><span id="health-providers-free">—</span><br><small>Free</small></div>\n'
        '  <div class="stat-box"><span id="health-uptime">—</span><br><small>Uptime</small></div>\n'
        '  <div class="stat-box"><span id="health-intel">—</span><br><small>Intel</small></div>\n'
        '  <div class="stat-box"><span id="health-local-llm">—</span><br><small>Local LLM</small></div>\n'
        '</div>\n'
    )


def health_latency_section() -> str:
    """Request latency chart section (health tab)."""
    return panel_section(
        "Request latency",
        '<div style="height:200px"><canvas id="chart-latency-pct"></canvas></div>',
        desc="p50 / p95 / p99 latency in milliseconds (sampled from telemetry ring buffer).",
    )


def findings_heatmap_section() -> str:
    """Severity heatmap section (findings tab)."""
    return panel_section(
        "Severity heatmap",
        '<div id="chart-findings-heatmap" style="height:220px"></div>',
        desc="Findings by severity and date. Darker = more findings.",
    )


def ioc_breakdown_section() -> str:
    """IOC breakdown charts section (iocs tab)."""
    return panel_section(
        "IOC breakdown",
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">'
        '<div style="height:200px"><canvas id="chart-ioc-types"></canvas></div>'
        '<div id="chart-ioc-timeline" style="height:200px"></div>'
        '</div>',
        desc="IOC type distribution (left) and scatter timeline by type (right).",
    )


def compliance_heatmap_section() -> str:
    """MITRE technique frequency heatmap section (compliance tab)."""
    return panel_section(
        "MITRE technique frequency",
        '<div id="chart-mitre-heatmap" style="height:340px"></div>',
        desc="Technique IDs detected across all findings. Darker = more hits.",
    )
