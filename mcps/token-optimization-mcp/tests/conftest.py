"""Shared fixtures for token-optimization-mcp tests."""
import pytest
import main


@pytest.fixture(autouse=True)
def reset_main_state():
    """Reset all module-level mutable state before/after every test."""
    main._mem.clear()
    main._rate_store.clear()
    main._session_savings.clear()
    yield
    main._mem.clear()
    main._rate_store.clear()
    main._session_savings.clear()
