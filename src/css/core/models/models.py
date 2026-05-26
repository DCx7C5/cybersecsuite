"""LLM model metadata and validation."""
import msgspec

from typing import Any

from css.core.db.models.base import BaseModel
from .enums import ModelProvider, ModelFamily, ModelCapability

class ModelPricing(msgspec.Struct, frozen=True, kw_only=True):
    """Pricing information for a model."""
    input_tokens_per_1k: float  # Cost per 1000 input tokens
    output_tokens_per_1k: float  # Cost per 1000 output tokens
    currency: str = "USD"

class LLMModel(BaseModel):
    # TODO: implement real database table; get rid off @dataclass ModelMetadata and ModelPricing. Find other ways to implement
    ...

class ModelMetadata(msgspec.Struct, frozen=True, kw_only=True):
    """Metadata for an LLM model."""
    
    id: str  # e.g., "claude-3-opus-20240229"
    provider: ModelProvider
    family: ModelFamily
    display_name: str
    
    # Architecture
    context_window: int  # Max context window in tokens
    max_output_tokens: int  # Max output tokens per call
    
    # Performance
    latency_ms: int  # Typical latency in milliseconds
    throughput_tokens_per_sec: float = 100.0
    
    # Pricing
    pricing: ModelPricing | None = None
    
    # Capabilities
    capabilities: set[ModelCapability] = msgspec.field(default_factory=set)
    
    # Configuration
    temperature_range: tuple = (0.0, 2.0)
    top_p_range: tuple = (0.0, 1.0)
    top_k_range: tuple = (0, 500)
    
    # Metadata
    released_at: str = ""  # ISO 8601 date
    deprecated: bool = False
    custom_params: dict[str, Any] = msgspec.field(default_factory=dict)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage."""
        if not self.pricing:
            return 0.0
        
        input_cost = (input_tokens / 1000) * self.pricing.input_tokens_per_1k
        output_cost = (output_tokens / 1000) * self.pricing.output_tokens_per_1k
        return input_cost + output_cost
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports capability."""
        return capability in self.capabilities
    
    def validate_parameters(self, **kwargs) -> dict[str, str]:
        """Validate model parameters. Return errors dict if invalid."""
        errors = {}
        
        if "temperature" in kwargs:
            temp = kwargs["temperature"]
            min_temp, max_temp = self.temperature_range
            if not (min_temp <= temp <= max_temp):
                errors["temperature"] = f"Must be between {min_temp} and {max_temp}"
        
        if "top_p" in kwargs:
            top_p = kwargs["top_p"]
            min_p, max_p = self.top_p_range
            if not (min_p <= top_p <= max_p):
                errors["top_p"] = f"Must be between {min_p} and {max_p}"
        
        if "top_k" in kwargs:
            top_k = kwargs["top_k"]
            min_k, max_k = self.top_k_range
            if not (min_k <= top_k <= max_k):
                errors["top_k"] = f"Must be between {min_k} and {max_k}"
        
        if "max_tokens" in kwargs:
            max_tokens = kwargs["max_tokens"]
            if max_tokens > self.max_output_tokens:
                errors["max_tokens"] = f"Cannot exceed {self.max_output_tokens}"
        
        return errors
