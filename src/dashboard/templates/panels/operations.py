"""Operations & Case Management panels."""
from .._components import (
    mini_card,
    mini_grid,
    simple_panel,
    stat_card,
    stat_grid,
    table_slot,
    tab_panel,
)


def _cases() -> str:
    counters = mini_grid(
        mini_card("cases-total", "Total Cases"),
        mini_card("cases-open", "Open", "text-green-400"),
        mini_card("cases-closed", "Closed"),
        cols=3,
    )
    return tab_panel(
        "cases",
        "&#x1f4c2; Phase 0 Case Intake",
        counters,
        table_slot("cases-table", loading=True, loading_text="Loading cases..."),
    )


def _tasks() -> str:
    counters = mini_grid(
        mini_card("tasks-total", "Total"),
        mini_card("tasks-submitted", "Submitted", "text-blue-400"),
        mini_card("tasks-working", "Working", "text-yellow-400"),
        mini_card("tasks-completed", "Done", "text-green-400"),
        mini_card("tasks-failed", "Failed", "text-red-400"),
        cols=5,
    )
    return tab_panel(
        "tasks",
        "&#x23f1; Task Management",
        counters,
        table_slot("tasks-table", loading=True, loading_text="Loading tasks..."),
    )


def _pocs() -> str:
    return simple_panel("pocs", "&#x1f4a3; Proof-of-Concept Exploits", "pocs-content", "Loading PoC data...")


def _a2a() -> str:
    return simple_panel("a2a", "&#x1f916; A2A Agent Tasks", "a2a-content", "Loading A2A stats...")
