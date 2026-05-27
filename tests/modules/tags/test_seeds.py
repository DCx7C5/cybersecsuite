import pytest

from css.modules.tags.enums import TagColor
from css.modules.tags.seeds import DEFAULT_SYSTEM_TAGS, seed_default_tags


class _FakeTag:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeTagManager:
    def __init__(self) -> None:
        self.by_slug: dict[str, _FakeTag] = {}
        self.created_names: list[str] = []

    async def get_tag_by_slug(self, slug: str) -> _FakeTag | None:
        return self.by_slug.get(slug)

    async def create_tag(self, name: str, color: TagColor, description: str) -> _FakeTag:
        tag = _FakeTag(name=name)
        self.by_slug[name.lower().replace(" ", "-")] = tag
        self.created_names.append(name)
        return tag


def test_default_system_tags_contract() -> None:
    assert len(DEFAULT_SYSTEM_TAGS) >= 1
    for name, color, description in DEFAULT_SYSTEM_TAGS:
        assert isinstance(name, str) and name
        assert isinstance(color, TagColor)
        assert isinstance(description, str) and description


@pytest.mark.asyncio
async def test_seed_default_tags_is_idempotent() -> None:
    manager = _FakeTagManager()

    created_first = await seed_default_tags(manager)
    created_second = await seed_default_tags(manager)

    assert len(created_first) == len(DEFAULT_SYSTEM_TAGS)
    assert len(created_second) == 0
    assert len(manager.created_names) == len(DEFAULT_SYSTEM_TAGS)
