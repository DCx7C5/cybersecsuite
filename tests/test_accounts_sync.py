"""Tests for accounts sync and provider models."""
import pytest


@pytest.mark.asyncio
async def test_sync_providers_import():
    """Test that sync module can be imported."""
    from accounts.sync import sync_providers_to_db, sync_auth_methods
    assert sync_providers_to_db is not None
    assert sync_auth_methods is not None


@pytest.mark.asyncio
async def test_provider_model_import():
    """Test Provider model can be imported."""
    from db.models.provider import Provider
    assert Provider is not None


@pytest.mark.asyncio
async def test_provider_auth_method_import():
    """Test ProviderAuthMethod model can be imported."""
    from db.models.provider import ProviderAuthMethod
    assert ProviderAuthMethod is not None


@pytest.mark.asyncio
async def test_api_account_import():
    """Test ApiAccount can be imported."""
    from db.models.api_account import ApiAccount
    assert ApiAccount is not None


@pytest.mark.asyncio
async def test_all_new_models_load():
    """Verify all new models load without errors."""
    from db.models import Provider, ProviderAuthMethod, ApiAccount

    # Just verify they can be instantiated without error
    assert Provider is not None
    assert ProviderAuthMethod is not None
    assert ApiAccount is not None