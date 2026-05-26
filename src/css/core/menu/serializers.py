"""Serializers for the menu module.

Replaces the inline ``serialize(item)`` async closure in ``endpoints.py``
with a proper ``MenuItemSerializer`` built on ``BaseModelSerializer``.
"""

from typing import Any, override

from css.core.types.base_serializer import BaseModelSerializer

from css.core.db.models.menu import MenuItem


class MenuItemSerializer(BaseModelSerializer[MenuItem]):
    """Serializes a ``MenuItem`` ORM instance to a nested response dict.

    The ``async_to_representation`` method fetches direct children recursively
    so a full subtree can be serialized in a single call.
    """

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = MenuItem
        fields = ("id", "parent_id", "menu_id", "name", "url", "icon_path", "icon_url", "order")
        exclude: tuple[str, ...] = ()
        read_only_fields = ("id",)

    @override
    def to_representation(self, instance: MenuItem) -> dict[str, Any]:
        return {
            "id": int(instance.id),
            "parent_id": instance.parent_id,
            "menu_id": instance.menu_id,
            "name": instance.name,
            "url": instance.url,
            "icon_path": instance.icon_path,
            "icon_url": instance.icon_url,
            "order": int(instance.order),
            "children": [],
        }

    @override
    async def async_to_representation(self, instance: MenuItem) -> dict[str, Any]:
        """Recursively serialize item and all its children."""
        base = self.to_representation(instance)
        children = await instance.ordered_children()
        child_ser = MenuItemSerializer()
        base["children"] = [
            await child_ser.async_to_representation(child) for child in children
        ]
        return base


__all__ = ["MenuItemSerializer"]
