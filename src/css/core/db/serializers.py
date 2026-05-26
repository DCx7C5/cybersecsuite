"""Base serializer classes — Django REST Framework pattern adapted for
FastAPI + Tortoise ORM + msgspec.

Three classes cover the serialization layer:

* ``BaseSerializer``      — generic validation and representation for arbitrary data.
* ``BaseModelSerializer`` — field-auto-mapping for Tortoise ORM models.
* ``BaseListSerializer``  — collection wrapper that delegates to a child serializer.

Usage::

    # Model serializer — auto-maps ORM fields
    class AgentSerializer(BaseModelSerializer[AgentModel]):
        class Meta:
            model = AgentModel
            fields = "__all__"
            read_only_fields = ("id", "created_at")

    # Serialize a single ORM instance to dict
    result = AgentSerializer(instance=agent).data

    # Serialize with async related fetches
    result = await AgentSerializer(instance=agent).async_data()

    # Deserialize and persist
    ser = AgentSerializer(data=request_payload)
    if ser.is_valid():
        saved = await ser.async_save()

    # Collection serializer
    ser = BaseListSerializer(child=AgentSerializer(), instance=agents)
    result = ser.data   # list[dict[str, Any]]
"""

from datetime import date, datetime
from typing import Any, Generic, TypeVar, override

import msgspec
from tortoise.models import Model

from css.core.exceptions import BaseCoreException

M = TypeVar("M", bound=Model)
T = TypeVar("T")


class SerializerValidationError(BaseCoreException):
    """Raised when serializer field or object validation fails."""

    def __init__(self, errors: dict[str, list[str]]) -> None:
        self.errors = errors
        super().__init__(str(errors))


class BaseSerializer(Generic[T]):
    """Core serializer — validates and transforms arbitrary data.

    Follows the Django REST Framework ``Serializer`` contract, adapted for
    this async-first msgspec/Tortoise stack:

    - **Output**: ``data`` / ``async_data()`` → ``dict[str, Any]``
    - **Input**: ``to_internal_value()`` + ``validate()`` → ``validated_data``
    - **Persist**: ``async_save()`` dispatches to ``async_create`` or ``async_update``

    Override ``to_representation`` for custom sync output, or
    ``async_to_representation`` for output that requires awaiting related records.

    Override ``to_internal_value`` and/or ``validate_<field>`` methods (by
    convention) for input validation before the ``validate()`` cross-field hook.
    """

    def __init__(
        self,
        instance: T | None = None,
        data: dict[str, Any] | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.instance = instance
        self.initial_data = data
        self.context: dict[str, Any] = context or {}
        self._errors: dict[str, list[str]] = {}
        self._validated_data: dict[str, Any] | None = None

    # ── Output ────────────────────────────────────────────────────────────────

    @property
    def data(self) -> dict[str, Any]:
        """Serialized representation of ``instance`` (sync)."""
        if self.instance is None:
            return {}
        return self.to_representation(self.instance)

    async def async_data(self) -> dict[str, Any]:
        """Serialized representation of ``instance`` (async — for relation fetches)."""
        if self.instance is None:
            return {}
        return await self.async_to_representation(self.instance)

    def to_representation(self, instance: T) -> dict[str, Any]:
        """Convert ``instance`` to a JSON-serializable dict.

        Default: msgspec Structs → ``msgspec.to_builtins``; objects with
        ``__dict__`` → filtered copy; fallback → ``{}``.
        """
        if isinstance(instance, msgspec.Struct):
            return msgspec.to_builtins(instance)  # type: ignore[return-value]
        if hasattr(instance, "__dict__"):
            return {k: v for k, v in instance.__dict__.items() if not k.startswith("_")}
        return {}

    async def async_to_representation(self, instance: T) -> dict[str, Any]:
        """Async output hook — override when related records must be fetched."""
        return self.to_representation(instance)

    # ── Input / validation ────────────────────────────────────────────────────

    @property
    def errors(self) -> dict[str, list[str]]:
        """Validation errors populated by the last ``is_valid()`` call."""
        return self._errors

    @property
    def validated_data(self) -> dict[str, Any]:
        """Validated data dict — only accessible after a successful ``is_valid()``."""
        if self._validated_data is None:
            raise AssertionError(
                "You must call .is_valid() before accessing .validated_data."
            )
        return self._validated_data

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        """Run the full validation pipeline on ``initial_data``.

        Pipeline: ``to_internal_value`` → ``validate`` (cross-field hook).
        Stores errors in ``self.errors`` on failure; sets ``validated_data`` on success.
        """
        if self.initial_data is None:
            self._errors = {"non_field_errors": ["No data provided."]}
            if raise_exception:
                raise SerializerValidationError(self._errors)
            return False

        try:
            value = self.to_internal_value(self.initial_data)
            self._validated_data = self.validate(value)
            self._errors = {}
            return True
        except SerializerValidationError as exc:
            self._errors = exc.errors
            if raise_exception:
                raise
            return False

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize raw incoming data.

        Override to add field-level checks.  Raise ``SerializerValidationError``
        with an ``{"field": ["message"]}`` dict on failure.
        """
        return data

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Object-level validation hook — override for cross-field checks.

        Raise ``SerializerValidationError`` with ``{"non_field_errors": [...]}``
        on failure.
        """
        return data

    # ── Persistence ───────────────────────────────────────────────────────────

    async def async_save(self) -> T:
        """Dispatch to ``async_create`` or ``async_update`` based on ``instance``."""
        if self.instance is not None:
            return await self.async_update(self.instance, self.validated_data)
        return await self.async_create(self.validated_data)

    async def async_create(self, validated_data: dict[str, Any]) -> T:
        """Create a new instance from validated data.  Must be overridden."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement async_create()."
        )

    async def async_update(self, instance: T, validated_data: dict[str, Any]) -> T:
        """Update an existing instance with validated data.  Must be overridden."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement async_update()."
        )


