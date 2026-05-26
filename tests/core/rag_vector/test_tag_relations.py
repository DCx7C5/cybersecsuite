from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from css.core.rag_vector.endpoints import list_documents
from css.core.rag_vector.retriever import KnowledgeRetriever


class _FakeQuery:
    def __init__(self) -> None:
        self.filters: list[dict[str, object]] = []
        self.prefetch_args: tuple[object, ...] = ()
        self.distinct_called = False

    def filter(self, **kwargs: object) -> "_FakeQuery":
        self.filters.append(kwargs)
        return self

    def distinct(self) -> "_FakeQuery":
        self.distinct_called = True
        return self

    def prefetch_related(self, *args: object) -> "_FakeQuery":
        self.prefetch_args = args
        return self

    def order_by(self, *_args: object) -> "_FakeQuery":
        return self

    def limit(self, _value: int) -> "_FakeQuery":
        return self

    async def all(self) -> list[object]:
        return []


class TestRagTagRelations:
    def test_document_tags_extracts_normalized_relation_values(self) -> None:
        retriever = KnowledgeRetriever()
        doc = SimpleNamespace(
            tag_links=[
                SimpleNamespace(tag=SimpleNamespace(tag="  CVE-2026-1234 ")),
                SimpleNamespace(tag=SimpleNamespace(tag="cve-2026-1234")),
                SimpleNamespace(tag=SimpleNamespace(tag="Malware")),
            ]
        )
        tags = retriever._document_tags(doc)
        assert tags == ["cve-2026-1234", "malware"]

    @pytest.mark.asyncio
    async def test_ingest_document_creates_tag_fk_associations(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        retriever = KnowledgeRetriever()

        document = SimpleNamespace(id=77)
        monkeypatch.setattr(
            "css.core.rag_vector.models.KnowledgeDocument.get_or_none",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "css.core.rag_vector.models.KnowledgeDocument.create",
            AsyncMock(return_value=document),
        )
        monkeypatch.setattr(
            "css.core.rag_vector.models.KnowledgeIndex.create",
            AsyncMock(return_value=None),
        )

        tag_a = SimpleNamespace(id=1, usage_count=0, save=AsyncMock(return_value=None))
        tag_b = SimpleNamespace(id=2, usage_count=3, save=AsyncMock(return_value=None))
        get_or_create_tag = AsyncMock(side_effect=[(tag_a, True), (tag_b, False)])
        monkeypatch.setattr(
            "css.core.rag_vector.models.KnowledgeTag.get_or_create",
            get_or_create_tag,
        )
        link_create = AsyncMock(return_value=(SimpleNamespace(), True))
        monkeypatch.setattr(
            "css.core.rag_vector.models.KnowledgeDocumentTag.get_or_create",
            link_create,
        )

        result = await retriever.ingest_document(
            organization_id=5,
            title="Doc",
            content="alpha beta gamma delta epsilon",
            document_type="playbook",
            source="internal",
            tags=["CVE-2026-1234", "cve-2026-1234", " malware ", ""],
            created_by="tester",
        )

        assert result["status"] == "created"
        assert get_or_create_tag.await_count == 2
        link_create.assert_any_await(document_id=77, tag_id=1)
        link_create.assert_any_await(document_id=77, tag_id=2)
        assert tag_a.usage_count == 1
        assert tag_b.usage_count == 4
        tag_a.save.assert_awaited_once()
        tag_b.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_documents_filters_by_tag_fk_relation(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        query = _FakeQuery()

        def _filter(**kwargs: object) -> _FakeQuery:
            query.filters.append(kwargs)
            return query

        monkeypatch.setattr("css.core.rag_vector.endpoints.KnowledgeDocument.filter", _filter)

        response = await list_documents(org_id=42, tag=" CVE-2026-1234 ")

        assert response == []
        assert {"organization_id": 42} in query.filters
        assert {"tag_links__tag__tag": "cve-2026-1234"} in query.filters
        assert query.distinct_called
        assert query.prefetch_args == ("tag_links__tag",)
