"""
Conftest — pytest fixtures shared across all tests.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch
from importlib.metadata import EntryPoint

import pytest
import pytest_asyncio

# Ensure src/ is on the path so both `css.*` and `legacy.*` imports resolve
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# ---------------------------------------------------------------------------
# Entry points isolation (Phase 6 P4 test fixture)
# ---------------------------------------------------------------------------

def mock_entry_points(group=None):
    """Mock entry_points to return only safe/available modules for testing.
    
    This prevents ModuleNotFoundError during test collection by filtering out
    modules that require external dependencies or are only partially implemented.
    """
    # Only return modules with verified endpoints.py (actual HTTP routes)
    modules_eps = [
        EntryPoint(name="tags", value="css.modules.tags.endpoints", group="css.modules"),
        EntryPoint(name="tasks", value="css.modules.tasks.endpoints", group="css.modules"),
        EntryPoint(name="teams", value="css.modules.teams.endpoints", group="css.modules"),
        EntryPoint(name="tools", value="css.modules.tools.endpoints", group="css.modules"),
    ]
    
    # Only return api_services that have __init__.py (safe to import)
    services_eps = [
        EntryPoint(name="anthropic", value="css.api_services.anthropic", group="css.api_services"),
        EntryPoint(name="openai", value="css.api_services.openai", group="css.api_services"),
        EntryPoint(name="gemini", value="css.api_services.gemini", group="css.api_services"),
        EntryPoint(name="cohere", value="css.api_services.cohere", group="css.api_services"),
        EntryPoint(name="mistral", value="css.api_services.mistral", group="css.api_services"),
        EntryPoint(name="groq", value="css.api_services.groq", group="css.api_services"),
    ]
    
    if group == "css.modules":
        return modules_eps
    elif group == "css.api_services":
        return services_eps
    elif group is None:
        # Return all
        return modules_eps + services_eps
    else:
        return []


@pytest.fixture(scope="session", autouse=True)
def mock_entry_points_session():
    """Auto-use fixture to mock entry_points for entire test session.
    
    This is applied before any test collection, preventing ModuleNotFoundError
    from trying to import unavailable modules during pytest startup.
    """
    with patch("importlib.metadata.entry_points", side_effect=mock_entry_points):
        yield


# ---------------------------------------------------------------------------
# Event loop
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create and provide event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CYBERSEC_DB_HOST", "localhost")
    monkeypatch.setenv("CYBERSEC_DB_PORT", "5432")
    monkeypatch.setenv("CYBERSEC_DB_USER", "test_user")
    monkeypatch.setenv("CYBERSEC_DB_PASSWORD", "test_pass")
    monkeypatch.setenv("CYBERSEC_DB_NAME", "test_cybersec")


# ---------------------------------------------------------------------------
# Temp directories
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary config directory."""
    config = tmp_path / "config"
    config.mkdir()
    return config


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary data directory."""
    data = tmp_path / "data"
    data.mkdir()
    return data


# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root():
    """Provide project root path."""
    return PROJECT_ROOT


# ---------------------------------------------------------------------------
# Database fixtures removed — tests run only after phase complete
# Docker infra (postgres) required for integration tests
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Domain fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_project(db):
    """Provide a test project."""
    from css.core.db.models.scope import ProjectScope
    project = await ProjectScope.create(
        name="test-project",
        description="Test project for Phase 5C",
    )
    return project


@pytest_asyncio.fixture
async def test_session(db):
    """Provide a test session."""
    from css.core.db.models.scope import SessionScope
    session = await SessionScope.create(
        session_id="test-session-001",
        name="Test Session",
    )
    return session


# ---------------------------------------------------------------------------
# Pytest configuration
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers."""
    markers = [
        "asyncio: mark test as async",
        "integration: mark test as integration test",
        "slow: mark test as slow",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
