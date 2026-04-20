"""Tests for dashboard routing after mount at / instead of /dashboard."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from proxy.asgi import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestDashboardRootAccess:
    """Verify dashboard page is accessible at /."""

    def test_get_root_returns_dashboard_page(self, client: TestClient) -> None:
        """GET / should return the dashboard HTML page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "<html" in response.text or "<!doctype" in response.text.lower()

    def test_get_dashboard_redirects_to_root(self, client: TestClient) -> None:
        """GET /dashboard should 308-redirect to /."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/"

    def test_get_dashboard_slash_redirects_to_root(self, client: TestClient) -> None:
        """GET /dashboard/ should 308-redirect to /."""
        response = client.get("/dashboard/", follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/"


class TestDashboardAPIEndpoints:
    """Verify API endpoints are accessible at /api/* (not /dashboard/api/*)."""

    def test_get_api_overview(self, client: TestClient) -> None:
        """GET /api/overview should return JSON."""
        response = client.get("/api/overview")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_get_api_health(self, client: TestClient) -> None:
        """GET /api/health should return JSON health status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        data = response.json()
        # Health endpoint returns nested structure with database and proxy keys
        assert "database" in data or "proxy" in data

    def test_get_api_providers(self, client: TestClient) -> None:
        """GET /api/providers should return provider list."""
        response = client.get("/api/providers")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_get_api_usage(self, client: TestClient) -> None:
        """GET /api/usage should return usage stats."""
        response = client.get("/api/usage")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_get_api_crypto(self, client: TestClient) -> None:
        """GET /api/crypto should return crypto module status."""
        response = client.get("/api/crypto")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_get_api_a2a(self, client: TestClient) -> None:
        """GET /api/a2a should return A2A server status."""
        response = client.get("/api/a2a")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_get_api_db_counts(self, client: TestClient) -> None:
        """GET /api/db-counts should return database counts."""
        response = client.get("/api/db-counts")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")


class TestDashboardSSEEndpoints:
    """Verify SSE endpoints are accessible at /sse/* (not /dashboard/sse/*)."""

    def test_sse_health_streaming_status_ok(self, client: TestClient) -> None:
        """GET /sse/health should return 200 with stream headers."""
        response = client.get("/sse/health", follow_redirects=False)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_sse_cases_streaming_status_ok(self, client: TestClient) -> None:
        """GET /sse/cases should return 200 with stream headers."""
        response = client.get("/sse/cases", follow_redirects=False)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_sse_tasks_streaming_status_ok(self, client: TestClient) -> None:
        """GET /sse/tasks should return 200 with stream headers."""
        response = client.get("/sse/tasks", follow_redirects=False)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestRoutePrecedence:
    """Verify that root-mounted dashboard does not steal higher-priority routes."""

    def test_health_endpoint_is_not_captured(self, client: TestClient) -> None:
        """GET /health should be handled by ASGI health route, not dashboard."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        # Verify it's the top-level health endpoint, not dashboard 404
        data = response.json()
        assert isinstance(data, dict)

    def test_v1_proxy_routes_not_captured(self, client: TestClient) -> None:
        """GET /v1/models should be handled by AI proxy, not dashboard."""
        response = client.get("/v1/models")
        assert response.status_code == 200
        # Proxy returns JSON list or dict, not HTML
        assert response.headers["content-type"].startswith("application/json")

    def test_a2a_route_not_captured(self, client: TestClient) -> None:
        """POST /a2a with invalid JSON should fail at A2A layer, not dashboard."""
        response = client.post("/a2a", json={})
        # A2A server will validate the JSON-RPC envelope and reject; not 404
        assert response.status_code in (200, 400)  # Valid A2A response or RPC error

    def test_agent_card_route_not_captured(self, client: TestClient) -> None:
        """GET /.well-known/agent.json should be handled by A2A, not dashboard."""
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_static_assets_served(self, client: TestClient) -> None:
        """Static assets under /static/ should be served, not captured by dashboard."""
        # Try to access a CSS file; the endpoint exists even if empty
        response = client.get("/static/css/dashboard.css")
        # May be 200 or 404 depending on whether the file exists, but should not be HTML
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.headers.get("content-type") != "text/html"


class TestBackwardCompatibilityRedirects:
    """Verify legacy /dashboard routes redirect cleanly."""

    def test_dashboard_with_follow_redirects(self, client: TestClient) -> None:
        """Following redirect from /dashboard should land at /."""
        response = client.get("/dashboard", follow_redirects=True)
        assert response.status_code == 200
        # Should be serving dashboard HTML
        assert "<html" in response.text or "<!doctype" in response.text.lower()

    def test_dashboard_slash_with_follow_redirects(self, client: TestClient) -> None:
        """Following redirect from /dashboard/ should land at /."""
        response = client.get("/dashboard/", follow_redirects=True)
        assert response.status_code == 200
        # Should be serving dashboard HTML
        assert "<html" in response.text or "<!doctype" in response.text.lower()
