"""Skill data models and types."""
import msgspec

from typing import Any
from collections.abc import Callable
from datetime import datetime

from .enums import SkillStatus, SkillCategory

@msgspec.struct
class SkillParameter:
    """Definition of a skill parameter."""
    name: str
    param_type: str  # "string", "integer", "boolean", "array", "object"
    description: str = ""
    required: bool = True
    default_value: Any = None
    validation_rules: dict[str, Any] = msgspec.field(default_factory=dict)

@msgspec.struct
class SkillResult:
    """Result from skill execution."""
    skill_id: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    executed_at: datetime = msgspec.field(default_factory=datetime.utcnow)

@msgspec.struct
class SkillDefinition:
    """Complete definition of a skill."""
    skill_id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    status: SkillStatus = SkillStatus.ACTIVE
    
    # Parameters and execution
    parameters: list[SkillParameter] = msgspec.field(default_factory=list)
    handler: Callable | None = None  # Execution function
    
    # Metadata
    author: str = ""
    tags: list[str] = msgspec.field(default_factory=list)
    dependencies: list[str] = msgspec.field(default_factory=list)  # Other skill IDs
    custom_metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    
    # Lifecycle
    created_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    updated_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    
    def validate_parameters(self, **kwargs) -> dict[str, str]:
        """Validate parameters against definition."""
        errors = {}
        
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                errors[param.name] = "Required parameter missing"
                continue
            
            if param.name in kwargs:
                value = kwargs[param.name]
                
                # Type checking
                if param.param_type == "string" and not isinstance(value, str):
                    errors[param.name] = f"Expected string, got {type(value).__name__}"
                elif param.param_type == "integer" and not isinstance(value, int):
                    errors[param.name] = f"Expected integer, got {type(value).__name__}"
                elif param.param_type == "boolean" and not isinstance(value, bool):
                    errors[param.name] = f"Expected boolean, got {type(value).__name__}"
                elif param.param_type == "array" and not isinstance(value, list):
                    errors[param.name] = f"Expected array, got {type(value).__name__}"
                elif param.param_type == "object" and not isinstance(value, dict):
                    errors[param.name] = f"Expected object, got {type(value).__name__}"
        
        return errors
