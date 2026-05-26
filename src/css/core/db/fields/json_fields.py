from typing import Any, override

from tortoise.fields import JSONField
from tortoise.models import Model


class StringListField(JSONField):
    """JSON list field normalized to ``list[str]``."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", list)
        super().__init__(*args, **kwargs)

    @override
    def to_db_value(self, value: Any, instance: Model | type[Model]) -> Any:
        if value is None:
            return None
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"Expected list/tuple value, got {type(value).__name__}")
        normalized = [str(item) for item in value]
        return super().to_db_value(normalized, instance)

    @override
    def to_python_value(self, value: Any) -> list[str] | None:
        if value is None:
            return None
        parsed = super().to_python_value(value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected list payload, got {type(parsed).__name__}")
        return [str(item) for item in parsed]


class JsonObjectField(JSONField):
    """JSON object field normalized to ``dict[str, Any]``."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", dict)
        super().__init__(*args, **kwargs)

    @override
    def to_db_value(self, value: Any, instance: Model | type[Model]) -> Any:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict value, got {type(value).__name__}")
        normalized = {str(key): item for key, item in value.items()}
        return super().to_db_value(normalized, instance)

    @override
    def to_python_value(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        parsed = super().to_python_value(value)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected object payload, got {type(parsed).__name__}")
        return {str(key): item for key, item in parsed.items()}
