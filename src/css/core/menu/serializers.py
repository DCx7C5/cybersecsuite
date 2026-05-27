"""Serializers for the menu module.

Replaces the inline ``serialize(item)`` async closure in ``endpoints.py``
with a proper ``MenuItemTreeSerializer`` built on ``BaseModelSerializer``.
"""

from typing import override

from css.core.db.serializers import BaseModelSerializer

from css.core.db.models.menu import MenuItem


class MenuItemTreeSerializer(BaseModelSerializer[MenuItem]):
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
    def to_representation(self, instance: MenuItem) -> dict[str, object]:
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
    async def async_to_representation(self, instance: MenuItem) -> dict[str, object]:
        """Recursively serialize item and all its children."""
        base = self.to_representation(instance)
        children = await instance.ordered_children()
        child_ser = MenuItemTreeSerializer()
        base["children"] = [
            await child_ser.async_to_representation(child) for child in children
        ]
        return base


__all__ = ["MenuItemTreeSerializer"]
