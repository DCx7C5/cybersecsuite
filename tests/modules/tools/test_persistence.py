import pytest

from css.modules.tools.enums import CompositionStrategy
from css.modules.tools.registry import ToolRegistry
from css.modules.tools.types import HybridToolSchema


@pytest.mark.asyncio
async def test_save_hybrid_tool_persists_new_record(monkeypatch):
    from css.modules.tools import models as tools_models

    class FakeHybridToolDefinition:
        created = None

        def __init__(self, name: str):
            self.name = name
            self.saved = False

        async def save(self) -> None:
            self.saved = True

        @classmethod
        async def get_or_none(cls, name: str):
            return None

        @classmethod
        def from_schema(cls, schema: HybridToolSchema):
            instance = cls(schema.name)
            cls.created = instance
            return instance

    monkeypatch.setattr(tools_models, "HybridToolDefinition", FakeHybridToolDefinition)

    registry = ToolRegistry()
    schema = HybridToolSchema(
        name="persisted-analysis",
        description="Persisted test tool",
        component_tools=["openai:code_interpreter"],
        composition_strategy=CompositionStrategy.SEQUENTIAL,
    )

    await registry.save_hybrid_tool(schema)

    assert FakeHybridToolDefinition.created is not None
    assert FakeHybridToolDefinition.created.name == "persisted-analysis"
    assert FakeHybridToolDefinition.created.saved is True


@pytest.mark.asyncio
async def test_load_hybrid_tools_from_db_registers_tools(monkeypatch):
    from css.modules.tools import models as tools_models

    schema = HybridToolSchema(
        name="loaded-analysis",
        description="Loaded from DB",
        component_tools=["openai:file_search"],
        composition_strategy=CompositionStrategy.PARALLEL,
    )

    class FakeOrmRow:
        def to_schema(self) -> HybridToolSchema:
            return schema

    class FakeHybridToolDefinition:
        @classmethod
        async def all(cls):
            return [FakeOrmRow()]

    monkeypatch.setattr(tools_models, "HybridToolDefinition", FakeHybridToolDefinition)

    registry = ToolRegistry()
    await registry._load_hybrid_tools_from_db()

    loaded = registry.get_hybrid_tool("hybrid:loaded-analysis")
    assert loaded.name == "loaded-analysis"
    assert loaded.composition_strategy is CompositionStrategy.PARALLEL


def test_hybrid_schema_tool_id_and_serialization():
    schema = HybridToolSchema(
        name="security-audit",
        description="Hybrid schema serialization check",
        component_tools=["openai:file_search"],
        composition_strategy=CompositionStrategy.SEQUENTIAL,
        fallback_provider="openai",
        requires_coordination=True,
        metadata={"domain": "security"},
        tags=["audit"],
    )

    data = schema.to_dict()
    assert schema.tool_id == "hybrid:security-audit"
    assert data["tool_id"] == "hybrid:security-audit"
    assert data["composition_strategy"] == "sequential"
    assert data["fallback_provider"] == "openai"


def test_register_hybrid_tool_validates_component_tools():
    registry = ToolRegistry()
    invalid = HybridToolSchema(
        name="invalid-hybrid",
        description="Uses missing component tool",
        component_tools=["openai:does_not_exist"],
        composition_strategy=CompositionStrategy.SEQUENTIAL,
    )

    with pytest.raises(ValueError, match="Component tool not found"):
        registry.register_hybrid_tool(invalid)


def test_resolve_tool_returns_builtin_and_hybrid():
    registry = ToolRegistry()
    hybrid = HybridToolSchema(
        name="resolver-check",
        description="Resolver test tool",
        component_tools=["openai:code_interpreter"],
        composition_strategy=CompositionStrategy.PARALLEL,
    )
    registry.register_hybrid_tool(hybrid)

    builtin = registry.resolve_tool("openai:code_interpreter")
    resolved_hybrid = registry.resolve_tool("hybrid:resolver-check")

    assert builtin.tool_id == "openai:code_interpreter"
    assert resolved_hybrid.tool_id == "hybrid:resolver-check"
