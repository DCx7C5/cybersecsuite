"""Builtin provider tool catalog for ToolRegistry bootstrap."""

import pkgutil
from pathlib import Path

from css.modules.tools.enums import ParameterType
from css.modules.tools.types import ToolParameter, ToolReturnType, ToolSchema


def discover_provider_ids() -> set[str]:
    """Discover provider package names under ``src/css/api_services``."""
    api_services = Path(__file__).resolve().parents[2] / "api_services"
    return {
        name
        for _, name, is_pkg in pkgutil.iter_modules([str(api_services)])
        if is_pkg and not name.startswith("_")
    }


def load_builtin_tool_schemas() -> dict[str, list[ToolSchema]]:
    """Return builtin tool schemas keyed by provider slug."""
    return {
        "openai": [
            ToolSchema(
                provider="openai",
                name="code_interpreter",
                description="Execute Python code and return execution output.",
                parameters=[
                    ToolParameter(
                        name="code",
                        type=ParameterType.STRING,
                        description="Python source code to execute.",
                        required=True,
                    )
                ],
                returns=ToolReturnType(
                    type="object",
                    description="Execution result object containing stdout/stderr/artifacts.",
                ),
                tags=["code", "python", "execution"],
                timeout_seconds=60,
            ),
            ToolSchema(
                provider="openai",
                name="file_search",
                description="Search indexed files and return matching snippets.",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Query string for retrieval.",
                        required=True,
                    )
                ],
                returns=ToolReturnType(
                    type="array",
                    description="Matching file snippets.",
                ),
                tags=["search", "retrieval"],
            ),
        ],
        "anthropic": [
            ToolSchema(
                provider="anthropic",
                name="computer_use",
                description="Perform UI actions using vision-guided automation.",
                parameters=[
                    ToolParameter(
                        name="action",
                        type=ParameterType.STRING,
                        description="Action to perform.",
                        required=True,
                        enum=["screenshot", "click", "type", "scroll", "key_press"],
                    ),
                    ToolParameter(
                        name="coordinates",
                        type=ParameterType.ARRAY,
                        description="[x,y] target for pointer actions.",
                    ),
                    ToolParameter(
                        name="text",
                        type=ParameterType.STRING,
                        description="Input text for typing actions.",
                    ),
                ],
                returns=ToolReturnType(
                    type="object",
                    description="Action result payload.",
                ),
                tags=["computer_vision", "interaction"],
            )
        ],
        "groq": [],
        "ollama": [],
        "gemini": [],
        "mistral": [],
        "together": [],
    }
