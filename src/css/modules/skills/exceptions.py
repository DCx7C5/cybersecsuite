from css.core.exceptions import BaseModuleException


class BaseSkillException(BaseModuleException):
    """Base exception for the skill module."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="skill", **kwargs)


class SkillNotFoundError(BaseSkillException):
    """Raised when skill is not found."""

    def __init__(self, skill_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if skill_id:
            ctx["skill_id"] = skill_id
        super().__init__(
            f"Skill not found: {skill_id}" if skill_id else "Skill not found",
            context=ctx,
            **kwargs
        )


class SkillExecutionError(BaseSkillException):
    """Raised when skill execution fails."""

    def __init__(self, message: str = None, skill_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if skill_id:
            ctx["skill_id"] = skill_id
        super().__init__(
            message or f"Skill execution failed: {skill_id}" if skill_id else "Skill execution failed",
            context=ctx,
            **kwargs
        )


class SkillConfigurationError(BaseSkillException):
    """Raised when skill configuration is invalid."""

    def __init__(self, message: str = None, config_key: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if config_key:
            ctx["config_key"] = config_key
        super().__init__(
            message or f"Skill configuration error: {config_key}" if config_key else "Skill configuration error",
            context=ctx,
            **kwargs
        )
