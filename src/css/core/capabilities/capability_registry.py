"""Dynamic Capability Registry — loads provider capabilities at startup with caching."""

from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from css.core.types.base_enums import CapabilityType
from css.core.types.base_enums import MemorySupportMode

from css.core.logger import getLogger


@runtime_checkable
class _ProviderRegistryProto(Protocol):
    def list_providers(self) -> list[str]: ...
    def get_provider(self, name: str) -> Any: ...

logger = getLogger(__name__)


class DynamicCapabilityRegistry:
    """
    Dynamic capability discovery and caching system.

    Discovers capabilities from all providers at startup:
    1. Hardcoded defaults (fast)
    2. Environment variables (override)
    3. YAML config (persistent)
    4. Provider /models endpoints (authoritative)

    Caches results for 24 hours to avoid repeated discovery calls.
    Falls back gracefully if any discovery step fails.

    Example:
        registry = DynamicCapabilityRegistry()
        await registry.discover()  # Called at startup

        capabilities = registry.get_capabilities('openai', 'gpt-4')
        is_streaming = registry.has_capability('openai', 'gpt-4', CapabilityType.STREAMING)
    """

    # Cache TTL in hours
    CACHE_TTL_HOURS = 24

    # Hardcoded capability defaults (fast-path, no I/O)
    DEFAULT_CAPABILITIES = {
        "openai": {
            "gpt-4": [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.JSON_MODE,
                CapabilityType.LONG_CONTEXT,
            ],
            "gpt-3.5-turbo": [
                CapabilityType.STREAMING,
                CapabilityType.TOOL_USE,
            ],
        },
        "anthropic": {
            "claude-3-sonnet": [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.LONG_CONTEXT,
            ],
            "claude-3-opus": [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.LONG_CONTEXT,
            ],
        },
    }

    DEFAULT_MEMORY_SUPPORT: dict[str, MemorySupportMode] = {
        "anthropic": MemorySupportMode.NATIVE_TOOL,
        "openai": MemorySupportMode.PLATFORM_EMULATED,
        "gemini": MemorySupportMode.PLATFORM_EMULATED,
        "deepseek": MemorySupportMode.PLATFORM_EMULATED,
        "groq": MemorySupportMode.PLATFORM_EMULATED,
        "mistral": MemorySupportMode.PLATFORM_EMULATED,
        "xai": MemorySupportMode.PLATFORM_EMULATED,
        "openrouter": MemorySupportMode.PLATFORM_EMULATED,
        "ollama": MemorySupportMode.PLATFORM_EMULATED,
    }

    def __init__(self) -> None:
        """Initialize capability registry with empty cache."""
        self._capabilities: dict[str, dict[str, set[CapabilityType]]] = {}
        self._last_discovery: datetime | None = None
        self._discovery_in_progress = False

    async def discover(self) -> None:
        """
        Discover capabilities from all providers.

        Called at application startup. Runs discovery sequence:
        1. Load hardcoded defaults
        2. Override with env vars
        3. Override with YAML config
        4. Query provider /models endpoints (if available)

        Caches results for 24h TTL. Subsequent calls within TTL skip discovery.
        Falls back gracefully if any step fails (no exception raised).

        Example:
            registry = DynamicCapabilityRegistry()
            await registry.discover()  # Runs full discovery
            await registry.discover()  # Skips if cache still valid
        """
        # Skip if already discovering or cache is still valid
        if self._discovery_in_progress:
            return

        if not self.needs_discovery():
            logger.debug("Capability cache still valid, skipping discovery")
            return

        self._discovery_in_progress = True

        try:
            # Run discovery sequence
            await self._load_defaults()
            await self._load_env_overrides()
            await self._load_yaml_config()
            # Note: _query_provider_endpoints requires provider registry, skip for now

            self._last_discovery = datetime.now()
            logger.info(
                f"Capability discovery completed, cached {len(self._capabilities)} providers"
            )
        except Exception as e:
            logger.error(f"Capability discovery failed: {e}")
        finally:
            self._discovery_in_progress = False

    def get_capabilities(
        self,
        provider_name: str,
        model_id: str,
    ) -> list[CapabilityType]:
        """
        Get capabilities for a specific model.

        Args:
            provider_name: Provider name (e.g., 'openai', 'anthropic')
            model_id: Model ID (e.g., 'gpt-4', 'claude-3-sonnet')

        Returns:
            List of CapabilityType enums supported by model
            Empty list if model not found or discovery failed
        """
        provider_caps = self._capabilities.get(provider_name, {})
        model_caps = provider_caps.get(model_id, set())
        return list(model_caps)

    def has_capability(
        self,
        provider_name: str,
        model_id: str,
        capability: CapabilityType,
    ) -> bool:
        """
        Check if model supports a specific capability.

        Args:
            provider_name: Provider name
            model_id: Model ID
            capability: CapabilityType to check

        Returns:
            True if capability is supported, False otherwise
        """
        provider_caps = self._capabilities.get(provider_name, {})
        model_caps = provider_caps.get(model_id, set())
        return capability in model_caps

    def is_cache_stale(self) -> bool:
        """
        Check if cache has expired (>24h since last discovery).

        Returns:
            True if cache is stale, False if still valid
        """
        if self._last_discovery is None:
            return True

        ttl_seconds = self.CACHE_TTL_HOURS * 3600
        elapsed = (datetime.now() - self._last_discovery).total_seconds()
        return elapsed > ttl_seconds

    def needs_discovery(self) -> bool:
        """
        Check if discovery needs to run.

        Returns:
            True if discovery not run yet or cache is stale
        """
        return self._last_discovery is None or self.is_cache_stale()

    def clear_cache(self) -> None:
        """Clear all cached capabilities and reset discovery timestamp."""
        self._capabilities.clear()
        self._last_discovery = None
        logger.info("Cleared capability cache")

    def get_memory_support_mode(self, provider_name: str) -> MemorySupportMode:
        """Get memory support mode for provider."""
        return self.DEFAULT_MEMORY_SUPPORT.get(
            provider_name.lower(),
            MemorySupportMode.PLATFORM_EMULATED,
        )

    def has_native_memory_support(self, provider_name: str) -> bool:
        """Check whether provider has native memory support."""
        return self.get_memory_support_mode(provider_name) in {
            MemorySupportMode.NATIVE_TOOL,
            MemorySupportMode.NATIVE_MANAGED,
        }

    async def _load_defaults(self) -> None:
        """
        Load hardcoded capability defaults.

        Fast path, no I/O. Called first in discovery sequence.
        """
        for provider, models in self.DEFAULT_CAPABILITIES.items():
            if provider not in self._capabilities:
                self._capabilities[provider] = {}

            for model_id, capabilities in models.items():
                self._capabilities[provider][model_id] = set(capabilities)

        logger.debug(f"Loaded hardcoded defaults for {len(self.DEFAULT_CAPABILITIES)} providers")

    async def _load_env_overrides(self) -> None:
        """
        Load capability overrides from environment variables.

        Example format:
            CAPABILITY_OPENAI_GPT4=streaming,vision,tool_use
        """
        import os

        for key, value in os.environ.items():
            if not key.startswith("CAPABILITY_"):
                continue

            # Parse key: CAPABILITY_PROVIDER_MODEL
            parts = key.split("_")[1:]
            if len(parts) < 2:
                continue

            provider = parts[0].lower()
            model = "_".join(parts[1:]).lower()

            # Parse capabilities
            cap_strs = value.split(",")
            capabilities: list[CapabilityType] = []

            for cap_str in cap_strs:
                cap_str = cap_str.strip().upper()
                try:
                    capabilities.append(CapabilityType[cap_str])
                except KeyError:
                    logger.warning(f"Unknown capability: {cap_str}")

            if provider not in self._capabilities:
                self._capabilities[provider] = {}

            self._capabilities[provider][model] = set(capabilities)

        logger.debug("Loaded environment variable overrides")

    async def _load_yaml_config(self) -> None:
        """
        Load capabilities from YAML configuration file.

        File path from CAPABILITY_CONFIG_PATH env var, default config/capabilities.yaml.
        Format:
            providers:
              <name>:
                models:
                  <model_id>: {capabilities: [streaming, vision]}

        Silently no-ops if the file does not exist. Overrides env-loaded defaults
        for any provider/model that appears in the YAML.
        """
        import os

        path_str = os.environ.get("CAPABILITY_CONFIG_PATH", "config/capabilities.yaml")
        config_path = Path(path_str)
        if not config_path.is_file():
            logger.debug("No capability config file at %s, skipping YAML load", config_path)
            return

        try:
            import yaml

            raw = config_path.read_text(encoding="utf-8")
            data: dict[str, Any] = yaml.safe_load(raw) or {}
            providers_data = data.get("providers", {})
            count = 0
            for provider_name, provider_cfg in providers_data.items():
                provider = provider_name.lower()
                if provider not in self._capabilities:
                    self._capabilities[provider] = {}
                models_data = provider_cfg.get("models", {})
                for model_id, model_cfg in models_data.items():
                    raw_caps = model_cfg.get("capabilities", [])
                    parsed: set[CapabilityType] = set()
                    for c in raw_caps:
                        try:
                            parsed.add(CapabilityType(c.upper()))
                        except (ValueError, AttributeError):
                            logger.warning("Unknown capability '%s' for %s/%s", c, provider, model_id)
                    self._capabilities[provider][model_id] = parsed
                    count += 1
            logger.debug("Loaded %d model capabilities from %s", count, config_path)
        except Exception:
            logger.warning("Failed to load capabilities from %s", config_path, exc_info=True)

    async def _query_provider_endpoints(
        self,
        provider_registry: _ProviderRegistryProto,
    ) -> None:
        """
        Query provider /models endpoints for authoritative capability data.

        Iterates over providers registered in provider_registry and attempts
        to fetch model lists from their /models endpoints. Falls back silently
        on any per-provider failure.

        Args:
            provider_registry: ProviderRegistry-like instance with list_providers() and get_provider()
        """
        if not isinstance(provider_registry, _ProviderRegistryProto):
            logger.debug("provider_registry does not conform to protocol, skipping endpoint query")
            return

        providers = provider_registry.list_providers()
        for provider_name in providers:
            try:
                adapter = provider_registry.get_provider(provider_name)
            except Exception:
                continue

            get_models: Callable[[], Awaitable[list[Any]]] | None = getattr(
                adapter, "list_models", None
            )
            if get_models is None:
                continue

            try:
                models = await get_models()
            except Exception:
                logger.debug("Failed to query models for %s, skipping", provider_name)
                continue

            provider = provider_name.lower()
            if provider not in self._capabilities:
                self._capabilities[provider] = {}
            for model_entry in models:
                model_id: str | None = None
                capabilities_raw: list[str] | None = None
                if isinstance(model_entry, str):
                    model_id = model_entry
                elif isinstance(model_entry, dict):
                    model_id = model_entry.get("id") or model_entry.get("model_id")
                    capabilities_raw = model_entry.get("capabilities") or model_entry.get("capabilities_raw")

                if not model_id:
                    continue

                if model_id not in self._capabilities[provider]:
                    self._capabilities[provider][model_id] = set()

                if capabilities_raw:
                    for c in capabilities_raw:
                        try:
                            self._capabilities[provider][model_id].add(CapabilityType(c.upper()))
                        except (ValueError, AttributeError):
                            pass

            logger.debug(
                "Queried %d models from %s", len(self._capabilities.get(provider, {})), provider_name
            )
