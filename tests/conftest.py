"""
Conftest — pytest fixtures shared across all tests.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path FIRST — before any imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest



@pytest.fixture(scope="session")
def event_loop():
    """Create and provide event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def project_root():
    """Provide project root path."""
    return PROJECT_ROOT


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CYBERSEC_DB_HOST", "localhost")
    monkeypatch.setenv("CYBERSEC_DB_PORT", "5432")
    monkeypatch.setenv("CYBERSEC_DB_USER", "test_user")
    monkeypatch.setenv("CYBERSEC_DB_PASSWORD", "test_pass")
    monkeypatch.setenv("CYBERSEC_DB_NAME", "test_cybersec")
    return os.environ


@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")

