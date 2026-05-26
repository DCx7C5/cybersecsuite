"""Navigation menu ORM model and query helpers."""

from typing import override
import msgspec
from tortoise import fields
from tortoise.fields import IntField
from tortoise.indexes import Index

from css.core.db.fields import LabelField, PathField, UrlField

from .base import BaseTreeModel


class MenuItemInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for one menu node."""

    id: int
    parent_id: int | None
    name: str
    url: str
    icon_path: str
    icon_url: str | None
    order: int


class MenuItemManager:
    """Query helpers for ``MenuItem`` tree operations."""

    async def roots(self) -> list[MenuItem]:
        return await MenuItem.filter(parent_id=None).order_by("order", "id")

    async def children_of(self, parent_id: int) -> list["MenuItem"]:
        return await MenuItem.filter(parent_id=parent_id).order_by("order", "id")

    async def by_url(self, url: str) -> MenuItem | None:
        return await MenuItem.get_or_none(url=url)

    async def next_order(self, parent_id: int | None) -> int:
        sibling = await MenuItem.filter(parent_id=parent_id).order_by("-order", "-id").first()
        if sibling is None:
            return 0
        return int(sibling.order) + 1

    async def create_item(
        self,
        *,
        name: str,
        url: str = "",
        icon_path: str = "",
        icon_url: str | None = None,
        parent_id: int | None = None,
        order: int | None = None,
    ) -> "MenuItem":
        resolved_order = await self.next_order(parent_id) if order is None else order
        return await MenuItem.create(
            name=name,
            url=url,
            icon_path=icon_path,
            icon_url=icon_url,
            parent_id=parent_id,
            order=resolved_order,
        )


class MenuItem(BaseTreeModel):
    """Hierarchical menu item for nested navigation trees."""

    parent = fields.ForeignKeyField(
        "models.MenuItem",
        on_delete=fields.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    name = LabelField(max_length=64, db_index=True)
    url = PathField(max_length=256, default="", db_index=True)
    icon_path = PathField(max_length=256, default="")
    icon_url = UrlField(max_length=256, null=True)
    order = IntField(default=0, db_index=True)
    menu_id = LabelField(max_length=12, null=True, db_index=True)

    manager = MenuItemManager()

    def to_domain(self) -> MenuItemInfo:
        """Convert ORM record to an immutable menu value object."""

        return MenuItemInfo(
            id=self.id,
            parent_id=self.parent_id,
            name=self.name,
            url=self.url,
            icon_path=self.icon_path,
            icon_url=self.icon_url,
            order=self.order,
        )

    @classmethod
    def from_domain(cls, info: MenuItemInfo) -> MenuItem:
        """Create an ORM instance from a menu value object."""

        return cls(
            name=info.name,
            url=info.url,
            icon_path=info.icon_path,
            icon_url=info.icon_url,
            parent_id=info.parent_id,
            order=info.order,
        )

    @property
    def has_icon(self) -> bool:
        """Whether the item has any icon source configured."""

        return bool(self.icon_url or self.icon_path)

    @property
    def icon(self) -> str | None:
        """Preferred icon source, URL first and path second."""

        return self.icon_url or self.icon_path or None

    @property
    def has_destination(self) -> bool:
        """Whether the item points somewhere navigable."""

        return bool(self.url)

    @property
    def is_external(self) -> bool:
        """Whether the destination is an absolute HTTP(S) URL."""

        return self.url.startswith(("http://", "https://"))

    @override
    async def ordered_children(self) -> list[MenuItem]:
        """Load direct children in stable display order."""

        return await type(self).filter(parent_id=self.id).order_by("order", "id")

    @override
    async def siblings(self, *, include_self: bool = False) -> list[MenuItem]:
        """Load sibling menu items in display order."""

        items = await type(self).filter(parent_id=self.parent_id).order_by("order", "id")
        if include_self:
            return items
        return [item for item in items if item.id != self.id]

    async def move(
        self,
        *,
        parent_id: int | None = None,
        order: int | None = None,
    ) -> None:
        """Move this node to a new parent and/or display position."""

        self.parent_id = parent_id
        self.order = (
            await type(self).manager.next_order(parent_id)
            if order is None
            else order
        )
        await self.save(update_fields=["parent_id", "order"])

    async def resequence_children(self) -> None:
        """Normalize child ordering to a dense 0..N-1 sequence."""

        children = await self.ordered_children()
        for idx, child in enumerate(children):
            if child.order == idx:
                continue
            child.order = idx
            await child.save(update_fields=["order"])

    async def breadcrumb(self) -> list[MenuItem]:
        """Return root-to-self breadcrumb items."""

        trail = [self]
        current = self
        while current.parent_id is not None:
            parent = await type(self).get_or_none(id=current.parent_id)
            if parent is None:
                break
            trail.append(parent)
            current = parent
        trail.reverse()
        return trail

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "menu_item"
        table_verbose = "Menu Item"
        table_verbose_plural = "Menu Items"
        ordering = ["order", "id"]
        indexes = [
            Index(fields=["url"]),
            Index(fields=["parent_id", "order"]),
        ]


DEFAULT_MENU_ITEMS: list[dict[str, str | int | list[dict[str, str | int]]]] = [
    {"name": "Dashboard", "url": "/", "icon_path": "LayoutDashboard", "order": 0},
    {"name": "Settings", "url": "/settings", "icon_path": "Settings", "order": 1},
    {
        "name": "Marketplace",
        "url": "/marketplace",
        "icon_path": "Store",
        "order": 2,
        "children": [
            {
                "name": "Installed",
                "url": "/marketplace?tab=installed",
                "icon_path": "Store",
                "order": 0,
            },
            {
                "name": "Marketplace",
                "url": "/marketplace?tab=marketplace",
                "icon_path": "Store",
                "order": 1,
            },
            {
                "name": "Agents",
                "url": "/marketplace?tab=marketplace&kind=agent",
                "icon_path": "LayoutDashboard",
                "order": 2,
            },
            {
                "name": "Skills",
                "url": "/marketplace?tab=marketplace&kind=skill",
                "icon_path": "Settings",
                "order": 3,
            },
            {
                "name": "MCPs",
                "url": "/marketplace?tab=marketplace&kind=mcp",
                "icon_path": "Store",
                "order": 4,
            },
            {
                "name": "Workflows",
                "url": "/marketplace?tab=marketplace&kind=workflow",
                "icon_path": "Store",
                "order": 5,
            },
            {
                "name": "Templates",
                "url": "/marketplace?tab=marketplace&kind=template",
                "icon_path": "Store",
                "order": 6,
            },
            {
                "name": "Prompts",
                "url": "/marketplace?tab=marketplace&kind=prompt",
                "icon_path": "Store",
                "order": 7,
            },
            {
                "name": "Teams",
                "url": "/marketplace?tab=marketplace&kind=team",
                "icon_path": "Store",
                "order": 8,
            },
        ],
    },
    {"name": "Chat", "url": "/chat", "icon_path": "MessageSquare", "order": 3},
]


async def sync_default_menu_items() -> list[MenuItem]:
    """Seed on empty table and keep known navigation items up-to-date."""
    existing = await MenuItem.all().order_by("order", "id")

    async def upsert_item(
        *,
        parent_id: int | None,
        name: str,
        url: str,
        icon_path: str,
        order: int,
    ) -> MenuItem:
        current = next(
            (
                item
                for item in existing
                if item.parent_id == parent_id and item.name == name
            ),
            None,
        )
        if current is None:
            current = await MenuItem.create(
                name=name,
                url=url,
                icon_path=icon_path,
                parent_id=parent_id,
                order=order,
            )
            existing.append(current)
            return current
        await current.save_changes(
            name=name,
            url=url,
            icon_path=icon_path,
            order=order,
            parent_id=parent_id,
        )
        return current

    for entry in DEFAULT_MENU_ITEMS:
        name = str(entry["name"])
        url = str(entry["url"])
        icon_path = str(entry["icon_path"])
        order = int(entry["order"])
        root = await upsert_item(
            parent_id=None,
            name=name,
            url=url,
            icon_path=icon_path,
            order=order,
        )
        children = entry.get("children")
        if not isinstance(children, list):
            continue
        for child in children:
            await upsert_item(
                parent_id=int(root.id),
                name=str(child["name"]),
                url=str(child["url"]),
                icon_path=str(child["icon_path"]),
                order=int(child["order"]),
            )

    return await MenuItem.manager.roots()
