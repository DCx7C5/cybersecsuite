"""Enumeration types for tool definitions and configuration.

Defines all enum classes used across the tools module for type safety
and standardized value constraints.
"""

from enum import Enum


class ParameterType(str, Enum):
    """Parameter type enumeration for tool parameter definitions.
    
    Represents JSON Schema-compatible types for tool parameters.
    """
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


class ToolStatus(str, Enum):
    """Status of a tool."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


class ToolType(str, Enum):
    """Type of tool."""
    # TODO: Add comments
    BUILTIN = "builtin"         #
    CUSTOM = "custom"           #
    EXTERNAL = "external"
    MCP = "mcp"


class CompositionStrategy(str, Enum):
    """Strategy for composing hybrid tools across multiple providers.
    
    Defines how component tools are combined and executed in a hybrid tool.
    """
    # TODO: Add comments
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    FALLBACK = "fallback"
    LOAD_BALANCED = "load_balanced"
