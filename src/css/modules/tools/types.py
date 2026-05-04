"""Tool type definitions and data models for normalized tool definitions.

Provides unified data structures for tool definitions across all 26 LLM providers.
Enables consistent representation of tools with different naming/structure conventions.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from css.modules.tools.enums import ParameterType


@dataclass
class ToolParameter:
    """Single parameter definition for a tool.
    
    Attributes:
        name: Parameter name (must be unique within a tool)
        type: Parameter data type
        description: Human-readable description of the parameter
        required: Whether this parameter is mandatory
        default: Default value if not provided
        enum: List of allowed values (if constrained)
        items: Schema for array items (if type is array)
        properties: Schema for object properties (if type is object)
    """
    name: str
    type: ParameterType
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[list[Any]] = None
    items: Optional[dict[str, Any]] = None
    properties: Optional[dict[str, Any]] = None


@dataclass
class ToolReturnType:
    """Return value specification for a tool.
    
    Attributes:
        type: Return type (string, integer, object, array, etc.)
        description: Description of what the tool returns
        schema: JSON Schema for the return value structure (if complex)
    """
    type: str
    description: str
    schema: Optional[dict[str, Any]] = None


@dataclass
class ToolSchema:
    """Normalized tool schema for unified representation across all LLM providers.
    
    This is the canonical format for all tools, regardless of provider SDK differences.
    Tools from different providers are normalized to this schema during registry loading.
    
    Attributes:
        provider: LLM provider ID (openai, anthropic, groq, ollama, etc.)
        name: Tool name (unique per provider, e.g., 'code_interpreter')
        description: Human-readable tool description
        parameters: List of parameter definitions (empty if no parameters)
        returns: Return value specification
        version: Tool API version (some providers have multiple versions)
        enabled: Whether tool is currently enabled
        tags: Optional tags for categorization (e.g., ['code', 'execution'])
        examples: Optional usage examples
        requires_auth: Whether tool requires additional authentication
        rate_limit: Optional rate limit (requests per minute, None if unlimited)
        timeout_seconds: Execution timeout in seconds
        cost_per_call: Estimated cost per call (if metered)
    """
    provider: str
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: Optional[ToolReturnType] = None
    version: str = "1.0"
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    requires_auth: bool = False
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    cost_per_call: Optional[float] = None

    @property
    def tool_id(self) -> str:
        """Unique tool identifier combining provider and name."""
        return f"{self.provider}:{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_id": self.tool_id,
            "provider": self.provider,
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type.value,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "enum": p.enum,
                }
                for p in self.parameters
            ],
            "returns": {
                "type": self.returns.type,
                "description": self.returns.description,
                "schema": self.returns.schema,
            } if self.returns else None,
            "version": self.version,
            "enabled": self.enabled,
            "tags": self.tags,
            "examples": self.examples,
            "requires_auth": self.requires_auth,
            "rate_limit": self.rate_limit,
            "timeout_seconds": self.timeout_seconds,
            "cost_per_call": self.cost_per_call,
        }


@dataclass
class HybridToolSchema:
    """Composite tool combining capabilities from multiple LLM providers.
    
    Enables hybrid workflows: combine OpenAI code execution + Anthropic vision,
    or route to different providers based on capability/availability.
    
    Attributes:
        name: Unique hybrid tool identifier
        description: What this hybrid tool does
        component_tools: List of tool_ids (format: "provider:name")
        composition_strategy: How to blend tools (sequential, parallel, conditional, fallback, load_balanced)
        fallback_provider: Optional fallback provider if primary fails
        requires_coordination: Whether component tools need sequential execution
        metadata: Additional configuration (serialized to JSON in DB)
        enabled: Whether tool is currently enabled
        tags: Categorization tags
    """
    name: str
    description: str
    component_tools: list[str]
    composition_strategy: str
    fallback_provider: Optional[str] = None
    requires_coordination: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    tags: list[str] = field(default_factory=list)

    @property
    def tool_id(self) -> str:
        """Unique identifier for this hybrid tool."""
        return f"hybrid:{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "component_tools": self.component_tools,
            "composition_strategy": self.composition_strategy,
            "fallback_provider": self.fallback_provider,
            "requires_coordination": self.requires_coordination,
            "metadata": self.metadata,
            "enabled": self.enabled,
            "tags": self.tags,
        }


@dataclass
class ManagedTool:
    """Runtime wrapper for a tool with execution state and metadata.
    
    Used by ToolRegistry to track tool status, execution history, and configuration.
    Works with both ToolSchema and HybridToolSchema.
    
    Attributes:
        schema: The canonical ToolSchema or HybridToolSchema definition
        last_called: Timestamp of last execution
        call_count: Total number of times tool was called
        last_error: Last error message if any
        disabled_reason: If disabled, the reason why
    """
    schema: Any
    last_called: Optional[float] = None
    call_count: int = 0
    last_error: Optional[str] = None
    disabled_reason: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Check if tool is available for execution."""
        return self.schema.enabled and self.disabled_reason is None

    def mark_called(self) -> None:
        """Record that tool was called."""
        import time
        self.last_called = time.time()
        self.call_count += 1
        self.last_error = None

    def mark_error(self, error: str) -> None:
        """Record tool execution error."""
        import time
        self.last_called = time.time()
        self.last_error = error
