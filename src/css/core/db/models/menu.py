"""Navigation menu ORM model and query helpers."""

from typing import NotRequired, TypedDict, cast, override
import msgspec
from tortoise import fields
from tortoise.fields import IntField
from tortoise.indexes import Index
from fastapi import HTTPException

from css.core.db.fields import LabelField, PathField, UrlField

from css.core.db.serializers import BaseModelSerializer
from .base import BaseTreeModel


class MenuItemInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for one menu node."""

    id: int
    menu_id: str | None
    parent_id: int | None
    name: str
    url: str
    icon_path: str
    icon_url: str | None
    order: int


class MenuItemManager:
    """Query helpers for ``MenuItem`` tree operations."""

    async def validate_parent(self, parent_id: int | None, child_menu_id: str | None) -> None:
        """Validate parent before linking, reject self-parenting and cross-menu links.

        Raises:
            HTTPException: If parent_id is invalid or belongs to different menu_id partition
        """
        if parent_id is None:
            return
        if parent_id == 0:  # Invalid ID
            raise HTTPException(status_code=400, detail="Parent ID cannot be zero")

        parent = await MenuItem.get_or_none(id=parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail=f"Parent menu item {parent_id} not found")

        if child_menu_id is not None and parent.menu_id != child_menu_id:
            raise HTTPException(
                status_code=400,
                detail=f"Parent menu_id ({parent.menu_id}) must match child menu_id ({child_menu_id})",
            )

    async def roots(self, menu_id: str | None = None) -> list[MenuItem]:
        query = MenuItem.filter(parent_id=None)
        if menu_id is not None:
            query = query.filter(menu_id=menu_id)
        return await query.order_by("menu_id", "order", "id")

    async def children_of(
        self,
        parent_id: int,
        *,
        menu_id: str | None = None,
    ) -> list[MenuItem]:
        query = MenuItem.filter(parent_id=parent_id)
        if menu_id is not None:
            query = query.filter(menu_id=menu_id)
        return await query.order_by("order", "id")

    async def by_url(self, url: str) -> MenuItem | None:
        return await MenuItem.get_or_none(url=url)

    async def next_order(
        self,
        parent_id: int | None,
        *,
        menu_id: str | None = None,
    ) -> int:
        query = MenuItem.filter(parent_id=parent_id)
        if parent_id is None:
            query = query.filter(menu_id=menu_id)
        sibling = await query.order_by("-order", "-id").first()
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
        menu_id: str | None = None,
        parent_id: int | None = None,
        order: int | None = None,
    ) -> MenuItem:
        # Validate parent exists and shares menu_id partition
        await self.validate_parent(parent_id, menu_id)

        resolved_order = (
            await self.next_order(parent_id, menu_id=menu_id)
            if order is None
            else order
        )
        return await MenuItem.create(
            name=name,
            url=url,
            icon_path=icon_path,
            icon_url=icon_url,
            menu_id=menu_id,
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
            menu_id=self.menu_id,
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
            menu_id=info.menu_id,
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
    async def ordered_children(self) -> list[MenuItem]:  # type: ignore[reportIncompatibleMethodOverride]
        """Load direct children in stable display order."""

        return cast(list[MenuItem], await type(self).filter(parent_id=self.id).order_by("order", "id"))

    @override
    async def siblings(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        include_self: bool = False,
    ) -> list[MenuItem]:
        """Load sibling menu items in display order."""

        items = cast(
            list[MenuItem],
            await type(self).filter(parent_id=self.parent_id).order_by("order", "id"),
        )
        if include_self:
            return items
        return [item for item in items if item.id != self.id]

    async def move(
        self,
        *,
        parent_id: int | None = None,
        order: int | None = None,
    ) -> None:
        """Move this node to a new parent and/or display position.

        Raises:
            HTTPException: If self-parenting or cross-menu_id reparenting is attempted
        """
        # Prevent self-parenting
        if parent_id is not None and parent_id == self.id:
            raise HTTPException(status_code=400, detail="Cannot set a menu item as its own parent")

        # Validate parent exists and shares menu_id partition
        await type(self).manager.validate_parent(parent_id, self.menu_id)

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
        """Return root-to-self breadcrumb items.

        Raises:
            RuntimeError: If a cycle is detected in the tree
        """
        trail = [self]
        current = self
        visited: set[int] = {self.id}

        while current.parent_id is not None:
            if current.parent_id in visited:
                raise RuntimeError(
                    f"Cycle detected in menu tree at item {current.parent_id}: visited={visited}"
                )
            visited.add(current.parent_id)

            parent = await type(self).get_or_none(id=current.parent_id)
            if parent is None:
                break
            trail.append(parent)
            current = parent
        trail.reverse()
        return cast(list[MenuItem], trail)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "menu_item"
        table_verbose = "Menu Item"
        table_verbose_plural = "Menu Items"
        ordering = ["order", "id"]
        indexes = [
            Index(fields=["url"]),
            Index(fields=["menu_id", "parent_id", "order"]),
            Index(fields=["parent_id", "order"]),
        ]


class MenuItemSerializer(BaseModelSerializer[MenuItem]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = MenuItem
        fields = "__all__"
        read_only_fields = ("id",)


class MenuSeedChild(TypedDict):
    name: str
    url: str
    icon_path: str
    order: int
    menu_id: NotRequired[str]


class MenuSeedEntry(TypedDict):
    menu_id: str
    name: str
    url: str
    icon_path: str
    order: int
    children: NotRequired[list[MenuSeedChild]]


DEFAULT_MENU_ITEMS: list[MenuSeedEntry] = [
    {"menu_id": "sidebar", "name": "Dashboard", "url": "/", "icon_path": "LayoutDashboard", "order": 0},
    {"menu_id": "sidebar", "name": "Settings", "url": "/settings", "icon_path": "Settings", "order": 1},
    {
        "menu_id": "sidebar",
        "name": "Marketplace",
        "url": "/marketplace",
        "icon_path": "Store",
        "order": 2,
        "children": [
            {
                "name": "Agents",
                "url": "/marketplace?kind=agent",
                "icon_path": "LayoutDashboard",
                "order": 0,
            },
            {
                "name": "Skills",
                "url": "/marketplace?kind=skill",
                "icon_path": "Settings",
                "order": 1,
            },
            {
                "name": "MCPs",
                "url": "/marketplace?kind=mcp",
                "icon_path": "Store",
                "order": 2,
            },
            {
                "name": "Workflows",
                "url": "/marketplace?kind=workflow",
                "icon_path": "Store",
                "order": 3,
            },
            {
                "name": "Templates",
                "url": "/marketplace?kind=template",
                "icon_path": "Store",
                "order": 4,
            },
            {
                "name": "Prompts",
                "url": "/marketplace?kind=prompt",
                "icon_path": "Store",
                "order": 5,
            },
            {
                "name": "Teams",
                "url": "/marketplace?kind=team",
                "icon_path": "Store",
                "order": 6,
            },
        ],
    },
    {"menu_id": "sidebar", "name": "Chat", "url": "/chat", "icon_path": "MessageSquare", "order": 3},
    {"menu_id": "settings", "name": "General", "url": "/settings", "icon_path": "Settings", "order": 0},
    {"menu_id": "settings", "name": "Account", "url": "/settings/account", "icon_path": "Settings", "order": 1},
    {"menu_id": "topnav", "name": "Dashboard", "url": "/", "icon_path": "LayoutDashboard", "order": 0},
    {"menu_id": "topnav", "name": "Marketplace", "url": "/marketplace", "icon_path": "Store", "order": 1},
    {"menu_id": "topnav", "name": "Chat", "url": "/chat", "icon_path": "MessageSquare", "order": 2},
]


async def sync_default_menu_items() -> list[MenuItem]:
    """Seed on empty table and keep known navigation items up-to-date."""
    existing = await MenuItem.all().order_by("menu_id", "parent_id", "order", "id")

    async def upsert_item(
        *,
        menu_id: str,
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
                if item.menu_id == menu_id and item.parent_id == parent_id and item.name == name
            ),
            None,
        )
        if current is None:
            # Validate parent before creating
            if parent_id is not None:
                parent = await MenuItem.get_or_none(id=parent_id)
                if parent is None:
                    raise HTTPException(status_code=404, detail=f"Parent menu item {parent_id} not found")
                if parent.menu_id != menu_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Parent menu_id ({parent.menu_id}) must match child menu_id ({menu_id})",
                    )
            current = await MenuItem.create(
                name=name,
                url=url,
                icon_path=icon_path,
                menu_id=menu_id,
                parent_id=parent_id,
                order=order,
            )
            existing.append(current)
            return current
        await current.save_changes(
            name=name,
            url=url,
            icon_path=icon_path,
            menu_id=menu_id,
            order=order,
            parent_id=parent_id,
        )
        return current

    # Track which (parent_id, name) pairs should exist as children for cleanup
    canonical_children: dict[tuple[int | None, str], str] = {}

    for entry in DEFAULT_MENU_ITEMS:
        menu_id = str(entry.get("menu_id") or "sidebar")
        name = str(entry["name"])
        url = str(entry["url"])
        icon_path = str(entry["icon_path"])
        order = int(entry["order"])
        root = await upsert_item(
            menu_id=menu_id,
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
            child_menu_id = str(child.get("menu_id") or menu_id)
            canonical_children[(int(root.id), str(child["name"]))] = child_menu_id
            await upsert_item(
                menu_id=child_menu_id,
                parent_id=int(root.id),
                name=str(child["name"]),
                url=str(child["url"]),
                icon_path=str(child["icon_path"]),
                order=int(child["order"]),
            )

    # Clean up orphaned marketplace sidebar children (Installed, nested Marketplace, etc.)
    marketplace_root = next(
        (
            item
            for item in existing
            if item.menu_id == "sidebar" and item.parent_id is None and item.name == "Marketplace"
        ),
        None,
    )
    if marketplace_root is not None:
        orphaned = [
            item
            for item in existing
            if item.parent_id == marketplace_root.id
            and (int(marketplace_root.id), item.name) not in canonical_children
        ]
        for item in orphaned:
            await item.delete()

    # Resequence all parent groups to have dense ordering
    parent_groups: dict[int | None, list[MenuItem]] = {}
    for item in await MenuItem.all():
        key = item.parent_id
        if key not in parent_groups:
            parent_groups[key] = []
        parent_groups[key].append(item)

    for items in parent_groups.values():
        items_sorted = sorted(items, key=lambda x: (x.order, x.id))
        for idx, item in enumerate(items_sorted):
            if item.order != idx:
                item.order = idx
                await item.save(update_fields=["order"])

    return await MenuItem.manager.roots(menu_id="sidebar")
