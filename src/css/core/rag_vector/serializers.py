"""Serializers for the rag_vector knowledge-base module.

Replaces the standalone ``_serialize_document`` and ``_serialize_search_result``
helpers in ``endpoints.py`` with proper serializer classes that follow the
``BaseModelSerializer`` / ``BaseSerializer`` contract.
"""

from typing import Any, override

from css.core.db.serializers import BaseModelSerializer, BaseSerializer

from .models import KnowledgeDocument


def _normalize_tag(tag: str) -> str:
    return tag.strip().lower()


class KnowledgeDocumentSerializer(BaseModelSerializer[KnowledgeDocument]):
    """Serializes a ``KnowledgeDocument`` ORM instance.

    Use ``async_to_representation`` (via ``async_data()``) to ensure
    ``tag_links__tag`` relations are prefetched before the dict is built.
    Sync ``to_representation`` omits tags — it is only used when the
    caller already holds prefetched data or does not need tags.
    """

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = KnowledgeDocument
        fields = (
            "id",
            "title",
            "document_type",
            "source",
            "cve_ids",
            "status",
            "version",
            "created_at",
            "updated_at",
        )
        exclude: tuple[str, ...] = ()
        read_only_fields = ("id", "created_at", "updated_at")

    @override
    def to_representation(self, instance: KnowledgeDocument) -> dict[str, Any]:
        base = super().to_representation(instance)
        base["document_type"] = str(base.get("document_type", ""))
        base["status"] = str(base.get("status", ""))
        raw_cve = base.get("cve_ids")
        base["cve_ids"] = [str(c) for c in raw_cve if isinstance(c, str)] if isinstance(raw_cve, list) else []
        base["tags"] = []
        return base

    @override
    async def async_to_representation(self, instance: KnowledgeDocument) -> dict[str, Any]:
        """Fetch related tags then build the full dict."""
        await instance.fetch_related("tag_links__tag")
        base = self.to_representation(instance)

        tag_values: list[str] = []
        seen: set[str] = set()
        links = getattr(instance, "tag_links", None)
        links_iter = iter(links) if links is not None else iter([])
        for link in links_iter:
            tag_obj = getattr(link, "tag", None)
            tag_name = getattr(tag_obj, "tag", None)
            if not isinstance(tag_name, str):
                continue
            normalized = _normalize_tag(tag_name)
            if not normalized or normalized in seen:
                continue
            tag_values.append(normalized)
            seen.add(normalized)

        base["tags"] = tag_values
        return base


class SearchResultSerializer(BaseSerializer[dict[str, object]]):
    """Serializes a raw search-result dict returned by ``KnowledgeRetriever``."""

    @override
    def to_representation(self, instance: dict[str, object]) -> dict[str, Any]:
        raw_id = instance.get("id")
        raw_tags = instance.get("tags")
        score_value = instance.get("score")
        return {
            "id": raw_id if isinstance(raw_id, int) else 0,
            "title": str(instance.get("title") or ""),
            "content": str(instance.get("content") or ""),
            "document_type": str(instance.get("document_type") or ""),
            "score": float(score_value) if isinstance(score_value, (int, float)) else 0.0,
            "tags": [t for t in raw_tags if isinstance(t, str)] if isinstance(raw_tags, list) else [],
            "source": str(instance.get("source") or ""),
        }


__all__ = [
    "KnowledgeDocumentSerializer",
    "SearchResultSerializer",
]
