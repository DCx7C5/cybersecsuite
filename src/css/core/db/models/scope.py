"""Scope hierarchy — the foundation every other model depends on."""

from datetime import datetime

import msgspec
from tortoise import fields, models

from css.core.db.fields import DescriptionField, NameField, PathField
from .base import BaseModel
from .enums import RedBlueMode, ScopeLevel
from .mixins import SoftDeleteMixin


class AppScopeInfo(msgspec.Struct):
    """Domain value type for app scope data."""
    id: int
    name: str
    description: str
    working_dir: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None


class AppScope(BaseModel, SoftDeleteMixin):
    """Application scope — top-level global container."""
    name = NameField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> AppScopeInfo:
        return AppScopeInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            working_dir=self.working_dir,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_domain(cls, info: AppScopeInfo) -> "AppScope":
        return cls(
            name=info.name,
            description=info.description,
            working_dir=info.working_dir,
        )

    class Meta:
        table = "app_scopes"
        table_description_singular = "App Scope"
        table_description_plural = "App Scopes"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active", "deleted_at"]),
        ]


class ProjectScopeInfo(msgspec.Struct):
    """Domain value type for project scope data."""
    id: int
    name: str
    description: str
    working_dir: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None


class ProjectScope(BaseModel, SoftDeleteMixin):
    """Project scope — organizational container within app scope."""
    name = NameField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> ProjectScopeInfo:
        return ProjectScopeInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            working_dir=self.working_dir,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_domain(cls, info: ProjectScopeInfo) -> "ProjectScope":
        return cls(
            name=info.name,
            description=info.description,
            working_dir=info.working_dir,
        )

    class Meta:
        table = "projects"
        table_description_plural = "Project Scopes"
        table_description_singular = "Project Scope"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active", "deleted_at"]),
        ]


class SessionScopeInfo(msgspec.Struct):
    """Domain value type for session scope data."""
    id: int
    project_id: int
    session_id: str
    sdk_session_id: str | None
    name: str
    description: str
    working_dir: str
    agent: str
    mode: str
    phase: str
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None


class SessionScope(BaseModel, SoftDeleteMixin):
    """Forensic root session — UUID-keyed anchor for all forensic artifacts.

    Every :class:`Finding`, :class:`IOC`, :class:`AuditLog`, :class:`Artifact`,
    :class:`ComplianceCheck`, :class:`DefenseRecommendation`, :class:`Vulnerability`,
    :class:`UserGuidance`, and :class:`ForensicSession` row is FK-linked to this
    model.  Managed via Tortoise ORM through the ASGI stack.

    Not to be confused with:
    - :class:`db.models.llm_session.LlmSession` — per-worktree LLM cost tracker
      (asyncpg-only, 12-char hex PK, no Tortoise ORM dependency)
    - :class:`db.models.forensic.ForensicSession` — investigation phase bridge
      between this ``Session`` and a :class:`ForensicProject`
    """
    project = fields.ForeignKeyField(
        "css.ProjectScope",
        related_name="sessions",
        on_delete=fields.CASCADE,
    )
    session_id = fields.CharField(max_length=128, unique=True, db_index=True)
    sdk_session_id = fields.CharField(max_length=128, null=True, db_index=True)
    name = fields.CharField(max_length=256, default="")
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    agent = fields.CharField(max_length=128, default="", db_index=True)
    mode = fields.CharEnumField(RedBlueMode, default=RedBlueMode.BLUE, db_index=True)
    phase = fields.CharField(max_length=64, default="init")
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> SessionScopeInfo:
        return SessionScopeInfo(
            id=self.id,
            project_id=self.project_id,
            session_id=self.session_id,
            sdk_session_id=self.sdk_session_id,
            name=self.name,
            description=self.description,
            working_dir=self.working_dir,
            agent=self.agent,
            mode=self.mode.value if hasattr(self.mode, 'value') else self.mode,
            phase=self.phase,
            started_at=self.started_at,
            completed_at=self.completed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_domain(cls, info: SessionScopeInfo) -> "SessionScope":
        return cls(
            project_id=info.project_id,
            session_id=info.session_id,
            sdk_session_id=info.sdk_session_id,
            name=info.name,
            description=info.description,
            working_dir=info.working_dir,
            agent=info.agent,
            mode=info.mode,
            phase=info.phase,
            started_at=info.started_at,
            completed_at=info.completed_at,
        )

    class Meta:
        table = "sessions"
        table_verbose = "Session Scope"
        table_verbose_plural = "Session Scopes"
        indexes = [
            models.Index(fields=["project_id", "is_active"]),
            models.Index(fields=["session_id", "project_id"]),
        ]


class ScopedEntry(BaseModel, SoftDeleteMixin):
    """Abstract base for all scoped data.

    5-level scopes columns (T045 / scope_v2):
        runtime_id    — container/pod runtime identity (VARCHAR 64, nullable)
        worktree_path — absolute path to .css/<runtime-id>/worktree-<SID>/
                        (VARCHAR 1024, nullable)
        scope_level   — one of: global, app, project, runtime, session
                        (VARCHAR 16, default 'session')

    Scope Hierarchy (inclusive):
        GLOBAL > APP > PROJECT > RUNTIME > SESSION

    Composite indexes for optimized queries:
        - (project, scope_level) — filter by project and scopes
        - (session, runtime_id) — filter by session and runtime
        - (runtime_id, worktree_path) — filter by runtime and path
        - (is_active, deleted_at) — soft-delete queries
    """
    project = fields.ForeignKeyField(
        "css.ProjectScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    session = fields.ForeignKeyField(
        "css.SessionScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # T045: 5-level scopes fields
    runtime_id = fields.CharField(
        max_length=64,
        null=True,
        db_index=True,
        description="Container/pod runtime identity for RUNTIME+ scopes",
    )
    worktree_path = PathField(
        max_length=1024,
        null=True,
        description="Absolute path to .css/<runtime-id>/worktree-<SID>/",
    )
    scope_level = fields.CharEnumField(
        ScopeLevel,
        default=ScopeLevel.SESSION,
        db_index=True,
        description="One of: global, app, project, runtime, session",
    )

    class Meta:
        abstract = True
