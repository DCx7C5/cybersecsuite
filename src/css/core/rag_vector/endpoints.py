"""Knowledge base management endpoints."""

import msgspec
from css.core.types.base_endpoint import EndpointModel

from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timezone
from typing import Any
from .models import KnowledgeDocument, KnowledgeTag, SearchLog
from .retriever import KnowledgeRetriever

router = APIRouter(prefix="/api/rag_vector", tags=["rag_vector"])
retriever = KnowledgeRetriever()

# Request/Response Models
class DocumentCreate(EndpointModel, kw_only=True):
    title: str
    content: str
    document_type: str
    source: str
    tags: list[str] = []
    cve_ids: list[str] = []
    relevance_score: float = 0.5

class DocumentResponse(EndpointModel, kw_only=True):
    id: int
    title: str
    document_type: str
    source: str
    tags: list[str]
    cve_ids: list[str]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

class SearchRequest(EndpointModel, kw_only=True):
    query: str
    search_type: str = "keyword"
    limit: int = 5

class SearchResult(EndpointModel, kw_only=True):
    id: int
    title: str
    content: str
    document_type: str
    score: float
    tags: list[str]
    source: str

# Document Management Endpoints
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    req: DocumentCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create rag_vector document."""
    
    try:
        result = await retriever.ingest_document(
            organization_id=org_id,
            title=req.title,
            content=req.content,
            document_type=req.document_type,
            source=req.source,
            tags=req.tags,
        )
        
        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to ingest"))
        
        if result["status"] == "duplicate":
            raise HTTPException(status_code=409, detail="Document already exists (duplicate)")
        
        doc = await KnowledgeDocument.get_by_id(result["document_id"])
        return DocumentResponse(**{f: getattr(doc, f) for f in DocumentResponse.__struct_fields__})
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create document: {str(e)}")

@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    org_id: int = Query(..., description="Organization ID"),
    document_type: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    tag: str | None = None,
    limit: int = Query(50, ge=1, le=500),
):
    """List rag_vector documents."""
    
    query = KnowledgeDocument.filter(organization_id=org_id)
    if document_type:
        query = query.filter(document_type=document_type)
    if status_filter:
        query = query.filter(status=status_filter)
    if tag:
        query = query.filter(tags__contains=tag)
    
    docs = await query.order_by("-updated_at").limit(limit).all()
    return [DocumentResponse(**{f: getattr(d, f) for f in DocumentResponse.__struct_fields__}) for d in docs]

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get document details."""
    
    doc = await KnowledgeDocument.get_or_none(id=doc_id, organization_id=org_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update last_accessed_at
    doc.last_accessed_at = datetime.now(timezone.utc)
    await doc.save()
    
    return DocumentResponse(**{f: getattr(doc, f) for f in DocumentResponse.__struct_fields__})

@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Delete/archive document."""
    
    doc = await KnowledgeDocument.get_or_none(id=doc_id, organization_id=org_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Archive instead of hard delete
    doc.status = "archived"
    await doc.save()

# Search Endpoints
@router.post("/search", response_model=list[SearchResult])
async def search_knowledge(
    req: SearchRequest,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Search rag_vector base.
    
    Supports:
    - keyword: Full-text search on titles and content
    - semantic: Vector-based similarity search (requires embeddings)
    - hybrid: Combination of both methods
    """
    
    try:
        results = await retriever.retrieve(
            query=req.query,
            organization_id=org_id,
            limit=req.limit,
            search_type=req.search_type,
        )
        
        return [SearchResult(**r) for r in results]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")

# Tag Management Endpoints
@router.get("/tags", response_model=list[dict[str, Any]])
async def list_tags(
    org_id: int = Query(..., description="Organization ID"),
    category: str | None = None,
):
    """List rag_vector tags."""
    
    query = KnowledgeTag.filter(organization_id=org_id)
    if category:
        query = query.filter(category=category)
    
    tags = await query.order_by("-usage_count").all()
    return [{"tag": t.tag, "category": t.category, "usage_count": t.usage_count} for t in tags]

@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: str = Query(..., min_length=1, max_length=128),
    category: str = Query("custom", pattern="^(tactic|technique|threat_actor|malware|tool|vulnerability|custom)$"),
    org_id: int = Query(..., description="Organization ID"),
):
    """Create rag_vector tag."""
    
    existing = await KnowledgeTag.get_or_none(organization_id=org_id, tag=tag)
    if existing:
        raise HTTPException(status_code=409, detail="Tag already exists")
    
    try:
        tag_obj = await KnowledgeTag.create(
            organization_id=org_id,
            tag=tag,
            category=category,
        )
        return {"tag": tag_obj.tag, "category": tag_obj.category}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create tag: {str(e)}")

# Analytics Endpoints
@router.get("/search-log", response_model=list[dict[str, Any]])
async def get_search_log(
    org_id: int = Query(..., description="Organization ID"),
    agent_id: str | None = None,
    limit: int = Query(50, ge=1, le=500),
):
    """Get rag_vector search history for analytics."""
    
    query = SearchLog.filter(organization_id=org_id)
    if agent_id:
        query = query.filter(agent_id=agent_id)
    
    logs = await query.order_by("-searched_at").limit(limit).all()
    return [
        {
            "query": log.query,
            "search_type": log.search_type,
            "result_count": log.result_count,
            "relevance_feedback": log.relevance_feedback,
            "searched_at": log.searched_at,
        }
        for log in logs
    ]

@router.post("/search-feedback")
async def record_search_feedback(
    query: str = Query(...),
    feedback: str = Query(..., pattern="^(relevant|irrelevant|partially_relevant)$"),
    org_id: int = Query(..., description="Organization ID"),
):
    """Record user feedback on search results for ranking improvement."""
    
    try:
        # Find most recent search matching query
        log = await SearchLog.filter(
            organization_id=org_id,
            query=query,
        ).order_by("-searched_at").first()
        
        if not log:
            raise HTTPException(status_code=404, detail="Search log not found")
        
        log.relevance_feedback = feedback
        await log.save()
        
        return {"status": "recorded"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to record feedback: {str(e)}")

__all__ = ["router"]
