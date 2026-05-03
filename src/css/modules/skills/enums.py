"""Skill enumerations."""

from enum import Enum


class SkillStatus(str, Enum):
    """Status of a skill."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ERROR = "error"


class SkillCategory(str, Enum):
    """Category of a skill."""
    
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    CUSTOM = "custom"
