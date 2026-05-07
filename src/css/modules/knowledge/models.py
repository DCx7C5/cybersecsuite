"""Knowledge module — RAG knowledge base for LLM agents (Phase 7)."""

from tortoise import Model, fields
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Knowledge document source types."""
    CVE_FEED = "cve_feed"
    PLAYBOOK = "playbook"
    THREAT_REPORT = "threat_report"
    RUNBOOK = "runbook"
    INCIDENT_RETROSPECTIVE = "incident_retrospective"
    POLICY = "policy"
    TOOL_DOCUMENTATION = "tool_documentation"
    VENDOR_ADVISORY = "vendor_advisory"
    CUSTOM = "custom"


class DocumentStatus(str, Enum):
    """Document lifecycle status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class KnowledgeDocument(Model):
    """Searchable knowledge document with embeddings."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="knowledge_documents",
        on_delete=fields.CASCADE,
    )
    
    # Content
    title = fields.CharField(max_length=512, db_index=True)
    content = fields.TextField()
    
    # Classification
    document_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in DocumentType],
        db_index=True,
    )
    
    # Metadata
    source = fields.CharField(
        max_length=512,
        help_text="URL or internal path where document came from"
    )
    source_type = fields.CharField(
        max_length=64,
        choices=["url", "internal_file", "user_uploaded", "api_sync"],
        default="internal_file",
    )
    
    # Tagging
    tags = fields.JSONField(
        default=list,
        help_text="searchable tags (cve, malware, lateral_movement, etc.)"
    )
    cve_ids = fields.JSONField(
        default=list,
        help_text="CVE IDs mentioned in document"
    )
    
    # Relevance
    relevance_score = fields.FloatField(
        default=0.5,
        help_text="How relevant to org's context (0.0-1.0)"
    )
    
    # Embedding (for vector search)
    embedding = fields.TextField(
        null=True,
        help_text="JSON-serialized vector embedding for semantic search"
    )
    embedding_model = fields.CharField(
        max_length=64,
        default="sentence-transformers/all-mpnet-base-v2",
        help_text="Model used to generate embedding"
    )
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=[s.value for s in DocumentStatus],
        default="published",
        db_index=True,
    )
    
    # Versioning
    version = fields.IntField(default=1)
    parent_document_id = fields.BigIntField(
        null=True,
        help_text="Parent document if this is a version"
    )
    
    # Tracking
    created_by = fields.CharField(max_length=255, default="system")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_accessed_at = fields.DatetimeField(null=True)
    
    # Metadata for vector search optimization
    content_hash = fields.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA256 hash for deduplication"
    )
    
    class Meta:
        table = "knowledge_documents"
        indexes = [
            fields.Index(["organization", "document_type", "status"]),
            fields.Index(["organization", "-updated_at"]),
        ]


class KnowledgeIndex(Model):
    """Index entry for full-text search across documents."""
    
    id = fields.BigIntField(primary_key=True)
    document: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.KnowledgeDocument",
        related_name="index_entries",
        on_delete=fields.CASCADE,
    )
    
    # Indexed text (stemmed/tokenized)
    term = fields.CharField(max_length=128, db_index=True)
    frequency = fields.IntField(default=1)
    
    # Position tracking for phrase matching
    positions = fields.JSONField(default=list)
    
    class Meta:
        table = "knowledge_index"
        unique_together = (("document", "term"),)


class KnowledgeTag(Model):
    """Taxonomy tags for knowledge organization."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="knowledge_tags",
        on_delete=fields.CASCADE,
    )
    
    tag = fields.CharField(max_length=128, db_index=True)
    category = fields.CharField(
        max_length=64,
        choices=["tactic", "technique", "threat_actor", "malware", "tool", "vulnerability", "custom"],
        default="custom",
    )
    
    description = fields.TextField(default="")
    usage_count = fields.IntField(default=0)
    
    class Meta:
        table = "knowledge_tags"
        unique_together = (("organization", "tag"),)


class SearchLog(Model):
    """Log of agent/user knowledge base searches for analytics."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="knowledge_searches",
        on_delete=fields.CASCADE,
    )
    
    # Search query
    query = fields.TextField()
    search_type = fields.CharField(
        max_length=32,
        choices=["keyword", "semantic", "tag_filter"],
        default="keyword",
    )
    
    # Result
    matched_documents = fields.JSONField(
        default=list,
        help_text="IDs of documents returned"
    )
    result_count = fields.IntField(default=0)
    
    # Context
    agent_id = fields.CharField(max_length=255, null=True)
    user_id = fields.CharField(max_length=255, null=True)
    
    # Metadata
    relevance_feedback = fields.CharField(
        max_length=16,
        choices=["relevant", "irrelevant", "partially_relevant", "none"],
        default="none",
    )
    
    searched_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "knowledge_search_log"
        ordering = ["-searched_at"]


__all__ = [
    "DocumentType",
    "DocumentStatus",
    "KnowledgeDocument",
    "KnowledgeIndex",
    "KnowledgeTag",
    "SearchLog",
]
