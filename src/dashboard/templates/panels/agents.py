"""AI & Agent panels."""
from .._components import (
    action_bar,
    btn,
    filter_bar,
    form_field,
    form_input,
    form_select,
    form_textarea,
    grid,
    modal_overlay,
    panel_section,
    panel_toolbar,
    simple_panel,
    status_span,
    table_slot,
    tab_panel,
)


def _agents() -> str:
    return simple_panel("agents", "&#x1f916; Agent Registry", "agents-content", "Loading agents...")


def _routing() -> str:
    return tab_panel(
        "routing",
        "&#x1f500; Routing Engine",
        panel_section(
            "Strategy",
            grid(
                form_field("Strategy", form_select("route-strategy", [
                    ("auto", "Auto"), ("cost", "Cost"), ("quality", "Quality"),
                    ("speed", "Speed"), ("balanced", "Balanced"),
                    ("round_robin", "Round Robin"), ("fallback", "Fallback"),
                ], onchange="routingSetStrategy()")),
                form_field("Resilience Profile", form_select("route-resilience", [
                    ("standard", "Standard"), ("aggressive", "Aggressive"), ("passive", "Passive"),
                ], onchange="routingSetResilience()")),
                cols=2,
            ),
        ),
        panel_section(
            "Simulate Route",
            grid(
                form_field("Prompt", form_input("route-sim-prompt", placeholder="Enter a test prompt...")),
                form_field("Task Type", form_select("route-sim-task", [
                    ("general", "General"), ("code", "Code"),
                    ("analysis", "Analysis"), ("forensic", "Forensic"),
                ])),
                cols=2,
            ),
            '<button class="btn btn-sm btn-accent" onclick="routingSimulate()">Simulate</button>',
            '<pre id="route-sim-result" style="display:none;margin-top:8px;padding:10px;'
            'background:var(--bg-deep);border:1px solid var(--border);border-radius:var(--radius);'
            'font-size:11px;font-family:var(--font-mono);white-space:pre-wrap;'
            'max-height:200px;overflow-y:auto"></pre>',
        ),
        panel_section("Circuit Breakers",
            table_slot("routing-cb-table", loading=True, loading_text="Loading circuit breakers...")),
        panel_section("Budget Guard",
            '<div id="routing-budgets" style="font-size:12px;font-family:var(--font-mono);'
            'color:var(--text-muted)">Loading...</div>'),
    )


def _factory() -> str:
    return simple_panel("factory", "&#x1f3ed; Agent Factory", "factory-content", "Loading factory...")


def _prompts() -> str:
    modal = modal_overlay(
        "prompts-modal",
        '<h3 style="margin-bottom:16px;font-size:15px;font-weight:600">Prompt</h3>',
        form_field("Name", form_input("prm-name", placeholder="unique-prompt-name")),
        form_field("Category", form_select("prm-category", [
            ("general", "General"), ("forensic", "Forensic"), ("recon", "Recon"),
            ("analysis", "Analysis"), ("report", "Report"),
        ])),
        form_field("Content", form_textarea("prm-content", rows=6, placeholder="Prompt text...")),
        '<div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">'
        '<button class="btn btn-sm" onclick="document.getElementById(\'prompts-modal\').style.display=\'none\'">Cancel</button>'
        '<button class="btn btn-sm btn-accent" onclick="promptSave()">Save</button>'
        '</div>',
    )
    return tab_panel(
        "prompts",
        "&#x1f4dd; Prompts",
        panel_toolbar("Prompts", '<button class="btn btn-sm btn-accent" onclick="promptCreate()">+ New</button>'),
        filter_bar("prompts-search", "Filter prompts...", "filterPrompts()", "prompts-count"),
        table_slot("prompts-table", loading=True, loading_text="Loading prompts..."),
        modal,
    )


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
