"""template_engine — Jinja2 parametric template engine with 4-scope context.

Public API::

    from template_engine import render, render_string, get_context, resolve_template

    # Render a named template (searched session→project→app→global)
    output = render("reports/investigation-report.md", {"case_id": "CS-001"})

    # Render an inline string
    output = render_string("Case: {{ case_id }}", {"case_id": "CS-001"})

    # Get merged context for all 4 scopes
    ctx = get_context(session_id="apt29-hunt")

    # Find template path (highest-priority scope wins)
    path = resolve_template("artifact.md")
"""
from __future__ import annotations

from template_engine.context import get_context
from template_engine.discovery import list_templates, resolve_template
from template_engine.renderer import build_environment, render, render_string

__all__ = [
    "render",
    "render_string",
    "get_context",
    "resolve_template",
    "list_templates",
    "build_environment",
]
