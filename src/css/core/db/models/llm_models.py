"""Provider-linked LLM model catalog ORM records and query helpers."""

from datetime import datetime
from enum import Enum
from typing import Any
from typing import cast

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.fields import (
    CurrencyCodeField,
    DescriptionField,
    JsonObjectField,
    LabelField,
    NonNegativeFloatField,
    NonNegativeIntField,
    PositiveIntField,
    StringListField,
    TemperatureFloatField,
    UnitIntervalFloatField,
)
from css.core.models.enums import ModelCapability, ModelFamily, ModelProvider
from css.core.models.models import ModelMetadata, ModelPricing

from .base import BaseModel
from .mixins import TimestampMixin


def _enum_value(value: Enum | str) -> str:
    """Return the string value for either an enum member or a raw string."""

    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


class LLMModelInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for one persisted LLM model record."""

    id: int
    name: str
    provider: str
    family: str
    display_name: str
    description: str
    context_window: int
    max_output_tokens: int
    latency_ms: int
    throughput_tokens_per_sec: float
    input_tokens_per_1k: float
    output_tokens_per_1k: float
    pricing_currency: str
    capabilities: list[str]
    temperature_min: float
    temperature_max: float
    top_p_min: float
    top_p_max: float
    top_k_min: int
    top_k_max: int
    released_at: str
    deprecated: bool
    custom_params: dict[str, Any]


class LLMModelTagInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for LLM model/tag relation."""

    id: int
    llm_model_id: int
    tag_id: int
    created_at: datetime
    updated_at: datetime


class LLMModelManager:
    """Query helpers for ``LLMModel``."""

    async def active(self) -> list[LLMModel]:
        return await LLMModel.filter(deprecated=False).order_by("provider", "family", "name", "id")

    async def by_name(self, name: str) -> LLMModel | None:
        return await LLMModel.get_or_none(name=name)

    async def by_provider(self, provider: ModelProvider | str) -> list[LLMModel]:
        """Filter by provider slug until FK ownership relation is introduced."""
        provider_value = _enum_value(provider)
        return await LLMModel.filter(provider=provider_value).order_by("family", "name", "id")

    async def by_family(self, family: ModelFamily | str) -> list[LLMModel]:
        family_value = _enum_value(family)
        return await LLMModel.filter(family=family_value).order_by("provider", "name", "id")

    async def with_context_window(self, minimum_tokens: int) -> list[LLMModel]:
        return await LLMModel.filter(
            deprecated=False,
            context_window__gte=max(0, minimum_tokens),
        ).order_by("-context_window", "provider", "name", "id")

    async def supporting_capability(
        self,
        capability: ModelCapability | str,
    ) -> list[LLMModel]:
        capability_value = _enum_value(capability)
        models_for_capability = await self.active()
        return [
            model for model in models_for_capability if model.supports_capability(capability_value)
        ]


