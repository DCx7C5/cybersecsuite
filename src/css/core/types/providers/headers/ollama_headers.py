"""Headers for Ollama provider (local LLM support)."""

from dataclasses import dataclass

from .local_headers import OllamaLocalHeader


@dataclass
class OllamaHeader(OllamaLocalHeader):
    """Comprehensive header for Ollama local provider.

    Extends OllamaLocalHeader with execution-specific metadata.
    """

    # Resource management
    gpu_layers: int = 0  # Number of layers to offload to GPU
    num_gpu: int = -1  # Number of GPUs (-1 = all available)
    num_thread: int = 4  # Number of CPU threads
    batch_size: int = 512  # Batch size for processing

    # Model management
    keep_alive: int = 5 * 60  # Keep model in memory for 5 minutes
    model_auto_pull: bool = False  # Auto-pull missing models
    model_auto_load: bool = True  # Auto-load models on startup

    # Performance tuning
    streaming_chunk_size: int = 1024
    streaming_timeout_seconds: int = 120
    connection_pool_size: int = 10

    # Debugging
    verbose_mode: bool = False
    log_requests: bool = False
    track_metrics: bool = True

    # Health checks
    health_check_interval_seconds: int = 60
    health_check_timeout_seconds: int = 10

    # Capabilities detection
    detect_vision: bool = False  # Detect vision models
    detect_embeddings: bool = True  # Detect embedding models


__all__ = ["OllamaHeader"]
