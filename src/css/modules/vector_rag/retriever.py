"""Knowledge retriever — semantic search for LLM agent context."""

from css.core.logger import getLogger
import hashlib
from typing import List, Dict

logger = getLogger(__name__)


class KnowledgeRetriever:
    """Retrieve relevant documents from vector_rag base for agent context."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embedding_model = embedding_model
        self._embedding_cache = {}
    
    async def retrieve(
        self,
        query: str,
        organization_id: int,
        limit: int = 5,
        search_type: str = "keyword",  # keyword, semantic, hybrid
    ) -> List[Dict]:
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
            matched_ids = [r["id"] for r in results]
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
    
    async def _keyword_search(self, query: str, org_id: int, limit: int) -> List[Dict]:
        """Keyword-based search using inverted index."""
        from .models import KnowledgeIndex
        
        # Tokenize query
        terms = query.lower().split()
        
        # Find documents matching any term
        matching_docs = {}
        for term in terms:
            entries = await KnowledgeIndex.filter(
                term__startswith=term[:3],
                document__organization_id=org_id,
                document__status="published",
            ).select_related("document").all()
            
            for entry in entries:
                doc_id = entry.document.id
                if doc_id not in matching_docs:
                    matching_docs[doc_id] = {
                        "id": entry.document.id,
                        "title": entry.document.title,
                        "content": entry.document.content[:500],
                        "document_type": entry.document.document_type,
                        "tags": entry.document.tags,
                        "source": entry.document.source,
                        "score": 0.0,
                        "matched_terms": set(),
                    }
                
                matching_docs[doc_id]["score"] += entry.frequency * 0.1
                matching_docs[doc_id]["matched_terms"].add(term)
        
        # Sort by score
        results = sorted(matching_docs.values(), key=lambda x: x["score"], reverse=True)
        
        # Clean up sets for JSON serialization
        for r in results:
            r["matched_terms"] = list(r["matched_terms"])
        
        return results[:limit]
    
    async def _semantic_search(self, query: str, org_id: int, limit: int) -> List[Dict]:
        """Semantic search using embeddings (placeholder)."""
        from .models import KnowledgeDocument
        
        # TODO: Implement actual vector search with pgvector
        # For now, return top documents by relevance_score
        docs = await KnowledgeDocument.filter(
            organization_id=org_id,
            status="published",
        ).order_by("-relevance_score").limit(limit).all()
        
        return [
            {
                "id": d.id,
                "title": d.title,
                "content": d.content[:500],
                "document_type": d.document_type,
                "tags": d.tags,
                "source": d.source,
                "score": d.relevance_score,
            }
            for d in docs
        ]
    
    def _merge_results(self, kw_results: List[Dict], sem_results: List[Dict]) -> List[Dict]:
        """Merge keyword and semantic results, deduplicating by doc ID."""
        merged = {}
        
        for r in kw_results:
            merged[r["id"]] = {**r, "keyword_score": r.get("score", 0.0), "score": 0}
        
        for r in sem_results:
            if r["id"] in merged:
                merged[r["id"]]["semantic_score"] = r.get("score", 0.0)
                # Average scores
                merged[r["id"]]["score"] = (
                    merged[r["id"]].get("keyword_score", 0.0) +
                    r.get("score", 0.0)
                ) / 2
            else:
                merged[r["id"]] = {**r, "semantic_score": r.get("score", 0.0)}
        
        return sorted(merged.values(), key=lambda x: x.get("score", 0), reverse=True)
    
    async def ingest_document(
        self,
        organization_id: int,
        title: str,
        content: str,
        document_type: str,
        source: str,
        tags: List[str],
        created_by: str = "system",
    ) -> Dict:
        """Ingest new document into vector_rag base."""
        from .models import KnowledgeDocument, KnowledgeIndex
        
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
                tags=tags,
                created_by=created_by,
                content_hash=content_hash,
                status="published",
            )
            
            # Index content (simple tokenization)
            terms = content.lower().split()
            term_freq = {}
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
