"""LLM model registry and management."""

from .enums import ModelProvider, ModelFamily, ModelCapability
from .models import ModelMetadata, ModelPricing
from .registry import ModelRegistry, DEFAULT_MODELS, get_model_registry
from .discovery import (
    discover_groq_models,
    discover_mistral_models,
    discover_ollama_models,
    discover_openrouter_models,
)
from .discovery_integration import register_model_discovery_providers

from css.core.logger import getLogger
logger = getLogger(__name__)

logger.info("LLM models module loaded")