class LLMModel(BaseModel, TimestampMixin):
    """Persistent metadata for one available LLM model."""

    name = fields.CharField(max_length=128, unique=True, db_index=True)
    # Temporary bridge: provider slug stays denormalized here until the
    # explicit Provider↔LLMModel relation todo lands.
    provider = fields.CharField(max_length=64, db_index=True)
    family = fields.CharField(max_length=64, db_index=True)
    display_name = LabelField(max_length=255, db_index=True)
    description = DescriptionField(default="")
    context_window = PositiveIntField(default=8192)
    max_output_tokens = PositiveIntField(default=4096)
    latency_ms = NonNegativeIntField(default=0)
    throughput_tokens_per_sec = NonNegativeFloatField(default=0.0)
    input_tokens_per_1k = NonNegativeFloatField(default=0.0)
    output_tokens_per_1k = NonNegativeFloatField(default=0.0)
    pricing_currency = CurrencyCodeField()
    capabilities = StringListField()
    temperature_min = TemperatureFloatField(default=0.0)
    temperature_max = TemperatureFloatField(default=2.0)
    top_p_min = UnitIntervalFloatField(default=0.0)
    top_p_max = UnitIntervalFloatField(default=1.0)
    top_k_min = NonNegativeIntField(default=0)
    top_k_max = NonNegativeIntField(default=500)
    released_at = fields.CharField(max_length=32, default="")
    deprecated = fields.BooleanField(default=False, db_index=True)
    custom_params = JsonObjectField()

    manager = LLMModelManager()

    class Meta(BaseModel.Meta, TimestampMixin.Meta):
        abstract = False
        table = "llm_model"
        table_description_singular = "LLM Model"
        table_description_plural = "LLM Models"
        ordering = ["provider", "family", "name", "id"]
        indexes = [
            Index(fields=["provider", "family"]),
            Index(fields=["provider", "deprecated"]),
            Index(fields=["family", "deprecated"]),
        ]

    def to_domain(self) -> LLMModelInfo:
        return LLMModelInfo(
            id=self.id,
            name=self.name,
            provider=self.provider,
            family=self.family,
            display_name=self.display_name,
            description=self.description,
            context_window=self.context_window,
            max_output_tokens=self.max_output_tokens,
            latency_ms=self.latency_ms,
            throughput_tokens_per_sec=self.throughput_tokens_per_sec,
            input_tokens_per_1k=self.input_tokens_per_1k,
            output_tokens_per_1k=self.output_tokens_per_1k,
            pricing_currency=self.pricing_currency,
            capabilities=self.capability_values,
            temperature_min=self.temperature_min,
            temperature_max=self.temperature_max,
            top_p_min=self.top_p_min,
            top_p_max=self.top_p_max,
            top_k_min=self.top_k_min,
            top_k_max=self.top_k_max,
            released_at=self.released_at,
            deprecated=self.deprecated,
            custom_params=dict(self.custom_params or {}),
        )

    @classmethod
    def from_domain(cls, info: LLMModelInfo) -> LLMModel:
        return cls(
            name=info.name,
            provider=info.provider,
            family=info.family,
            display_name=info.display_name,
            description=info.description,
            context_window=info.context_window,
            max_output_tokens=info.max_output_tokens,
            latency_ms=info.latency_ms,
            throughput_tokens_per_sec=info.throughput_tokens_per_sec,
            input_tokens_per_1k=info.input_tokens_per_1k,
            output_tokens_per_1k=info.output_tokens_per_1k,
            pricing_currency=info.pricing_currency,
            capabilities=list(info.capabilities),
            temperature_min=info.temperature_min,
            temperature_max=info.temperature_max,
            top_p_min=info.top_p_min,
            top_p_max=info.top_p_max,
            top_k_min=info.top_k_min,
            top_k_max=info.top_k_max,
            released_at=info.released_at,
            deprecated=info.deprecated,
            custom_params=dict(info.custom_params),
        )

    def to_metadata(self) -> ModelMetadata:
        return ModelMetadata(
            id=self.name,
            provider=self.provider_member,
            family=self.family_member,
            display_name=self.display_name,
            context_window=self.context_window,
            max_output_tokens=self.max_output_tokens,
            latency_ms=self.latency_ms,
            throughput_tokens_per_sec=self.throughput_tokens_per_sec,
            pricing=self.pricing,
            capabilities=self.capability_members,
            temperature_range=(self.temperature_min, self.temperature_max),
            top_p_range=(self.top_p_min, self.top_p_max),
            top_k_range=(self.top_k_min, self.top_k_max),
            released_at=self.released_at,
            deprecated=self.deprecated,
            custom_params=dict(self.custom_params or {}),
        )

    @classmethod
    def from_metadata(cls, metadata: ModelMetadata) -> LLMModel:
        pricing = metadata.pricing or ModelPricing(
            input_tokens_per_1k=0.0,
            output_tokens_per_1k=0.0,
        )
        return cls(
            name=metadata.id,
            provider=metadata.provider.value,
            family=metadata.family.value,
            display_name=metadata.display_name,
            description="",
            context_window=metadata.context_window,
            max_output_tokens=metadata.max_output_tokens,
            latency_ms=metadata.latency_ms,
            throughput_tokens_per_sec=metadata.throughput_tokens_per_sec,
            input_tokens_per_1k=pricing.input_tokens_per_1k,
            output_tokens_per_1k=pricing.output_tokens_per_1k,
            pricing_currency=pricing.currency,
            capabilities=[capability.value for capability in metadata.capabilities],
            temperature_min=float(metadata.temperature_range[0]),
            temperature_max=float(metadata.temperature_range[1]),
            top_p_min=float(metadata.top_p_range[0]),
            top_p_max=float(metadata.top_p_range[1]),
            top_k_min=int(metadata.top_k_range[0]),
            top_k_max=int(metadata.top_k_range[1]),
            released_at=metadata.released_at,
            deprecated=metadata.deprecated,
            custom_params=dict(metadata.custom_params or {}),
        )

    @property
    def pricing(self) -> ModelPricing | None:
        if self.input_tokens_per_1k <= 0 and self.output_tokens_per_1k <= 0:
            return None
        return ModelPricing(
            input_tokens_per_1k=self.input_tokens_per_1k,
            output_tokens_per_1k=self.output_tokens_per_1k,
            currency=self.pricing_currency,
        )

    @property
    def provider_member(self) -> ModelProvider:
        member = getattr(ModelProvider, self.provider.upper(), None)
        if isinstance(member, Enum):
            return cast(ModelProvider, member)
        for candidate in ModelProvider:
            if _enum_value(candidate) == self.provider:
                return cast(ModelProvider, candidate)
        raise ValueError(f"Unknown model provider: {self.provider}")

    @property
    def family_member(self) -> ModelFamily:
        return ModelFamily(self.family)

    @property
    def capability_values(self) -> list[str]:
        if not isinstance(self.capabilities, list):
            return []
        return [str(capability) for capability in self.capabilities]

    @property
    def capability_members(self) -> set[ModelCapability]:
        return {ModelCapability(capability) for capability in self.capability_values}

    def supports_capability(self, capability: ModelCapability | str) -> bool:
        capability_value = _enum_value(capability)
        return capability_value in self.capability_values

    def set_capabilities(self, capabilities: list[ModelCapability | str]) -> None:
        normalized = [_enum_value(capability) for capability in capabilities]
        self.capabilities = list(dict.fromkeys(normalized))

    def add_capability(self, capability: ModelCapability | str) -> bool:
        capability_value = _enum_value(capability)
        if self.supports_capability(capability_value):
            return False
        self.capabilities = [*self.capability_values, capability_value]
        return True

    def remove_capability(self, capability: ModelCapability | str) -> bool:
        capability_value = _enum_value(capability)
        if not self.supports_capability(capability_value):
            return False
        self.capabilities = [
            existing
            for existing in self.capability_values
            if existing != capability_value
        ]
        return True

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.pricing
        if pricing is None:
            return 0.0
        input_cost = (max(0, input_tokens) / 1000) * pricing.input_tokens_per_1k
        output_cost = (max(0, output_tokens) / 1000) * pricing.output_tokens_per_1k
        return input_cost + output_cost

    def validate_parameters(self, **kwargs: float | int) -> dict[str, str]:
        errors: dict[str, str] = {}

        if "temperature" in kwargs:
            temperature = float(kwargs["temperature"])
            if not self.temperature_min <= temperature <= self.temperature_max:
                errors["temperature"] = (
                    f"Must be between {self.temperature_min} and {self.temperature_max}"
                )

        if "top_p" in kwargs:
            top_p = float(kwargs["top_p"])
            if not self.top_p_min <= top_p <= self.top_p_max:
                errors["top_p"] = f"Must be between {self.top_p_min} and {self.top_p_max}"

        if "top_k" in kwargs:
            top_k = int(kwargs["top_k"])
            if not self.top_k_min <= top_k <= self.top_k_max:
                errors["top_k"] = f"Must be between {self.top_k_min} and {self.top_k_max}"

        if "max_tokens" in kwargs:
            max_tokens = int(kwargs["max_tokens"])
            if max_tokens > self.max_output_tokens:
                errors["max_tokens"] = f"Cannot exceed {self.max_output_tokens}"

        return errors


class LLMModelTag(BaseModel, TimestampMixin):
    """M2M junction table linking LLMModel to Tag."""

    llm_model = fields.ForeignKeyField(
        "models.LLMModel",
        related_name="tags_m2m",
    )
    tag = fields.ForeignKeyField(
        "models.Tag",
        related_name="llm_models",
    )

    def to_domain(self) -> LLMModelTagInfo:
        llm_model_id = cast(int, getattr(self, "llm_model_id"))
        tag_id = cast(int, getattr(self, "tag_id"))
        return LLMModelTagInfo(
            id=self.id,
            llm_model_id=llm_model_id,
            tag_id=tag_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: LLMModelTagInfo) -> "LLMModelTag":
        return cls(
            llm_model_id=info.llm_model_id,
            tag_id=info.tag_id,
            created_at=info.created_at,
            updated_at=info.updated_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "llm_model_tag"
        table_verbose = "LLM Model Tag"
        table_verbose_plural = "LLM Model Tags"
        unique_together = (
            ("llm_model", "tag"),
        )
        indexes = (
            Index(fields=["llm_model_id", "tag_id"]),
            Index(fields=["tag_id", "llm_model_id"]),
        )
