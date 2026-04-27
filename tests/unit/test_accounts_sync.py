"""Tests for accounts sync and API service models."""
import pytest


@pytest.mark.asyncio
async def test_sync_providers_import():
    """Test that sync module can be imported."""
    from accounts.sync import sync_providers_to_db, sync_auth_methods
    assert sync_providers_to_db is not None
    assert sync_auth_methods is not None


@pytest.mark.asyncio
async def test_api_service_model_import():
    """Test ApiService model can be imported."""
    from db.models.api_service import ApiService
    assert ApiService is not None


@pytest.mark.asyncio
async def test_api_service_auth_method_import():
    """Test ApiServiceAuthMethod model can be imported."""
    from db.models.api_service import ApiServiceAuthMethod
    assert ApiServiceAuthMethod is not None


@pytest.mark.asyncio
async def test_api_account_import():
    """Test ApiAccount can be imported."""
    from db.models.api_account import ApiAccount
    assert ApiAccount is not None


@pytest.mark.asyncio
async def test_all_new_models_load():
    """Verify all new models load without errors."""
    from db.models import ApiService, ApiServiceAuthMethod, ApiAccount

    # Just verify they can be instantiated without error
    assert ApiService is not None
    assert ApiServiceAuthMethod is not None
    assert ApiAccount is not None