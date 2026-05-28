"""Ollama model lifecycle management — pull, list, delete, copy operations.

Provides async operations for managing local Ollama models with:
- Download/pull lifecycle event emissions
- Model list caching with TTL
- Typed failure handling for unavailable daemon/models
- Progress event payloads
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp

from css.core.cache.memory_cache import L1MemoryCache
from css.core.events.emitter import NamespacedEventEmitter
from css.core.logger import getLogger
from .types import OllamaModel, OllamaConfig


logger = getLogger(__name__)


class OllamaModelManagerError(Exception):
    """Base exception for OllamaModelManager."""

    pass


class OllamaDaemonUnavailableError(OllamaModelManagerError):
    """Ollama daemon is not reachable."""

    pass


class OllamaModelNotFoundError(OllamaModelManagerError):
    """Model not found locally."""

    pass


class OllamaModelPullError(OllamaModelManagerError):
    """Model pull/download failed."""

    pass


class OllamaModelManager:
    """Manager for local Ollama model lifecycle.

    Wraps Ollama API endpoints for model management with async support,
    event emissions, and caching.

    Usage:
        manager = OllamaModelManager(base_url="http://localhost:11434")
        models = await manager.list()
        await manager.pull("llama2", on_progress=lambda p: print(p))
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        config: OllamaConfig | None = None,
        cache_ttl_seconds: int = 3600,
    ):
        """Initialize OllamaModelManager.

        Args:
            base_url: Ollama server base URL
            config: Optional OllamaConfig for endpoint customization
            cache_ttl_seconds: Cache TTL for model list (default 1 hour)
        """
        self.base_url = base_url.rstrip("/")
        self.config = config or OllamaConfig()
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache = L1MemoryCache(namespace="ollama_models")
        self._session: aiohttp.ClientSession | None = None
        self._emitter = NamespacedEventEmitter("ollama.models")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session is initialized."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request_json(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to Ollama API and return JSON.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: Optional JSON payload

        Returns:
            Response dict

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
        """
        session = await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        try:
            async with session.request(
                method,
                url,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
            ) as resp:
                if resp.status >= 400:
                    error_text = await resp.text()
                    raise OllamaDaemonUnavailableError(
                        f"Ollama API error {resp.status}: {error_text}"
                    )
                return await resp.json()
        except aiohttp.ClientConnectorError as e:
            raise OllamaDaemonUnavailableError(
                f"Cannot reach Ollama at {self.base_url}: {e}"
            ) from e
        except asyncio.TimeoutError as e:
            raise OllamaDaemonUnavailableError(
                f"Ollama request timeout ({self.config.timeout_seconds}s): {e}"
            ) from e

    async def is_available(self) -> bool:
        """Check if Ollama daemon is available and responding.

        Returns:
            True if daemon is reachable and responding, False otherwise
        """
        try:
            session = await self._ensure_session()
            async with session.head(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                return resp.status < 400
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def list(self, use_cache: bool = True) -> list[OllamaModel]:
        """List available local Ollama models.

        Fetches from /api/tags endpoint with optional caching.
        Returns typed OllamaModel objects with metadata.

        Args:
            use_cache: If True, use cached results if available

        Returns:
            List of OllamaModel with metadata

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
        """
        cache_key = "models_list"

        if use_cache:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.debug("Using cached model list")
                return cached

        logger.debug("Fetching model list from Ollama")
        response = await self._request_json("GET", self.config.model_discovery_endpoint)

        models: list[OllamaModel] = []
        for model_data in response.get("models", []):
            try:
                model = OllamaModel(
                    name=model_data.get("name", "unknown").split(":")[0],
                    full_name=model_data.get("name", "unknown"),
                    size_gb=model_data.get("size", 0) / (1024**3),
                    parameters=model_data.get("details", {}).get("parameter_count", 0),
                    quantization=model_data.get("details", {}).get("quantization_level"),
                    description=None,
                    modified_at=datetime.fromisoformat(
                        model_data.get("modified_at", datetime.now(timezone.utc).isoformat())
                    ),
                )
                models.append(model)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse model metadata: {e}")
                continue

        await self._cache.set(cache_key, models, ttl_seconds=self.cache_ttl_seconds)
        await self._emitter.emit("list_complete", {"count": len(models)})

        return models

    async def pull(
        self,
        model_name: str,
        stream_progress: bool = True,
    ) -> OllamaModel:
        """Pull (download) a model from ollama.ai library.

        Calls /api/pull endpoint and emits progress events.
        Blocks until download complete.

        Args:
            model_name: Model name to pull (e.g., "llama2", "mistral")
            stream_progress: If True, emit progress events

        Returns:
            OllamaModel metadata after successful pull

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
            OllamaModelPullError: If pull fails
        """
        logger.info(f"Pulling model: {model_name}")
        await self._emitter.emit("pull_started", {"model": model_name})

        try:
            session = await self._ensure_session()
            url = f"{self.base_url}/api/pull"

            async with session.post(
                url,
                json={"name": model_name, "stream": stream_progress},
                timeout=aiohttp.ClientTimeout(total=None),  # No timeout for long pull
            ) as resp:
                if resp.status >= 400:
                    error_text = await resp.text()
                    raise OllamaDaemonUnavailableError(
                        f"Ollama pull error {resp.status}: {error_text}"
                    )

                digest: str | None = None
                if stream_progress:
                    async for line in resp.content:
                        try:
                            import json

                            progress_data = json.loads(line)
                            digest = progress_data.get("digest")
                            status = progress_data.get("status", "")

                            await self._emitter.emit(
                                "pull_progress",
                                {
                                    "model": model_name,
                                    "status": status,
                                    "digest": digest,
                                    "completed": progress_data.get("completed", 0),
                                    "total": progress_data.get("total", 0),
                                },
                            )
                        except (json.JSONDecodeError, ValueError):
                            continue
                else:
                    result = await resp.json()
                    digest = result.get("digest")

            await self._emitter.emit("pull_complete", {"model": model_name, "digest": digest})

            models = await self.list(use_cache=False)
            for model in models:
                if model_name in model.full_name:
                    return model

            raise OllamaModelPullError(f"Model {model_name} pull succeeded but not found in list")

        except OllamaDaemonUnavailableError:
            await self._emitter.emit("pull_failed", {"model": model_name, "reason": "daemon_unavailable"})
            raise
        except Exception as e:
            await self._emitter.emit("pull_failed", {"model": model_name, "reason": str(e)})
            raise OllamaModelPullError(f"Failed to pull {model_name}: {e}") from e

    async def delete(self, model_name: str) -> bool:
        """Delete a local model.

        Calls /api/delete endpoint to remove model from disk.

        Args:
            model_name: Model name to delete

        Returns:
            True if deletion successful

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
            OllamaModelNotFoundError: If model not found
        """
        logger.info(f"Deleting model: {model_name}")

        try:
            await self._request_json(
                "DELETE",
                "/api/delete",
                json_data={"name": model_name},
            )
            await self._emitter.emit("delete_complete", {"model": model_name})
            await self._cache.delete("models_list")
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                raise OllamaModelNotFoundError(f"Model {model_name} not found") from e
            raise

    async def copy(self, source_model: str, target_model: str) -> bool:
        """Copy a model to a new name.

        Calls /api/copy endpoint to duplicate model with new name.

        Args:
            source_model: Source model name
            target_model: Target model name

        Returns:
            True if copy successful

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
            OllamaModelNotFoundError: If source model not found
        """
        logger.info(f"Copying model: {source_model} -> {target_model}")

        try:
            await self._request_json(
                "POST",
                "/api/copy",
                json_data={"source": source_model, "destination": target_model},
            )
            await self._emitter.emit(
                "copy_complete",
                {"source": source_model, "target": target_model},
            )
            await self._cache.delete("models_list")
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                raise OllamaModelNotFoundError(f"Model {source_model} not found") from e
            raise

    async def show(self, model_name: str) -> dict[str, Any]:
        """Get detailed model information.

        Calls /api/show endpoint for model details, capabilities, metadata.

        Args:
            model_name: Model name to show

        Returns:
            Model metadata dict

        Raises:
            OllamaDaemonUnavailableError: If daemon unreachable
            OllamaModelNotFoundError: If model not found
        """
        try:
            return await self._request_json(
                "POST",
                "/api/show",
                json_data={"name": model_name},
            )
        except Exception as e:
            if "not found" in str(e).lower():
                raise OllamaModelNotFoundError(f"Model {model_name} not found") from e
            raise

    async def close(self) -> None:
        """Close the session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()

