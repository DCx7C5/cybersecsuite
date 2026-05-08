"""Tool type definitions for registry and API surfaces."""

import time

import msgspec

from css.modules.tools.enums import CompositionStrategy, ParameterType


# TODO: Don't use objects as types here. Create precise TypedDicts if possible, create new type or find other solutions

class ToolParameter(msgspec.Struct):
    name: str
    type: ParameterType
    description: str
    required: bool = False
    default: object | None = None
    enum: list[object] = msgspec.field(default_factory=list)
    items: dict[str, object] = msgspec.field(default_factory=dict)
    properties: dict[str, object] = msgspec.field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "enum": self.enum,
            "items": self.items,
            "properties": self.properties,
        }


class ToolReturnType(msgspec.Struct):
    type: str
    description: str
    schema: dict[str, object] = msgspec.field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "description": self.description,
            "schema": self.schema,
        }


class ToolSchema(msgspec.Struct):
    provider: str
    name: str
    description: str
    parameters: list[ToolParameter] = msgspec.field(default_factory=list)
    returns: ToolReturnType | None = None
    version: str = "1.0"
    enabled: bool = True
    tags: list[str] = msgspec.field(default_factory=list)
    examples: list[str] = msgspec.field(default_factory=list)
    requires_auth: bool = False
    rate_limit: int | None = None
    timeout_seconds: int = 30
    cost_per_call: float | None = None
    type: str = "builtin"

    @property
    def tool_id(self) -> str:
        return f"{self.provider}:{self.name}"

    def to_dict(self) -> dict[str, object]:
        return {
            "tool_id": self.tool_id,
            "provider": self.provider,
            "name": self.name,
            "description": self.description,
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "returns": self.returns.to_dict() if self.returns is not None else None,
            "version": self.version,
            "enabled": self.enabled,
            "tags": self.tags,
            "examples": self.examples,
            "requires_auth": self.requires_auth,
            "rate_limit": self.rate_limit,
            "timeout_seconds": self.timeout_seconds,
            "cost_per_call": self.cost_per_call,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ToolSchema":
        provider = str(data.get("provider", ""))
        name = str(data.get("name", ""))
        description = str(data.get("description", ""))

        parameters_data = data.get("parameters", [])
        parameters: list[ToolParameter] = []
        if isinstance(parameters_data, list):
            for item in parameters_data:
                if isinstance(item, dict):
                    parameter_type = ParameterType(str(item.get("type", ParameterType.STRING.value)))
                    parameters.append(
                        ToolParameter(
                            name=str(item.get("name", "")),
                            type=parameter_type,
                            description=str(item.get("description", "")),
                            required=bool(item.get("required", False)),
                            default=item.get("default"),
                            enum=item.get("enum", []) if isinstance(item.get("enum"), list) else [],
                            items=item.get("items", {}) if isinstance(item.get("items"), dict) else {},
                            properties=item.get("properties", {}) if isinstance(item.get("properties"), dict) else {},
                        )
                    )

        returns_data = data.get("returns")
        returns: ToolReturnType | None = None
        if isinstance(returns_data, dict):
            returns = ToolReturnType(
                type=str(returns_data.get("type", "object")),
                description=str(returns_data.get("description", "")),
                schema=returns_data.get("schema", {}) if isinstance(returns_data.get("schema"), dict) else {},
            )

        return cls(
            provider=provider,
            name=name,
            description=description,
            parameters=parameters,
            returns=returns,
            version=str(data.get("version", "1.0")),
            enabled=bool(data.get("enabled", True)),
            tags=[str(tag) for tag in data.get("tags", [])] if isinstance(data.get("tags"), list) else [],
            examples=[str(example) for example in data.get("examples", [])]
            if isinstance(data.get("examples"), list)
            else [],
            requires_auth=bool(data.get("requires_auth", False)),
            rate_limit=int(data["rate_limit"]) if isinstance(data.get("rate_limit"), int) else None,
            timeout_seconds=int(data.get("timeout_seconds", 30)),
            cost_per_call=float(data["cost_per_call"]) if isinstance(data.get("cost_per_call"), (int, float)) else None,
            type=str(data.get("type", "builtin")),
        )


class HybridToolSchema(msgspec.Struct):
    name: str
    description: str
    component_tools: list[str]
    composition_strategy: CompositionStrategy
    fallback_provider: str | None = None
    requires_coordination: bool = False
    metadata: dict[str, object] = msgspec.field(default_factory=dict)
    enabled: bool = True
    tags: list[str] = msgspec.field(default_factory=list)

    @property
    def provider(self) -> str:
        return "hybrid"

    @property
    def tool_id(self) -> str:
        return f"hybrid:{self.name}"

    @property
    def type(self) -> str:
        return "hybrid"

    def to_dict(self) -> dict[str, object]:
        return {
            "tool_id": self.tool_id,
            "provider": self.provider,
            "name": self.name,
            "description": self.description,
            "component_tools": self.component_tools,
            "composition_strategy": self.composition_strategy.value,
            "fallback_provider": self.fallback_provider,
            "requires_coordination": self.requires_coordination,
            "metadata": self.metadata,
            "enabled": self.enabled,
            "tags": self.tags,
            "type": self.type,
        }


class ManagedTool(msgspec.Struct):
    schema: ToolSchema | HybridToolSchema
    last_called: float | None = None
    call_count: int = 0
    last_error: str | None = None
    disabled_reason: str | None = None

    @property
    def is_available(self) -> bool:
        return self.schema.enabled and self.disabled_reason is None

    def mark_called(self) -> None:
        self.last_called = time.time()
        self.call_count += 1
        self.last_error = None

    def mark_error(self, error: str) -> None:
        self.last_called = time.time()
        self.last_error = error


Tool = ToolSchema
