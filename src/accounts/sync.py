"""Sync ProviderConfig registry to database."""
import logging

from db.models import Provider, ProviderAuthMethod

logger = logging.getLogger(__name__)


def _val(x):
    return x.value if hasattr(x, "value") else str(x)


async def sync_providers_to_db() -> int:
    """Sync ProviderConfig registry to DB. Returns count of synced providers."""
    try:
        from ai_proxy.providers.registry import get_all_providers
    except ImportError:
        logger.warning("ai_proxy.providers.registry not available, skipping provider sync")
        return 0

    providers = get_all_providers()
    synced = 0

    for pid, cfg in providers.items():
        await Provider.update_or_create(
            id=pid,
            defaults={
                "name": cfg.name,
                "base_url": cfg.base_url,
                "auth_type": _val(cfg.auth_type),
                "auth_header": cfg.auth_header,
                "auth_prefix": cfg.auth_prefix,
                "api_format": _val(cfg.api_format),
                "env_key": cfg.env_key,
                "is_free": cfg.is_free,
                "enabled": cfg.enabled,
                "max_retries": cfg.max_retries,
                "timeout_seconds": cfg.timeout_seconds,
                "rate_limit_rpm": cfg.rate_limit_rpm,
                "rate_limit_tpm": cfg.rate_limit_tpm,
                "extra": cfg.extra,
            },
        )
        synced += 1
        if auths := cfg.extra.get("auth_methods"):
            p = await Provider.get(id=pid)
            for a in auths:
                await ProviderAuthMethod.get_or_create(provider=p, auth_method=a, defaults={"config": {}})

    logger.info(f"Synced {synced} providers to DB")
    return synced


async def sync_auth_methods(provider_id: str) -> None:
    """Sync auth methods for a specific provider."""
    try:
        from ai_proxy.providers.registry import get_provider
    except ImportError:
        return
    cfg = get_provider(provider_id)
    if not cfg:
        return
    p = await Provider.get_or_none(id=provider_id)
    if not p:
        return
    for a in cfg.extra.get("auth_methods", []):
        await ProviderAuthMethod.get_or_create(provider=p, auth_method=a, defaults={"config": {}})
