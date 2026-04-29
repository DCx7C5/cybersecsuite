"""Scope hierarchy — the foundation every other model depends on."""


from tortoise.models import Model
from tortoise import fields, models

from db.models.enums import RedBlueMode


class ProjectScope(Model):
    """Project scope level — organizational container."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "projects"
        table_description_plural = "Project Scopes"
        table_description_singular = "Project Scope"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active", "deleted_at"]),
        ]


class ApplicationScope(Model):
    """Application scope level — top-level application container."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "modules"
        table_description_singular = "Application Scope"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = ["name"]


class SessionScope(Model):
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
        "models.Project",
        related_name="sessions",
        on_delete=fields.CASCADE,
    )
    session_id = fields.CharField(max_length=128, unique=True, db_index=True)
    sdk_session_id = fields.CharField(max_length=128, null=True, db_index=True)
    name = fields.CharField(max_length=256, default="")
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")
    agent = fields.CharField(max_length=128, default="", db_index=True)
    mode = fields.CharEnumField(RedBlueMode, default=RedBlueMode.BLUE, db_index=True)
    phase = fields.CharField(max_length=64, default="init")
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "sessions"
        table_description_singular = "Session Scope"
        table_description_plural = "Session Scopes"
        indexes = [
            models.Index(fields=["project_id", "is_active"]),
            models.Index(fields=["session_id", "project_id"]),
        ]


class ScopedEntry(Model):
    """Abstract base for all scoped data.

    5-level scope columns (T045 / scope_v2):
        runtime_id    — container/pod runtime identity (VARCHAR 64, nullable)
        worktree_path — absolute path to .css/<runtime-id>/worktree-<SID>/
                        (VARCHAR 1024, nullable)
        scope_level   — one of: global, app, project, runtime, session
                        (VARCHAR 16, default 'session')

    Scope Hierarchy (inclusive):
        GLOBAL > APP > PROJECT > RUNTIME > SESSION

    Composite indexes for optimized queries:
        - (project, scope_level) — filter by project and scope
        - (session, runtime_id) — filter by session and runtime
        - (runtime_id, worktree_path) — filter by runtime and path
        - (is_active, deleted_at) — soft-delete queries
    """
    project = fields.ForeignKeyField(
        "models.Project",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    session = fields.ForeignKeyField(
        "models.Session",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)

    # T045: 5-level scope fields
    runtime_id = fields.CharField(
        max_length=64,
        null=True,
        db_index=True,
        description="Container/pod runtime identity for RUNTIME+ scopes",
    )
    worktree_path = fields.CharField(
        max_length=1024,
        null=True,
        description="Absolute path to .css/<runtime-id>/worktree-<SID>/",
    )
    scope_level = fields.CharField(
        max_length=16,
        default="session",
        db_index=True,
        description="One of: global, app, project, runtime, session",
    )

    class Meta:
        abstract = True

