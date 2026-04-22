"""
Ollama & Local Provider Health Check.

Provides health verification for local LLM providers (Ollama, LM Studio),
GPU detection, and daemon status verification.

Supported endpoints:
- http://localhost:11434/api/tags (Ollama)
- http://localhost:1234/v1/models (LM Studio)

GPU Detection:
- NVIDIA: nvidia-smi
- AMD: rocm-smi
- Apple: system_profiler
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import httpx

logger = logging.getLogger("ai_proxy.health")


class GPUProvider(str, Enum):
    """Detected GPU provider."""
    NVIDIA = "nvidia"
    AMD = "amd"
    APPLE = "apple"
    INTEL = "intel"
    NONE = "none"


@dataclass
class GPUInfo:
    """GPU detection result."""
    provider: GPUProvider
    available: bool
    count: int = 0
    memory_gb: float = 0.0
    model: str = ""
    detected_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "provider": self.provider.value,
            "available": self.available,
            "count": self.count,
            "memory_gb": self.memory_gb,
            "model": self.model,
            "detected_at": self.detected_at,
        }


@dataclass
class OllamaHealth:
    """Ollama health check result."""
    healthy: bool
    base_url: str
    status_code: int = 0
    response_time_ms: float = 0.0
    models: list[str] = None
    error: str = ""
    gpu_info: Optional[GPUInfo] = None
    checked_at: float = 0.0

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.models is None:
            self.models = []
        if self.checked_at == 0.0:
            self.checked_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "healthy": self.healthy,
            "base_url": self.base_url,
            "status_code": self.status_code,
            "response_time_ms": round(self.response_time_ms, 2),
            "models": self.models,
            "error": self.error,
            "gpu_info": self.gpu_info.to_dict() if self.gpu_info else None,
            "checked_at": self.checked_at,
        }


async def detect_gpu() -> GPUInfo:
    """
    Detect available GPU and return info.

    Returns:
        GPUInfo: GPU detection result with provider, availability, count, and memory.
    """
    time.time()

    # Check for NVIDIA GPU
    try:
        result = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                "nvidia-smi",
                "--query-gpu=count,memory.total",
                "--format=csv,noheader,nounits",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            ),
            timeout=2.0,
        )
        stdout, _ = await result.communicate()
        if result.returncode == 0:
            parts = stdout.decode().strip().split(",")
            if len(parts) >= 2:
                count = int(parts[0].split()[0])  # First number from "N"
                memory_gb = int(parts[1].split()[0]) / 1024  # Convert MB to GB
                return GPUInfo(
                    provider=GPUProvider.NVIDIA,
                    available=True,
                    count=count,
                    memory_gb=memory_gb,
                    model="NVIDIA GPU",
                    detected_at=time.time(),
                )
    except (asyncio.TimeoutError, FileNotFoundError, ValueError, IndexError):
        pass

    # Check for AMD/ROCm GPU
    try:
        result = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                "rocm-smi",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            ),
            timeout=2.0,
        )
        stdout, _ = await result.communicate()
        if result.returncode == 0:
            # Simple check: if rocm-smi works, assume 1 GPU
            return GPUInfo(
                provider=GPUProvider.AMD,
                available=True,
                count=1,
                memory_gb=0.0,
                model="AMD GPU (ROCm)",
                detected_at=time.time(),
            )
    except (asyncio.TimeoutError, FileNotFoundError):
        pass

    # Check for Apple Silicon
    if os.uname().sysname == "Darwin":
        try:
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    "system_profiler",
                    "SPDisplaysDataType",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                ),
                timeout=2.0,
            )
            stdout, _ = await result.communicate()
            if result.returncode == 0 and b"Apple" in stdout:
                return GPUInfo(
                    provider=GPUProvider.APPLE,
                    available=True,
                    count=1,
                    memory_gb=0.0,
                    model="Apple Silicon",
                    detected_at=time.time(),
                )
        except (asyncio.TimeoutError, FileNotFoundError):
            pass

    # Check for Intel GPU
    if os.path.exists("/sys/class/drm") or os.path.exists("/dev/dri"):
        return GPUInfo(
            provider=GPUProvider.INTEL,
            available=True,
            count=1,
            memory_gb=0.0,
            model="Intel GPU",
            detected_at=time.time(),
        )

    # No GPU detected
    return GPUInfo(
        provider=GPUProvider.NONE,
        available=False,
        count=0,
        memory_gb=0.0,
        model="",
        detected_at=time.time(),
    )


async def check_ollama_health(
    base_url: str = "http://localhost:11434",
    timeout_seconds: float = 5.0,
) -> OllamaHealth:
    """
    Check Ollama daemon health and list available models.

    Args:
        base_url: Ollama base URL (default: http://localhost:11434)
        timeout_seconds: HTTP timeout in seconds

    Returns:
        OllamaHealth: Health check result with status, models, GPU info, response time.
    """
    start_time = time.time()
    gpu_info = None

    try:
        # Detect GPU first
        gpu_info = await detect_gpu()

        # Try to reach Ollama /api/tags endpoint
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            try:
                response = await client.get(f"{base_url}/api/tags")
                response_time_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    try:
                        data = response.json()
                        models = [m.get("name", m.get("model", "")) for m in data.get("models", [])]
                        return OllamaHealth(
                            healthy=True,
                            base_url=base_url,
                            status_code=response.status_code,
                            response_time_ms=response_time_ms,
                            models=models,
                            gpu_info=gpu_info,
                        )
                    except json.JSONDecodeError as e:
                        return OllamaHealth(
                            healthy=False,
                            base_url=base_url,
                            status_code=response.status_code,
                            response_time_ms=response_time_ms,
                            error=f"Invalid JSON response: {str(e)}",
                            gpu_info=gpu_info,
                        )
                else:
                    return OllamaHealth(
                        healthy=False,
                        base_url=base_url,
                        status_code=response.status_code,
                        response_time_ms=(time.time() - start_time) * 1000,
                        error=f"HTTP {response.status_code}",
                        gpu_info=gpu_info,
                    )
            except httpx.TimeoutException:
                return OllamaHealth(
                    healthy=False,
                    base_url=base_url,
                    status_code=0,
                    response_time_ms=(time.time() - start_time) * 1000,
                    error=f"Timeout after {timeout_seconds}s",
                    gpu_info=gpu_info,
                )
            except httpx.ConnectError as e:
                return OllamaHealth(
                    healthy=False,
                    base_url=base_url,
                    status_code=0,
                    response_time_ms=(time.time() - start_time) * 1000,
                    error=f"Connection error: {str(e)}",
                    gpu_info=gpu_info,
                )
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return OllamaHealth(
            healthy=False,
            base_url=base_url,
            status_code=0,
            response_time_ms=(time.time() - start_time) * 1000,
            error=str(e),
            gpu_info=gpu_info,
        )


async def check_lmstudio_health(
    base_url: str = "http://localhost:1234",
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    """
    Check LM Studio daemon health and list available models.

    Args:
        base_url: LM Studio base URL (default: http://localhost:1234)
        timeout_seconds: HTTP timeout in seconds

    Returns:
        dict: Health check result with status, models, response time.
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            try:
                response = await client.get(f"{base_url}/v1/models")
                response_time_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    try:
                        data = response.json()
                        models = [m.get("id", m.get("model", "")) for m in data.get("data", [])]
                        return {
                            "healthy": True,
                            "base_url": base_url,
                            "status_code": response.status_code,
                            "response_time_ms": round(response_time_ms, 2),
                            "models": models,
                            "error": "",
                        }
                    except json.JSONDecodeError as e:
                        return {
                            "healthy": False,
                            "base_url": base_url,
                            "status_code": response.status_code,
                            "response_time_ms": round(response_time_ms, 2),
                            "models": [],
                            "error": f"Invalid JSON response: {str(e)}",
                        }
                else:
                    return {
                        "healthy": False,
                        "base_url": base_url,
                        "status_code": response.status_code,
                        "response_time_ms": round((time.time() - start_time) * 1000, 2),
                        "models": [],
                        "error": f"HTTP {response.status_code}",
                    }
            except httpx.TimeoutException:
                return {
                    "healthy": False,
                    "base_url": base_url,
                    "status_code": 0,
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "models": [],
                    "error": f"Timeout after {timeout_seconds}s",
                }
            except httpx.ConnectError as e:
                return {
                    "healthy": False,
                    "base_url": base_url,
                    "status_code": 0,
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "models": [],
                    "error": f"Connection error: {str(e)}",
                }
    except Exception as e:
        logger.error(f"LM Studio health check failed: {e}")
        return {
            "healthy": False,
            "base_url": base_url,
            "status_code": 0,
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "models": [],
            "error": str(e),
        }
