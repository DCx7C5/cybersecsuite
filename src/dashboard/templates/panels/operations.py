"""Operations & Case Management panels."""
from .._components import (
    filter_bar,
    form_field,
    form_input,
    form_select,
    form_textarea,
    mini_card,
    mini_grid,
    modal_overlay,
    panel_toolbar,
    simple_panel,
    stat_card,
    stat_grid,
    table_slot,
    tab_panel,
)

_CANCEL_BTN = (
    '<button class="btn btn-sm" '
    'onclick="this.closest(\'[id$=-modal]\').style.display=\'none\'">Cancel</button>'
)


def _modal_footer(save_fn: str) -> str:
    return (
        '<div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">'
        + _CANCEL_BTN
        + f'<button class="btn btn-sm btn-accent" onclick="{save_fn}()">Save</button>'
        + '</div>'
    )


def _cases() -> str:
    counters = mini_grid(
        mini_card("cases-total", "Total Cases"),
        mini_card("cases-open", "Open", "text-green-400"),
        mini_card("cases-closed", "Closed"),
        cols=3,
    )
    modal = modal_overlay(
        "cases-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">Case Intake</h3>',
        form_field("Title", form_input("cm-title", placeholder="Short title")),
        form_field("Problem Statement", form_textarea("cm-problem", rows=3, placeholder="What happened?")),
        form_field("Attack Hypothesis", form_textarea("cm-hypothesis", rows=2, placeholder="Initial theory...")),
        form_field("Severity", form_select("cm-severity", [
            ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical"),
        ])),
        _modal_footer("caseSave"),
    )
    return tab_panel(
        "cases",
        "&#x1f4c2; Phase 0 Case Intake",
        panel_toolbar("Cases", '<button class="btn btn-sm btn-accent" onclick="caseCreate()">+ New</button>'),
        counters,
        filter_bar("cases-search", "Filter cases...", "filterCases()", "cases-count"),
        table_slot("cases-table", loading=True, loading_text="Loading cases..."),
        modal,
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
    modal = modal_overlay(
        "tasks-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">New Task</h3>',
        form_field("Session ID", form_input("tm-session", placeholder="optional")),
        form_field("State", form_select("tm-state", [
            ("submitted", "Submitted"), ("working", "Working"),
            ("completed", "Completed"), ("failed", "Failed"), ("cancelled", "Cancelled"),
        ])),
        _modal_footer("taskSave"),
    )
    return tab_panel(
        "tasks",
        "&#x23f1; Task Management",
        panel_toolbar("Tasks", '<button class="btn btn-sm btn-accent" onclick="taskCreate()">+ New</button>'),
        counters,
        filter_bar("tasks-search", "Filter tasks...", "filterTasks()", "tasks-count"),
        table_slot("tasks-table", loading=True, loading_text="Loading tasks..."),
        modal,
    )


def _pocs() -> str:
    modal = modal_overlay(
        "pocs-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">PoC Record</h3>',
        form_field("Title", form_input("pm-title", placeholder="CVE-XXXX-XXXXX PoC")),
        form_field("PoC URL", form_input("pm-url", placeholder="https://...")),
        form_field("Source", form_input("pm-source", placeholder="ExploitDB / GitHub / ...")),
        form_field("Language", form_input("pm-lang", placeholder="python / c / ...")),
        form_field("Severity", form_select("pm-severity", [
            ("", "Unknown"), ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical"),
        ])),
        form_field("Description", form_textarea("pm-desc", rows=2)),
        _modal_footer("pocSave"),
    )
    return tab_panel(
        "pocs",
        "&#x1f4a3; Proof-of-Concept Exploits",
        panel_toolbar("PoCs", '<button class="btn btn-sm btn-accent" onclick="pocCreate()">+ New</button>'),
        filter_bar("pocs-search", "Filter PoCs...", "filterPocs()", "pocs-count"),
        table_slot("pocs-table", loading=True, loading_text="Loading PoC data..."),
        modal,
    )


def _a2a() -> str:
    modal = modal_overlay(
        "a2a-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">A2A Task</h3>',
        form_field("Session ID", form_input("am-session", placeholder="optional")),
        form_field("State", form_select("am-state", [
            ("submitted", "Submitted"), ("working", "Working"),
            ("completed", "Completed"), ("failed", "Failed"), ("cancelled", "Cancelled"),
        ])),
        _modal_footer("a2aTaskSave"),
    )
    return tab_panel(
        "a2a",
        "&#x1f916; A2A Agent Tasks",
        panel_toolbar("A2A Tasks", '<button class="btn btn-sm btn-accent" onclick="a2aTaskCreate()">+ New</button>'),
        filter_bar("a2a-search", "Filter tasks...", "filterA2a()", "a2a-count"),
        table_slot("a2a-table", loading=True, loading_text="Loading A2A tasks..."),
        modal,
    )
