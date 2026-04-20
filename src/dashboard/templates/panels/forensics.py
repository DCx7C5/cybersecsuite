"""Forensics & Security panels."""
from .._components import (
    panel_section,
    simple_panel,
    stat_card,
    stat_grid,
    table_slot,
    tab_panel,
)
from ..panel_helpers import (
    compliance_heatmap_section,
    findings_heatmap_section,
    ioc_breakdown_section,
)


def _investigations() -> str:
    return simple_panel(
        "investigations", "&#x1f50d; Investigations", "inv-content", "Loading investigation stats..."
    )


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
        findings_heatmap_section(),
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
        ioc_breakdown_section(),
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
        table_slot("network-table"),
    )


def _intel() -> str:
    return tab_panel(
        "intel",
        "&#x1f4a1; Intelligence Feed",
        stat_grid(
            stat_card("intel-techniques", "MITRE Techniques"),
            stat_card("intel-cve", "CVEs"),
            stat_card("intel-cwe", "CWEs"),
            stat_card("intel-capec", "CAPECs"),
        ),
        '<section class="text-xs uppercase tracking-wide mb-3" style="color:var(--text-muted)">Recent MITRE Techniques</section>',
        table_slot("intel-mitre-table"),
        '<section class="text-xs uppercase tracking-wide mb-3" style="color:var(--text-muted)">Recent CVEs</section>',
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
        compliance_heatmap_section(),
    )
