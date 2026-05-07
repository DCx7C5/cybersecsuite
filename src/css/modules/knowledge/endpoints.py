"""Knowledge base management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .models import KnowledgeDocument, KnowledgeTag, SearchLog, DocumentType, DocumentStatus
from .retriever import KnowledgeRetriever

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
retriever = KnowledgeRetriever()


# Request/Response Models
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=1)
    document_type: str = Field(..., regex="^(cve_feed|playbook|threat_report|runbook|incident_retrospective|policy|tool_documentation|vendor_advisory|custom)$")
    source: str = Field(..., min_length=1, max_length=512)
    tags: List[str] = Field(default_factory=list)
    cve_ids: List[str] = Field(default_factory=list)
    relevance_score: float = Field(0.5, ge=0.0, le=1.0)


class DocumentResponse(BaseModel):
    id: int
    title: str
    document_type: str
    source: str
    tags: List[str]
    cve_ids: List[str]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    search_type: str = Field("keyword", regex="^(keyword|semantic|hybrid)$")
    limit: int = Field(5, ge=1, le=20)


class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    document_type: str
    score: float
    tags: List[str]
    source: str


# Document Management Endpoints
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    req: DocumentCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create knowledge document."""
    # TODO: Check org authorization
    
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
        return DocumentResponse.model_validate(doc)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create document: {str(e)}")


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    org_id: int = Query(..., description="Organization ID"),
    document_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    tag: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    """List knowledge documents."""
    # TODO: Check org authorization
    
    query = KnowledgeDocument.filter(organization_id=org_id)
    if document_type:
        query = query.filter(document_type=document_type)
    if status_filter:
        query = query.filter(status=status_filter)
    if tag:
        query = query.filter(tags__contains=tag)
    
    docs = await query.order_by("-updated_at").limit(limit).all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get document details."""
    # TODO: Check org authorization
    
    doc = await KnowledgeDocument.get_or_none(id=doc_id, organization_id=org_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update last_accessed_at
    doc.last_accessed_at = datetime.utcnow()
    await doc.save()
    
    return DocumentResponse.model_validate(doc)


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Delete/archive document."""
    # TODO: Check org authorization
    
    doc = await KnowledgeDocument.get_or_none(id=doc_id, organization_id=org_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Archive instead of hard delete
    doc.status = "archived"
    await doc.save()


# Search Endpoints
@router.post("/search", response_model=List[SearchResult])
async def search_knowledge(
    req: SearchRequest,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Search knowledge base.
    
    Supports:
    - keyword: Full-text search on titles and content
    - semantic: Vector-based similarity search (requires embeddings)
    - hybrid: Combination of both methods
    """
    # TODO: Check org authorization
    
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
@router.get("/tags", response_model=List[dict])
async def list_tags(
    org_id: int = Query(..., description="Organization ID"),
    category: Optional[str] = None,
):
    """List knowledge tags."""
    # TODO: Check org authorization
    
    query = KnowledgeTag.filter(organization_id=org_id)
    if category:
        query = query.filter(category=category)
    
    tags = await query.order_by("-usage_count").all()
    return [{"tag": t.tag, "category": t.category, "usage_count": t.usage_count} for t in tags]


@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: str = Query(..., min_length=1, max_length=128),
    category: str = Query("custom", regex="^(tactic|technique|threat_actor|malware|tool|vulnerability|custom)$"),
    org_id: int = Query(..., description="Organization ID"),
):
    """Create knowledge tag."""
    # TODO: Check org authorization
    
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
@router.get("/search-log", response_model=List[dict])
async def get_search_log(
    org_id: int = Query(..., description="Organization ID"),
    agent_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    """Get knowledge search history for analytics."""
    # TODO: Check org authorization
    
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
    feedback: str = Query(..., regex="^(relevant|irrelevant|partially_relevant)$"),
    org_id: int = Query(..., description="Organization ID"),
):
    """Record user feedback on search results for ranking improvement."""
    # TODO: Check org authorization
    
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
