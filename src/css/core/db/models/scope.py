"""Scope hierarchy ORM models and query helpers."""

from datetime import UTC, datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.fields import DescriptionField, PathField, SlugField
from css.core.enums import ScopeLevel

from css.core.db.serializers import BaseModelSerializer
from .base import BaseModel
from .enums import RedBlueMode
from .mixins import SoftDeleteMixin, AuditTrailMixin


class AppScopeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for app scope data."""

    id: int
    name: str
    description: str
    working_dir: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None


class ProjectScopeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for project scope data."""

    id: int
    name: str
    description: str
    working_dir: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None


class SessionScopeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for session scope data."""

    id: int
    project_id: int | None
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


class AppScopeManager:
    """Query helpers for ``AppScope``."""

    async def active(self) -> list["AppScope"]:
        return await AppScope.filter(is_active=True, deleted_at__isnull=True).order_by("name", "id")

    async def by_name(self, name: str) -> "AppScope | None":
        return await AppScope.get_or_none(name=name)

    async def by_working_dir(self, working_dir: str) -> "AppScope | None":
        return await AppScope.get_or_none(working_dir=working_dir)


class ProjectScopeManager:
    """Query helpers for ``ProjectScope``."""

    async def active(self) -> list["ProjectScope"]:
        return await ProjectScope.filter(is_active=True, deleted_at__isnull=True).order_by(
            "name",
            "id",
        )

    async def by_name(self, name: str) -> "ProjectScope | None":
        return await ProjectScope.get_or_none(name=name)

    async def by_working_dir(self, working_dir: str) -> "ProjectScope | None":
        return await ProjectScope.get_or_none(working_dir=working_dir)


class SessionScopeManager:
    """Query helpers for ``SessionScope``."""

    async def active(self) -> list["SessionScope"]:
        return await SessionScope.filter(is_active=True, deleted_at__isnull=True).order_by(
            "-updated_at",
            "session_id",
            "id",
        )

    async def by_session_id(self, session_id: str) -> "SessionScope | None":
        return await SessionScope.get_or_none(session_id=session_id)

    async def by_project(self, project_id: int) -> list["SessionScope"]:
        return await SessionScope.filter(project_id=project_id).order_by("-updated_at", "session_id")

    async def by_mode(self, mode: RedBlueMode | str) -> list["SessionScope"]:
        mode_value = mode.value if hasattr(mode, "value") else str(mode)  # type: ignore[reportAttributeAccessIssue]
        return await SessionScope.filter(mode=mode_value).order_by("-updated_at", "session_id")

    async def in_phase(self, phase: str) -> list["SessionScope"]:
        return await SessionScope.filter(phase=phase).order_by("-updated_at", "session_id")

    async def running(self) -> list["SessionScope"]:
        return await SessionScope.filter(
            started_at__not_isnull=True,
            completed_at__isnull=True,
            is_active=True,
            deleted_at__isnull=True,
        ).order_by("-started_at", "session_id")


class AppScope(BaseModel, SoftDeleteMixin):
    """Application scope — top-level global container."""

    name = SlugField(max_length=256, allow_underscores=True, db_index=True, unique=True)
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = AppScopeManager()

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

    @property
    def has_working_dir(self) -> bool:
        return bool(self.working_dir)

    async def set_working_dir(self, working_dir: str) -> None:
        await self.save_changes(working_dir=working_dir, updated_at=datetime.now(UTC))

    async def deactivate(self) -> None:
        await self.save_changes(
            is_active=False,
            deleted_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def restore(self) -> None:
        await self.save_changes(
            is_active=True,
            deleted_at=None,
            updated_at=datetime.now(UTC),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "app_scopes"
        table_verbose = "App Scope"
        table_verbose_plural = "App Scopes"
        ordering = ["name", "id"]
        indexes = [
            Index(fields=["name"]),
            Index(fields=["is_active", "deleted_at"]),
            Index(fields=["working_dir"]),
        ]


class ProjectScope(BaseModel, SoftDeleteMixin):
    """Project scope — persistent project-level workspace container."""

    name = SlugField(max_length=256, allow_underscores=True, db_index=True, unique=True)
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = ProjectScopeManager()

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

    @property
    def has_working_dir(self) -> bool:
        return bool(self.working_dir)

    async def set_working_dir(self, working_dir: str) -> None:
        await self.save_changes(working_dir=working_dir, updated_at=datetime.now(UTC))

    async def deactivate(self) -> None:
        await self.save_changes(
            is_active=False,
            deleted_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def restore(self) -> None:
        await self.save_changes(
            is_active=True,
            deleted_at=None,
            updated_at=datetime.now(UTC),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "projects"
        table_verbose = "Project Scope"
        table_verbose_plural = "Project Scopes"
        ordering = ["name", "id"]
        indexes = [
            Index(fields=["name"]),
            Index(fields=["is_active", "deleted_at"]),
            Index(fields=["working_dir"]),
        ]


class SessionScope(BaseModel, SoftDeleteMixin):
    """Session scope — mutable execution context for one investigation run."""

    project = fields.ForeignKeyField(
        "models.ProjectScope",
        related_name="sessions",
        on_delete=fields.CASCADE,
        null=True,
        db_index=True,
    )
    session_id = fields.CharField(max_length=128, unique=True, db_index=True)
    sdk_session_id = fields.CharField(max_length=128, null=True, db_index=True)
    name = fields.CharField(max_length=256, default="")
    description = DescriptionField(default="")
    working_dir = PathField(max_length=1024, default="", db_index=True)
    agent = fields.CharField(max_length=128, default="", db_index=True)
    mode = fields.CharEnumField(RedBlueMode, default=RedBlueMode.BLUE, db_index=True)
    phase = fields.CharField(max_length=64, default="init", db_index=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = SessionScopeManager()

    def to_domain(self) -> SessionScopeInfo:
        return SessionScopeInfo(
            id=self.id,
            project_id=self.project_id,  # type: ignore[reportAttributeAccessIssue]
            session_id=self.session_id,
            sdk_session_id=self.sdk_session_id,
            name=self.name,
            description=self.description,
            working_dir=self.working_dir,
            agent=self.agent,
            mode=self.mode_value,
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

    @property
    def mode_value(self) -> str:
        return self.mode.value if hasattr(self.mode, "value") else str(self.mode)

    @property
    def has_sdk_session(self) -> bool:
        return bool(self.sdk_session_id)

    @property
    def is_running(self) -> bool:
        return self.started_at is not None and self.completed_at is None

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    async def bind_sdk_session(self, sdk_session_id: str | None) -> None:
        await self.save_changes(
            sdk_session_id=sdk_session_id,
            updated_at=datetime.now(UTC),
        )

    async def attach_project(self, project_id: int | None) -> None:
        await self.save_changes(project_id=project_id, updated_at=datetime.now(UTC))

    async def set_phase(self, phase: str) -> None:
        await self.save_changes(phase=phase, updated_at=datetime.now(UTC))

    async def switch_mode(self, mode: RedBlueMode | str) -> None:
        mode_value = mode.value if hasattr(mode, "value") else str(mode)  # type: ignore[reportAttributeAccessIssue]
        await self.save_changes(mode=mode_value, updated_at=datetime.now(UTC))

    async def set_working_dir(self, working_dir: str) -> None:
        await self.save_changes(working_dir=working_dir, updated_at=datetime.now(UTC))

    async def mark_started(
        self,
        *,
        phase: str | None = None,
        started_at: datetime | None = None,
    ) -> None:
        now = started_at or datetime.now(UTC)
        changes: dict[str, object] = {
            "started_at": now,
            "completed_at": None,
            "updated_at": now,
        }
        if phase is not None:
            changes["phase"] = phase
        await self.save_changes(**changes)

    async def mark_completed(self, completed_at: datetime | None = None) -> None:
        now = completed_at or datetime.now(UTC)
        await self.save_changes(completed_at=now, updated_at=now)

    async def deactivate(self) -> None:
        await self.save_changes(
            is_active=False,
            deleted_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def restore(self) -> None:
        await self.save_changes(
            is_active=True,
            deleted_at=None,
            updated_at=datetime.now(UTC),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "sessions"
        table_verbose = "Session Scope"
        table_verbose_plural = "Session Scopes"
        ordering = ["-updated_at", "session_id", "id"]
        indexes = [
            Index(fields=["project_id", "is_active"]),
            Index(fields=["session_id", "project_id"]),
            Index(fields=["mode", "phase"]),
            Index(fields=["sdk_session_id"]),
        ]


class ScopedEntry(BaseModel, SoftDeleteMixin, AuditTrailMixin):
    """Abstract base for records that can be bound to project/runtime/session scopes.

    Combines scope binding fields, audit trail (via AuditTrailMixin), and soft-delete
    support (via SoftDeleteMixin).
    """

    project = fields.ForeignKeyField(
        "models.ProjectScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    session = fields.ForeignKeyField(
        "models.SessionScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    runtime_id = fields.CharField(
        max_length=64,
        null=True,
        db_index=True,
        description="Container/pod runtime identity for runtime-bound scopes",
    )
    worktree_path = PathField(
        max_length=1024,
        null=True,
        description="Absolute path to the runtime worktree for this record",
    )
    scope_level = fields.CharEnumField(
        ScopeLevel,
        default=ScopeLevel.SESSION,
        db_index=True,
        description="One of: global, app, project, runtime, session",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True

    @property
    def scope_level_value(self) -> str:
        return self.scope_level.value if hasattr(self.scope_level, "value") else str(self.scope_level)  # type: ignore[reportAttributeAccessIssue]

    @property
    def has_project_scope(self) -> bool:
        return self.project_id is not None  # type: ignore[reportAttributeAccessIssue]

    @property
    def has_session_scope(self) -> bool:
        return self.session_id is not None  # type: ignore[reportAttributeAccessIssue]

    @property
    def scope_anchor(self) -> str | None:
        if self.scope_level == ScopeLevel.SESSION and self.session_id is not None:  # type: ignore[reportAttributeAccessIssue]
            return str(self.session_id)  # type: ignore[reportAttributeAccessIssue]
        if self.scope_level == ScopeLevel.RUNTIME and self.runtime_id:
            return self.runtime_id
        if self.scope_level == ScopeLevel.PROJECT and self.project_id is not None:  # type: ignore[reportAttributeAccessIssue]
            return str(self.project_id)  # type: ignore[reportAttributeAccessIssue]
        if self.scope_level == ScopeLevel.APP and self.project_id is not None:  # type: ignore[reportAttributeAccessIssue]
            return str(self.project_id)  # type: ignore[reportAttributeAccessIssue]
        if self.scope_level == ScopeLevel.GLOBAL:  # type: ignore[reportAttributeAccessIssue]
            return "global"
        return None

    @property
    def scope_key(self) -> str:
        return f"{self.scope_level_value}:{self.scope_anchor or 'unbound'}"

    def bind_scope(
        self,
        *,
        project_id: int | None = None,
        session_id: int | None = None,
        runtime_id: str | None = None,
        worktree_path: str | None = None,
        scope_level: ScopeLevel | str | None = None,
    ) -> list[str]:
        level_value = (
            scope_level.value  # type: ignore[reportAttributeAccessIssue]
            if scope_level is not None and hasattr(scope_level, "value")
            else scope_level
        )
        changes: dict[str, object] = {
            "project_id": project_id,
            "session_id": session_id,
            "runtime_id": runtime_id,
            "worktree_path": worktree_path,
        }
        if level_value is not None:
            changes["scope_level"] = level_value
        return self.apply_updates(**changes)

    async def save_scope(
        self,
        *,
        project_id: int | None = None,
        session_id: int | None = None,
        runtime_id: str | None = None,
        worktree_path: str | None = None,
        scope_level: ScopeLevel | str | None = None,
    ) -> list[str]:
        level_value = (
            scope_level.value  # type: ignore[reportAttributeAccessIssue]
            if scope_level is not None and hasattr(scope_level, "value")
            else scope_level
        )
        changes: dict[str, object] = {
            "project_id": project_id,
            "session_id": session_id,
            "runtime_id": runtime_id,
            "worktree_path": worktree_path,
            "updated_at": datetime.now(UTC),
        }
        if level_value is not None:
            changes["scope_level"] = level_value
        return await self.save_changes(**changes)

class AppScopeSerializer(BaseModelSerializer[AppScope]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = AppScope
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectScopeSerializer(BaseModelSerializer[ProjectScope]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = ProjectScope
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SessionScopeSerializer(BaseModelSerializer[SessionScope]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = SessionScope
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "session_id")
