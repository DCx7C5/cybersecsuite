"""Dynamic Capability Registry — loads provider capabilities at startup with caching."""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging

from css.core.types.capabilities import CapabilityType

logger = logging.getLogger(__name__)


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
        'openai': {
            'gpt-4': [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.JSON_MODE,
                CapabilityType.LONG_CONTEXT,
            ],
            'gpt-3.5-turbo': [
                CapabilityType.STREAMING,
                CapabilityType.TOOL_USE,
            ],
        },
        'anthropic': {
            'claude-3-sonnet': [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.LONG_CONTEXT,
            ],
            'claude-3-opus': [
                CapabilityType.STREAMING,
                CapabilityType.VISION,
                CapabilityType.TOOL_USE,
                CapabilityType.LONG_CONTEXT,
            ],
        },
    }
    
    def __init__(self):
        """Initialize capability registry with empty cache."""
        self._capabilities: Dict[str, Dict[str, Set[CapabilityType]]] = {}
        self._last_discovery: Optional[datetime] = None
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
            
            self._last_discovery = datetime.utcnow()
            logger.info(f"Capability discovery completed, cached {len(self._capabilities)} providers")
        except Exception as e:
            logger.error(f"Capability discovery failed: {e}")
        finally:
            self._discovery_in_progress = False
    
    def get_capabilities(
        self,
        provider_name: str,
        model_id: str,
    ) -> List[CapabilityType]:
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
        elapsed = (datetime.utcnow() - self._last_discovery).total_seconds()
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
            if not key.startswith('CAPABILITY_'):
                continue
            
            # Parse key: CAPABILITY_PROVIDER_MODEL
            parts = key.split('_')[1:]
            if len(parts) < 2:
                continue
            
            provider = parts[0].lower()
            model = '_'.join(parts[1:]).lower()
            
            # Parse capabilities
            cap_strs = value.split(',')
            capabilities = []
            
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
        
        File path: config/capabilities.yaml (or env var CAPABILITY_CONFIG_PATH)
        """
        # TODO: Implement YAML loading when config system is ready
        logger.debug("YAML config loading not yet implemented")
    
    async def _query_provider_endpoints(self, provider_registry) -> None:
        """
        Query provider /models endpoints for authoritative capability data.
        
        Called for each available provider. Requires provider registry instance.
        Falls back silently if provider endpoints unavailable.
        
        Args:
            provider_registry: ProviderRegistry instance for loading providers
        """
        # TODO: Implement provider endpoint querying
        logger.debug("Provider endpoint querying not yet implemented")

