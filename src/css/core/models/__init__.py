"""LLM model registry and management."""

from .enums import ModelProvider, ModelFamily, ModelCapability
from .models import ModelMetadata, ModelPricing
from .registry import ModelRegistry, DEFAULT_MODELS, get_model_registry

from css.core.logger import getLogger
logger = getLogger(__name__)

__all__ = [
    # Enums
    "ModelProvider",
    "ModelFamily",
    "ModelCapability",
    
    # Models
    "ModelMetadata",
    "ModelPricing",
    
    # Registry
    "ModelRegistry",
    "DEFAULT_MODELS",
    "get_model_registry",
]

logger.info("LLM models module loaded")
