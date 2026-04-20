"""Scope hierarchy — the foundation every other model depends on."""
from tortoise.models import Model
from tortoise import fields, models

from db.models.enums import RedBlueMode


class Project(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "projects"


class Application(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    class Meta:
        table = "applications"
        indexes = [
            models.Index(fields=["name"]),
        ]
        unique_together = ["name"]


class Session(Model):
    """Forensic root session — UUID-keyed anchor for all forensic artefacts.

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
    project = fields.ForeignKeyField("models.Project", related_name="sessions", on_delete=fields.CASCADE)
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


class ScopedEntry(Model):
    """Abstract base for all scoped data."""
    project = fields.ForeignKeyField("models.Project", related_name=False, null=True, on_delete=fields.CASCADE, db_index=True)
    session = fields.ForeignKeyField("models.Session", related_name=False, null=True, on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

