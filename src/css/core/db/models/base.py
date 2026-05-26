"""Shared abstract base model for Tortoise ORM entities."""

from typing import Any

from tortoise.fields import BigIntField
from tortoise.models import Model

from ..fields import NameField


class BaseModel(Model):
    """Canonical ORM base class for the project."""

    id = BigIntField(primary_key=True)

    @property
    def pk(self) -> int:
        """Typed primary-key accessor."""

        return int(self.id)

    @property
    def persisted(self) -> bool:
        """Whether this record has a database identity."""

        return getattr(self, "id", None) is not None

    def snapshot(self, *field_names: str) -> dict[str, Any]:
        """Return a shallow field snapshot for logging or event metadata."""

        names = field_names or tuple(self._meta.fields_map.keys())
        return {
            name: getattr(self, name)
            for name in names
            if hasattr(self, name)
        }

    def apply_updates(self, **changes: Any) -> list[str]:
        """Apply attribute updates and return the changed field names."""

        changed_fields: list[str] = []
        for field_name, value in changes.items():
            if not hasattr(self, field_name):
                raise AttributeError(f"{type(self).__name__} has no field {field_name!r}")
            if getattr(self, field_name) == value:
                continue
            setattr(self, field_name, value)
            changed_fields.append(field_name)
        return changed_fields

    async def save_changes(self, **changes: Any) -> list[str]:
        """Apply field changes and persist only the fields that actually changed."""

        changed_fields = self.apply_updates(**changes)
        if changed_fields:
            await self.save(update_fields=changed_fields)
        return changed_fields

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class BaseUserModel(BaseModel):
    """Abstract base model for user-related entities."""

    username = NameField(max_length=128, unique=True, db_index=True)

    @property
    def username_key(self) -> str:
        """Normalized identifier used in logs and caches."""

        return str(self.username).strip().lower()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class BaseTreeModel(BaseModel):
    """Abstract base model for hierarchical (tree) entities."""

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True
        ordering = ["id"]

    @property
    def is_root(self) -> bool:
        """Whether this node has no parent."""

        return self.parent_id is None

    async def ordered_children(self) -> list["BaseTreeModel"]:
        """Load direct children in stable tree order."""

        return await type(self).filter(parent_id=self.id).order_by("id")

    async def siblings(self, *, include_self: bool = False) -> list["BaseTreeModel"]:
        """Load sibling tree nodes."""

        nodes = await type(self).filter(parent_id=self.parent_id).order_by("id")
        if include_self:
            return nodes
        return [node for node in nodes if node.id != self.id]

    async def reparent(self, parent_id: int | None) -> None:
        """Move this node under a different parent."""

        await self.save_changes(parent_id=parent_id)
