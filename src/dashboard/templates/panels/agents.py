"""AI & Agent panels."""
from .._components import (
    action_bar,
    btn,
    form_field,
    form_input,
    form_select,
    form_textarea,
    grid,
    panel_section,
    simple_panel,
    status_span,
    table_slot,
    tab_panel,
)


def _agents() -> str:
    return simple_panel("agents", "&#x1f916; Agent Registry", "agents-content", "Loading agents...")


def _routing() -> str:
    return simple_panel("routing", "&#x1f500; Routing Engine", "routing-content", "Loading routing...")


def _factory() -> str:
    return simple_panel("factory", "&#x1f3ed; Agent Factory", "factory-content", "Loading factory...")


def _prompts() -> str:
    return simple_panel("prompts", "&#x1f4dd; Prompts &amp; Templates", "prompts-content", "Loading prompts...")


def _agent_query() -> str:
    return tab_panel(
        "agent-query",
        "&#x1f916; Interactive Agent Query",
        panel_section(
            "Filters",
            grid(
                form_field("Search",
                    form_input("aq-agent-search", placeholder="Filter agents...",
                               oninput="_aqApplyAgentFilters()")),
                form_field("Source",
                    form_select("aq-source", [("", "All sources")],
                                onchange="_aqApplyAgentFilters()")),
                form_field("Role",
                    form_select("aq-role", [("", "All roles")],
                                onchange="_aqApplyAgentFilters()")),
                form_field("Model",
                    form_select("aq-model", [("", "All models")],
                                onchange="_aqApplyAgentFilters()")),
                cols=4,
            ),
        ),
        panel_section(
            "Query setup",
            grid(
                form_field("Agent",
                    form_select("aq-agent", [("cybersec-agent", "cybersec-agent")])),
                form_field("Context table",
                    form_select("aq-context-table", [("", "None")])),
                form_field("Row IDs",
                    form_input("aq-row-ids", placeholder="e.g. 1,2,3"),
                    hint="comma-separated"),
                cols=3,
            ),
            '<p id="aq-agent-help" style="font-size:12px;color:var(--text-muted);'
            'font-family:var(--font-mono);margin-top:8px">Loading agent options...</p>',
        ),
        panel_section(
            "Prompt",
            form_field(
                "Prompt",
                form_textarea(
                    "aq-prompt",
                    rows=4,
                    placeholder="Ask the agent anything\u2026",
                    mono=True,
                    onkeydown="if(event.ctrlKey&&event.key==='Enter'){event.preventDefault();runAgentQuery();}",
                ),
                hint="Ctrl+Enter to send",
            ),
            action_bar(
                btn("&#x25b6; Run Query", onclick="runAgentQuery()", cls="btn btn-accent"),
                btn("Clear History", onclick="clearAgentHistory()", cls="btn btn-ghost"),
                status_span("aq-status"),
            ),
            '<div id="aq-history" class="space-y-4" style="margin-top:16px"></div>',
        ),
    )
