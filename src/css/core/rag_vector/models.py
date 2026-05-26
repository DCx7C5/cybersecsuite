"""Knowledge module — RAG rag_vector base for LLM agents (Phase 7)."""
from tortoise.indexes import Index
from tortoise import fields
from tortoise.fields import CharEnumField

from css.core.db.fields import DescriptionField, QualityScoreField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from css.core.rag_vector.enums import (
    DocumentStatus,
    DocumentType,
    RelevanceFeedback,
    SearchType,
    SourceType,
    TagCategory,
)


class KnowledgeDocument(BaseModel, TimestampMixin):
    """Searchable rag_vector document with embeddings."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="knowledge_documents",
        on_delete=fields.CASCADE,
    )
    
    # Content
    title = fields.CharField(max_length=512, db_index=True)
    content = fields.TextField()
    
    # Classification
    document_type = CharEnumField(
        DocumentType,
        db_index=True,
    )
    
    # Metadata
    source = fields.CharField(
        max_length=512,
        help_text="URL or internal path where document came from"
    )
    source_type = CharEnumField(
        SourceType,
        default=SourceType.INTERNAL_FILE,
    )
    
    # Tagging
    tags = fields.JSONField( # TODO: relation to tags 
        default=list,
        help_text="searchable tags (cve, malware, lateral_movement, etc.)"
    )
    cve_ids = fields.JSONField(
        default=list,
        help_text="CVE IDs mentioned in document"
    )
    
    # Relevance
    relevance_score = QualityScoreField(
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
    status = CharEnumField(
        DocumentStatus,
        default=DocumentStatus.PUBLISHED,
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
    last_accessed_at = fields.DatetimeField(null=True)
    
    # Metadata for vector search optimization
    content_hash = fields.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA256 hash for deduplication"
    )
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "knowledge_documents"
        indexes = [
            Index(fields=["organization_id", "document_type", "status"]),
            Index(fields=["organization_id", "updated_at"]),
        ]


class KnowledgeIndex(BaseModel):
    """Index entry for full-text search across documents."""

    document: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.KnowledgeDocument",
        related_name="index_entries",
        on_delete=fields.CASCADE,
    )
    
    # Indexed text (stemmed/tokenized)
    term = fields.CharField(max_length=128, db_index=True)
    frequency = fields.IntField(default=1)
    
    # Position tracking for phrase matching
    positions = fields.JSONField(default=list)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "knowledge_index"
        table_verbose = "Knowledge Index"
        table_verbose_plural = "Knowledge Indices"
        ordering = ["-document__updated_at"]
        indexes = [
            Index(fields=["document_id", "term"]),
        ]
        unique_together = (
            ("document", "term"),
        )


class KnowledgeTag(BaseModel):
    """Taxonomy tags for rag_vector organization."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="knowledge_tags",
        on_delete=fields.CASCADE,
    )
    
    tag = fields.CharField(max_length=128, db_index=True)
    category = CharEnumField(
        TagCategory,
        default=TagCategory.CUSTOM,
    )
    
    description = DescriptionField(default="")
    usage_count = fields.IntField(default=0)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "knowledge_tags"
        unique_together = (("organization_id", "tag"),)


class SearchLog(BaseModel):
    """Log of agent/user rag_vector base searches for analytics."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="knowledge_searches",
        on_delete=fields.CASCADE,
    )
    
    # Search query
    query = fields.TextField()
    search_type = CharEnumField(
        SearchType,
        default=SearchType.KEYWORD,
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
    relevance_feedback = CharEnumField(
        RelevanceFeedback,
        default=RelevanceFeedback.NONE,
    )
    
    searched_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
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