class BaseModelSerializer(BaseSerializer[M]):
    """Tortoise ORM model serializer.

    Automatically generates field representation from the model's
    ``_meta.fields_map``.  Configure via an inner ``Meta`` class::

        class TaskSerializer(BaseModelSerializer[TaskModel]):
            class Meta:
                model = TaskModel
                fields = "__all__"       # or explicit tuple of field names
                exclude = ()             # fields to always omit
                read_only_fields = ("id", "created_at", "updated_at")

    ``Meta.model`` — the concrete Tortoise Model class (required).
    ``Meta.fields`` — ``"__all__"`` or an explicit tuple of field names.
    ``Meta.exclude`` — tuple of field names always omitted from output.
    ``Meta.read_only_fields`` — fields ignored during ``to_internal_value``.

    ``async_to_representation`` is intentionally left for subclasses to override
    when prefetching related records is needed.

    Subclasses must define a nested ``Meta`` class.  Mark it with
    ``# pyright: ignore[reportIncompatibleVariableOverride]`` to suppress the
    type-narrowing false-positive from the inner-class override pattern.
    """

    # ── Meta accessors (avoids TypeVar-in-nested-class limitations) ───────────

    def _meta_model(self) -> type[Model]:
        """Return ``Meta.model`` safely across pyright's generic bounds."""
        return type(self).Meta.model  # type: ignore[attr-defined, return-value]

    def _meta_fields(self) -> str | tuple[str, ...]:
        return getattr(type(self).Meta, "fields", "__all__")  # type: ignore[attr-defined]

    def _meta_exclude(self) -> tuple[str, ...]:
        return getattr(type(self).Meta, "exclude", ())  # type: ignore[attr-defined]

    # ── Field resolution ──────────────────────────────────────────────────────

    def _get_field_names(self) -> tuple[str, ...]:
        """Resolve the active field list from Meta configuration."""
        model = self._meta_model()
        all_model_fields = tuple(model._meta.fields_map.keys())
        spec = self._meta_fields()
        base: tuple[str, ...] = all_model_fields if spec == "__all__" else tuple(spec)  # type: ignore[arg-type]
        excluded = set(self._meta_exclude())
        return tuple(f for f in base if f not in excluded)

    def _serialize_value(self, value: Any) -> Any:
        """Normalize a single field value to a JSON-serializable primitive."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, msgspec.Struct):
            return msgspec.to_builtins(value)  # type: ignore[return-value]
        return value

    # ── Output ────────────────────────────────────────────────────────────────

    @override
    def to_representation(self, instance: M) -> dict[str, Any]:
        """Build a dict of all configured fields from the ORM instance."""
        return {
            name: self._serialize_value(getattr(instance, name, None))
            for name in self._get_field_names()
        }

    # ── Persistence ───────────────────────────────────────────────────────────

    @override
    async def async_create(self, validated_data: dict[str, Any]) -> M:
        """Create a new model instance via ``Meta.model.create()``."""
        return await self._meta_model().create(**validated_data)  # type: ignore[return-value]

    @override
    async def async_update(self, instance: M, validated_data: dict[str, Any]) -> M:
        """Apply updates and persist only changed fields.

        Uses ``BaseModel.save_changes`` when available (preferred — only writes
        fields that actually changed).  Falls back to a full ``save`` on plain
        Tortoise models.
        """
        if hasattr(instance, "save_changes"):
            await instance.save_changes(**validated_data)  # type: ignore[union-attr]
        else:
            for field, value in validated_data.items():
                setattr(instance, field, value)
            await instance.save(update_fields=list(validated_data))
        return instance


class BaseListSerializer(Generic[T]):
    """Serializer for ordered collections.

    Wraps a child ``BaseSerializer`` and applies it element-wise::

        ser = BaseListSerializer(child=AgentSerializer(), instance=agents)
        result = ser.data                    # list[dict[str, Any]]

        # Async variant (relation fetches per item)
        result = await ser.async_data()

    For list deserialization and validation, ``is_valid()`` delegates to the
    child's ``to_internal_value`` for each item.
    """

    def __init__(
        self,
        child: BaseSerializer[T],
        instance: list[T] | None = None,
        data: list[dict[str, Any]] | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.child = child
        self.instance = instance
        self.initial_data = data
        self.context: dict[str, Any] = context or {}
        self._errors: list[dict[str, list[str]]] = []
        self._validated_data: list[dict[str, Any]] | None = None

    # ── Output ────────────────────────────────────────────────────────────────

    @property
    def data(self) -> list[dict[str, Any]]:
        """List of serialized representations (sync)."""
        if self.instance is None:
            return []
        return [self.child.to_representation(item) for item in self.instance]

    async def async_data(self) -> list[dict[str, Any]]:
        """List of serialized representations (async — for relation fetches)."""
        if self.instance is None:
            return []
        results = []
        for item in self.instance:
            results.append(await self.child.async_to_representation(item))
        return results

    # ── Input / validation ────────────────────────────────────────────────────

    @property
    def errors(self) -> list[dict[str, list[str]]]:
        return self._errors

    @property
    def validated_data(self) -> list[dict[str, Any]]:
        if self._validated_data is None:
            raise AssertionError(
                "You must call .is_valid() before accessing .validated_data."
            )
        return self._validated_data

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        """Validate each item in ``initial_data`` using the child serializer."""
        if self.initial_data is None:
            self._errors = [{"non_field_errors": ["No data provided."]}]
            if raise_exception:
                raise SerializerValidationError({"non_field_errors": ["No data provided."]})
            return False

        results: list[dict[str, Any]] = []
        all_errors: list[dict[str, list[str]]] = []

        for item in self.initial_data:
            self.child.initial_data = item
            if self.child.is_valid():
                results.append(self.child.validated_data)
            else:
                all_errors.append(self.child.errors)

        if all_errors:
            self._errors = all_errors
            if raise_exception:
                raise SerializerValidationError(
                    {"items": [str(e) for e in all_errors]}
                )
            return False

        self._validated_data = results
        return True


__all__ = [
    "SerializerValidationError",
    "BaseSerializer",
    "BaseModelSerializer",
    "BaseListSerializer",
]
