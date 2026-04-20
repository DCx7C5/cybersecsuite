"""Forensics & Security panels."""
from .._components import (
    filter_bar,
    form_field,
    form_input,
    form_select,
    form_textarea,
    modal_overlay,
    panel_section,
    panel_toolbar,
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

_CANCEL_BTN = (
    '<button class="btn btn-sm" '
    'onclick="this.closest(\'[id$=-modal]\').style.display=\'none\'">Cancel</button>'
)


def _mf(save_fn: str) -> str:
    return (
        '<div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">'
        + _CANCEL_BTN
        + f'<button class="btn btn-sm btn-accent" onclick="{save_fn}()">Save</button>'
        + '</div>'
    )


def _investigations() -> str:
    modal = modal_overlay(
        "inv-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">New Investigation</h3>',
        form_field("Name", form_input("ivm-name", placeholder="Investigation name")),
        form_field("Description", form_textarea("ivm-desc", rows=2)),
        form_field("Agent", form_input("ivm-agent", value="cybersec-agent")),
        form_field("Mode", form_select("ivm-mode", [
            ("blue", "Blue"), ("red", "Red"), ("purple", "Purple"),
        ])),
        form_field("Phase", form_select("ivm-phase", [
            ("init", "Init"), ("recon", "Recon"), ("exploit", "Exploit"), ("post", "Post"),
        ])),
        _mf("invSave"),
    )
    return tab_panel(
        "investigations",
        "&#x1f50d; Investigations",
        panel_toolbar("Investigations", '<button class="btn btn-sm btn-accent" onclick="invCreate()">+ New</button>'),
        filter_bar("inv-search", "Filter...", "filterInv()", "inv-count"),
        table_slot("investigations-table", loading=True, loading_text="Loading investigations..."),
        modal,
    )


def _findings() -> str:
    modal = modal_overlay(
        "findings-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">Finding</h3>',
        form_field("Title", form_input("fm-title", placeholder="Finding title")),
        form_field("Severity", form_select("fm-severity", [
            ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical"),
        ])),
        form_field("Status", form_select("fm-status", [
            ("open", "Open"), ("confirmed", "Confirmed"),
            ("false_positive", "False Positive"), ("resolved", "Resolved"),
        ])),
        form_field("Confidence", form_select("fm-confidence", [
            ("low", "Low"), ("medium", "Medium"), ("high", "High"),
        ])),
        form_field("Location", form_input("fm-location", placeholder="/path/or/host")),
        form_field("Description", form_textarea("fm-desc", rows=3)),
        _mf("findingSave"),
    )
    return tab_panel(
        "findings",
        "&#x1f6a8; Security Findings",
        panel_toolbar("Findings", '<button class="btn btn-sm btn-accent" onclick="findingCreate()">+ New</button>'),
        stat_grid(
            stat_card("findings-total", "Total"),
            stat_card("findings-critical", "Critical"),
            stat_card("findings-high", "High"),
            stat_card("findings-24h", "Last 24h"),
        ),
        filter_bar("findings-search", "Filter findings...", "filterFindings()", "findings-count"),
        table_slot("findings-table"),
        findings_heatmap_section(),
        modal,
    )


def _iocs() -> str:
    modal = modal_overlay(
        "iocs-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">IOC</h3>',
        form_field("Type", form_select("iocm-type", [
            ("ip", "IP"), ("domain", "Domain"), ("hash", "Hash"),
            ("url", "URL"), ("email", "Email"), ("file", "File"),
            ("registry", "Registry"), ("other", "Other"),
        ])),
        form_field("Value", form_input("iocm-value", placeholder="1.2.3.4 / evil.com / sha256...")),
        form_field("Confidence", form_select("iocm-confidence", [
            ("low", "Low"), ("medium", "Medium"), ("high", "High"),
        ])),
        form_field("Source", form_input("iocm-source", placeholder="tool / feed / manual")),
        _mf("iocSave"),
    )
    return tab_panel(
        "iocs",
        "&#x1f4cc; Indicators of Compromise",
        panel_toolbar("IOCs", '<button class="btn btn-sm btn-accent" onclick="iocCreate()">+ New</button>'),
        stat_grid(
            stat_card("iocs-total", "Total IOCs"),
            stat_card("iocs-active", "Active"),
            stat_card("iocs-high-conf", "High Conf"),
            stat_card("iocs-types", "Types"),
        ),
        filter_bar("iocs-search", "Filter IOCs...", "filterIocs()", "iocs-count"),
        table_slot("iocs-table"),
        ioc_breakdown_section(),
        modal,
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


def _intel() -> str:
    source_modal = modal_overlay(
        "intel-src-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">Intel Feed Source</h3>',
        form_field("Name", form_input("ism-name", placeholder="Source name")),
        form_field("URL", form_input("ism-url", placeholder="https://feeds.example.com/rss")),
        form_field("Type", form_select("ism-type", [
            ("rss", "RSS"), ("atom", "Atom"), ("json", "JSON API"), ("html", "HTML Scrape"),
        ])),
        form_field("Description", form_input("ism-desc", placeholder="optional")),
        _mf("intelSourceSave"),
    )
    return tab_panel(
        "intel",
        "&#x1f4a1; Intelligence Feed",
        stat_grid(
            stat_card("intel-techniques", "MITRE Techniques"),
            stat_card("intel-cve", "CVEs"),
            stat_card("intel-cwe", "CWEs"),
            stat_card("intel-capec", "CAPECs"),
        ),
        panel_section(
            "Feed Sources",
            panel_toolbar(
                "Sources",
                '<button class="btn btn-sm btn-accent" onclick="intelSourceCreate()">+ Add</button>',
                '<button class="btn btn-sm" onclick="seedIntelSources()">Seed Defaults</button>',
            ),
            filter_bar("intel-src-search", "Filter sources...", "filterIntelSources()", "intel-src-count"),
            table_slot("intel-sources-table", loading=True, loading_text="Loading sources..."),
            source_modal,
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
