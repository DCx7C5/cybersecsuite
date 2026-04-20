"""Tests for template registry API wiring and index builder."""

from __future__ import annotations

from dashboard.api.template_registry import build_template_index
from dashboard.routes import create_dashboard_router


def test_build_template_index_has_expected_top_level_keys() -> None:
    index = build_template_index()
    assert set(index.keys()) == {"agents", "skills", "hooks", "mcp", "other"}


def test_dashboard_routes_include_template_registry_endpoint() -> None:
    router = create_dashboard_router()

    for route in router.routes:
        route_path = getattr(route, "path", None)
        route_methods = getattr(route, "methods", None) or set()
        if route_path == "/api/templates" and "GET" in route_methods:
            return

    raise AssertionError("Missing GET /api/templates route")
