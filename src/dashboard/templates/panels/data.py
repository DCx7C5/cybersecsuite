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
    return simple_panel("opensearch", "&#x1f50d; OpenObserve", "opensearch-content", "Loading logs...")


def _explorer() -> str:
    return tab_panel(
        "explorer",
        "&#x1f5a5; Data Explorer",
        '<div id="explorer-content" style="padding: 16px; color: var(--text-muted);">Loading explorer...</div>',
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
