"""Data & Management panels."""
from .._components import (
    simple_panel,
    tab_panel,
    stat_card,
    stat_grid,
    table_slot,
)


def _dbcounts() -> str:
    return simple_panel("dbcounts", "&#x1f4ca; Database Table Counts", "db-content", "Loading DB counts...")


def _opensearch() -> str:
    return (
        '<div id="tab-opensearch" class="card" style="display:none">\n'
        '  <h3 style="font-size:1rem;font-weight:600;margin-bottom:14px">&#x1f50d; OpenObserve</h3>\n'
        '  <div id="os-cluster" style="margin-bottom:10px;color:var(--text-muted);font-size:13px"></div>\n'
        '  <div id="os-indices"></div>\n'
        '</div>\n'
    )


def _explorer() -> str:
    _inp = 'style="padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px"'
    return (
        '<div id="tab-explorer" class="card" style="display:none">\n'
        '  <h3 style="font-size:1rem;font-weight:600;margin-bottom:14px">&#x1f5a5; Data Explorer</h3>\n'
        '  <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">\n'
        '    <select id="explorer-model" onchange="loadExplorerTable()" ' + _inp + ' style="width:260px;padding:6px 10px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:12px">'
        '<option value="">Select model…</option></select>\n'
        '    <span id="explorer-count" style="font-size:12px;color:var(--text-muted)"></span>\n'
        '  </div>\n'
        '  <div id="explorer-table"></div>\n'
        '</div>\n'
    )


def _templates() -> str:
    return tab_panel(
        "templates",
        "&#x1f4c4; Templates & Workflows",
        stat_grid(
            stat_card("templates-total", "Templates"),
            stat_card("templates-workflows", "Workflows"),
            stat_card("templates-playbooks", "Playbooks"),
            cols=3,
        ),
        table_slot("templates-table"),
    )
