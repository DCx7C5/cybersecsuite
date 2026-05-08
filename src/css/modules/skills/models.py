"""Skill data models and types."""
from collections.abc import Callable
from datetime import datetime

import msgspec
from tortoise import fields, models

from css.core.db.fields import DescriptionField, VersionField
from css.core.db.models.base import BaseModel

from .enums import SkillStatus, SkillCategory

@msgspec.struct
class SkillParameter:
    """Definition of a skill parameter."""
    name: str
    param_type: str  # "string", "integer", "boolean", "array", "object"
    description: str = ""
    required: bool = True
    default_value: object | None = None
    validation_rules: dict[str, object] = msgspec.field(default_factory=dict)

@msgspec.struct
class SkillResult:
    """Result from skill execution."""
    skill_id: str
    success: bool
    output: object | None = None
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
    handler: Callable[..., object] | None = None  # Execution function
    
    # Metadata
    author: str = ""
    tags: list[str] = msgspec.field(default_factory=list)
    dependencies: list[str] = msgspec.field(default_factory=list)  # Other skill IDs
    custom_metadata: dict[str, object] = msgspec.field(default_factory=dict)
    
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


class SkillDefinitionModel(BaseModel):
    """Persistent skill definition in the database (Ring 2 ORM model)."""

    skill_id = fields.CharField(max_length=255, unique=True, db_index=True)
    name = fields.CharField(max_length=255)
    description = DescriptionField()
    category = fields.CharEnumField(SkillCategory, db_index=True)
    status = fields.CharEnumField(SkillStatus, default=SkillStatus.ACTIVE, db_index=True)
    version = VersionField()
    parameters_json = fields.JSONField(default=list)
    is_builtin = fields.BooleanField(default=False, db_index=True)
    author = fields.CharField(max_length=255, default="")
    tags = fields.JSONField(default=list)
    dependencies = fields.JSONField(default=list)
    custom_metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "skill_definitions"
        table_description = "Persistent skill definitions and metadata"
        ordering = ["skill_id"]
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["is_builtin", "status"]),
        ]

    def to_domain(self) -> SkillDefinition:
        parameters: list[SkillParameter] = []
        for item in self.parameters_json:
            if isinstance(item, dict):
                parameters.append(
                    SkillParameter(
                        name=str(item.get("name", "")),
                        param_type=str(item.get("param_type", "string")),
                        description=str(item.get("description", "")),
                        required=bool(item.get("required", True)),
                        default_value=item.get("default_value"),
                        validation_rules=(
                            item.get("validation_rules", {})
                            if isinstance(item.get("validation_rules"), dict)
                            else {}
                        ),
                    )
                )

        return SkillDefinition(
            skill_id=self.skill_id,
            name=self.name,
            description=self.description,
            category=self.category,
            version=self.version,
            status=self.status,
            parameters=parameters,
            handler=None,
            author=self.author,
            tags=[str(tag) for tag in self.tags if isinstance(tag, str)],
            dependencies=[str(dep) for dep in self.dependencies if isinstance(dep, str)],
            custom_metadata=self.custom_metadata if isinstance(self.custom_metadata, dict) else {},
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, skill: SkillDefinition, is_builtin: bool = False) -> "SkillDefinitionModel":
        return cls(
            skill_id=skill.skill_id,
            name=skill.name,
            description=skill.description,
            category=skill.category,
            status=skill.status,
            version=skill.version,
            parameters_json=[
                {
                    "name": parameter.name,
                    "param_type": parameter.param_type,
                    "description": parameter.description,
                    "required": parameter.required,
                    "default_value": parameter.default_value,
                    "validation_rules": parameter.validation_rules,
                }
                for parameter in skill.parameters
            ],
            is_builtin=is_builtin,
            author=skill.author,
            tags=skill.tags,
            dependencies=skill.dependencies,
            custom_metadata=skill.custom_metadata,
        )
