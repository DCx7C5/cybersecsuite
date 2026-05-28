"""Bridge adapter builtin tools into ToolRegistry.

Converts adapter-provided `Tool` objects (core/base/messages)
to `ToolSchema` objects and registers them with ToolRegistry.
"""

from collections.abc import Callable, Sequence
from typing import Any, cast

from css.core.logger import getLogger
from css.core.messages.types import Tool as AdapterTool
from css.modules.tools.enums import ParameterType
from css.modules.tools.registry import ToolRegistry
from css.modules.tools.types import ToolParameter, ToolReturnType, ToolSchema

logger = getLogger(__name__)


def _infer_parameter_type(schema: dict[str, object]) -> ParameterType:
    js_type = str(schema.get("type", "string"))
    mapping: dict[str, ParameterType] = {
        "string": ParameterType.STRING,
        "integer": ParameterType.INTEGER,
        "number": ParameterType.NUMBER,
        "boolean": ParameterType.BOOLEAN,
        "array": ParameterType.ARRAY,
        "object": ParameterType.OBJECT,
    }
    return mapping.get(js_type, ParameterType.STRING)


def _convert_tool_to_schema(provider: str, tool: AdapterTool) -> ToolSchema:
    params: list[ToolParameter] = []
    required_params: list[str] = tool.input_schema.get("required", [])
    properties = tool.input_schema.get("properties", {})

    for name, prop_schema in properties.items():
        if not isinstance(prop_schema, dict):
            continue
        params.append(ToolParameter(
            name=name,
            type=_infer_parameter_type(prop_schema),
            description=str(prop_schema.get("description", "")),
            required=name in required_params,
            enum=list(prop_schema.get("enum", [])),
        ))

    return ToolSchema(
        provider=provider,
        name=tool.name,
        description=tool.description,
        parameters=params,
        returns=ToolReturnType(type="object", description="Tool execution result"),
        tags=["builtin", provider],
    )


def register_adapter_tools(registry: ToolRegistry | None = None) -> None:
    """Register builtin_tools() from all registered SDK adapters.

    Call once at startup after all SDK adapters have been registered.
    """
    from css.core.sdks.registry import SDKRegistry

    if registry is None:
        registry = cast(ToolRegistry, ToolRegistry())

    sdk_registry = SDKRegistry()
    for provider_id in sdk_registry.list_registered():
        try:
            adapter_class = sdk_registry._registry.get(provider_id)
            if adapter_class is None:
                continue
            if callable(adapter_class):
                factory = cast(Callable[[], Any], adapter_class)
                instance: Any = factory()
            else:
                instance = adapter_class
            builtin_tools_method = getattr(instance, "builtin_tools", None)
            if builtin_tools_method is None:
                continue
            tools: Sequence[AdapterTool] = builtin_tools_method()
            for tool in tools:
                if not isinstance(tool, AdapterTool):
                    continue
                schema = _convert_tool_to_schema(provider_id, tool)
                registry.register_tool(schema.tool_id, schema.to_dict())
                logger.debug("Registered builtin tool %s from %s", schema.tool_id, provider_id)
        except Exception as exc:
            logger.warning("Failed to register builtin tools for %s: %s", provider_id, exc)

