"""Skill data models and types."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable
from datetime import datetime

from .enums import SkillStatus, SkillCategory


@dataclass
class SkillParameter:
    """Definition of a skill parameter."""
    name: str
    param_type: str  # "string", "integer", "boolean", "array", "object"
    description: str = ""
    required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillResult:
    """Result from skill execution."""
    skill_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    executed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SkillDefinition:
    """Complete definition of a skill."""
    skill_id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    status: SkillStatus = SkillStatus.ACTIVE
    
    # Parameters and execution
    parameters: List[SkillParameter] = field(default_factory=list)
    handler: Optional[Callable] = None  # Execution function
    
    # Metadata
    author: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other skill IDs
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def validate_parameters(self, **kwargs) -> Dict[str, str]:
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
