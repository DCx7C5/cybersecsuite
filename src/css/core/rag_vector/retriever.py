"""Knowledge retriever — semantic search for LLM agent context."""

import hashlib
from collections.abc import Iterable
from typing import TypeAlias

from css.core.logger import getLogger

logger = getLogger(__name__)

SearchPayload: TypeAlias = dict[str, object]
SearchPayloads: TypeAlias = list[SearchPayload]


class KnowledgeRetriever:
    """Retrieve relevant documents from rag_vector base for agent context."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embedding_model = embedding_model
        self._embedding_cache: dict[str, list[float]] = {}

    @staticmethod
    def _to_float(value: object) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for tag in tags:
            normalized_tag = tag.strip().lower()
            if not normalized_tag or normalized_tag in seen:
                continue
            normalized.append(normalized_tag)
            seen.add(normalized_tag)
        return normalized

    @staticmethod
    def _document_tags(document: object) -> list[str]:
        links = getattr(document, "tag_links", None)
        if links is None:
            return []
        links_iter: Iterable[object]
        try:
            links_iter = iter(links)
        except TypeError:
            return []

        tags: list[str] = []
        seen: set[str] = set()
        for link in links_iter:
            tag_obj = getattr(link, "tag", None)
            tag_name = getattr(tag_obj, "tag", None)
            if not isinstance(tag_name, str):
                continue
            normalized_tag = tag_name.strip().lower()
            if not normalized_tag or normalized_tag in seen:
                continue
            tags.append(normalized_tag)
            seen.add(normalized_tag)
        return tags
    
    async def retrieve(
        self,
        query: str,
        organization_id: int,
        limit: int = 5,
        search_type: str = "keyword",  # keyword, semantic, hybrid
    ) -> SearchPayloads:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: Search query string
            organization_id: Org context
            limit: Max documents to return
            search_type: keyword, semantic, or hybrid
        
        Returns:
            List of document dicts with scores + metadata
        """
        from .models import SearchLog
        
        try:
            if search_type == "keyword":
                results = await self._keyword_search(query, organization_id, limit)
            elif search_type == "semantic":
                results = await self._semantic_search(query, organization_id, limit)
            else:
                # Hybrid: combine both
                kw_results = await self._keyword_search(query, organization_id, limit // 2)
                sem_results = await self._semantic_search(query, organization_id, limit // 2)
                results = self._merge_results(kw_results, sem_results)[:limit]
            
            # Log search for analytics
            matched_ids = [
                result_id
                for result in results
                if isinstance((result_id := result.get("id")), int)
            ]
            await SearchLog.create(
                organization_id=organization_id,
                query=query,
                search_type=search_type,
                matched_documents=matched_ids,
                result_count=len(results),
            )
            
            return results
        
        except Exception as e:
            logger.exception(f"Knowledge retrieval failed: {e}")
            return []
    
    async def _keyword_search(self, query: str, org_id: int, limit: int) -> SearchPayloads:
        """Keyword-based search using inverted index."""
        from .models import KnowledgeIndex
        
        # Tokenize query
        terms = query.lower().split()
        
        # Find documents matching any term
        matching_docs: dict[int, SearchPayload] = {}
        for term in terms:
            entries = await KnowledgeIndex.filter(
                term__startswith=term[:3],
                document__organization_id=org_id,
                document__status="published",
            ).select_related("document").prefetch_related("document__tag_links__tag").all()
            
            for entry in entries:
                doc_id = entry.document.id
                if doc_id not in matching_docs:
                    matching_docs[doc_id] = {
                        "id": entry.document.id,
                        "title": entry.document.title,
                        "content": entry.document.content[:500],
                        "document_type": str(entry.document.document_type),
                        "tags": self._document_tags(entry.document),
                        "source": entry.document.source,
                        "score": 0.0,
                        "matched_terms": set(),
                    }
                
                existing = matching_docs[doc_id]
                existing["score"] = self._to_float(existing.get("score")) + (entry.frequency * 0.1)
                matched_terms = existing.get("matched_terms")
                if isinstance(matched_terms, set):
                    matched_terms.add(term)
                else:
                    existing["matched_terms"] = {term}
        
        # Sort by score
        results: SearchPayloads = sorted(
            matching_docs.values(),
            key=lambda result: self._to_float(result.get("score")),
            reverse=True,
        )
        
        # Clean up sets for JSON serialization
        for result in results:
            matched_terms = result.get("matched_terms")
            if isinstance(matched_terms, set):
                result["matched_terms"] = [
                    term for term in matched_terms if isinstance(term, str)
                ]
        
        return results[:limit]
    
    async def _semantic_search(self, query: str, org_id: int, limit: int) -> SearchPayloads:
        """Semantic search using embeddings (placeholder)."""
        from .models import KnowledgeDocument
        
        # stub: pgvector nearest-neighbour query — see tracker 'pgvector-retriever-impl'
        # For now, return top documents by relevance_score
        docs = await KnowledgeDocument.filter(
            organization_id=org_id,
            status="published",
        ).prefetch_related("tag_links__tag").order_by("-relevance_score").limit(limit).all()
        
        return [
            {
                "id": d.id,
                "title": d.title,
                "content": d.content[:500],
                "document_type": str(d.document_type),
                "tags": self._document_tags(d),
                "source": d.source,
                "score": float(d.relevance_score),
            }
            for d in docs
        ]
    
    def _merge_results(self, kw_results: SearchPayloads, sem_results: SearchPayloads) -> SearchPayloads:
        """Merge keyword and semantic results, deduplicating by doc ID."""
        merged: dict[int, SearchPayload] = {}
        
        for result in kw_results:
            doc_id = result.get("id")
            if not isinstance(doc_id, int):
                continue
            keyword_score = self._to_float(result.get("score"))
            merged[doc_id] = {
                **result,
                "keyword_score": keyword_score,
                "score": keyword_score,
            }
        
        for result in sem_results:
            doc_id = result.get("id")
            if not isinstance(doc_id, int):
                continue
            semantic_score = self._to_float(result.get("score"))
            if doc_id in merged:
                merged[doc_id]["semantic_score"] = semantic_score
                # Average scores
                merged[doc_id]["score"] = (
                    self._to_float(merged[doc_id].get("keyword_score")) +
                    semantic_score
                ) / 2
            else:
                merged[doc_id] = {
                    **result,
                    "semantic_score": semantic_score,
                    "score": semantic_score,
                }
        
        return sorted(
            merged.values(),
            key=lambda result: self._to_float(result.get("score")),
            reverse=True,
        )
    
    async def ingest_document(
        self,
        organization_id: int,
        title: str,
        content: str,
        document_type: str,
        source: str,
        tags: list[str],
        created_by: str = "system",
    ) -> dict[str, object]:
        """Ingest new document into rag_vector base."""
        from .enums import TagCategory
        from .models import KnowledgeDocument, KnowledgeDocumentTag, KnowledgeIndex, KnowledgeTag
        
        try:
            # Calculate content hash for deduplication
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check if duplicate exists
            existing = await KnowledgeDocument.get_or_none(
                organization_id=organization_id,
                content_hash=content_hash,
                status="published",
            )
            if existing:
                logger.info(f"Document already exists (hash: {content_hash})")
                return {"status": "duplicate", "document_id": existing.id}
            
            # Create document
            document = await KnowledgeDocument.create(
                organization_id=organization_id,
                title=title,
                content=content,
                document_type=document_type,
                source=source,
                created_by=created_by,
                content_hash=content_hash,
                status="published",
            )

            normalized_tags = self._normalize_tags(tags)
            for tag_name in normalized_tags:
                tag, created = await KnowledgeTag.get_or_create(
                    organization_id=organization_id,
                    tag=tag_name,
                    defaults={
                        "category": TagCategory.CUSTOM,
                        "usage_count": 0,
                    },
                )
                if created:
                    tag.usage_count = 1
                else:
                    tag.usage_count += 1
                await tag.save()
                await KnowledgeDocumentTag.get_or_create(
                    document_id=document.id,
                    tag_id=tag.id,
                )
            
            # Index content (simple tokenization)
            terms = content.lower().split()
            term_freq: dict[str, int] = {}
            for term in terms:
                if len(term) > 3:  # Skip short words
                    term_freq[term] = term_freq.get(term, 0) + 1
            
            for term, freq in list(term_freq.items())[:100]:  # Limit to top 100 terms
                await KnowledgeIndex.create(
                    document_id=document.id,
                    term=term[:128],
                    frequency=freq,
                )
            
            logger.info(f"Ingested document {document.id}: {title}")
            return {"status": "created", "document_id": document.id}
        
        except Exception as e:
            logger.exception(f"Document ingestion failed: {e}")
            return {"status": "failed", "error": str(e)}


__all__ = ["KnowledgeRetriever"]
