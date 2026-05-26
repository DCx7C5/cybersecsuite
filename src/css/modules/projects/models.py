from tortoise.indexes import Index
from css.core.db.fields import DescriptionField, PathField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from css.core.db.fields import LabelField


class ProjectFile(BaseModel, TimestampMixin):
    """Database model for a project file."""

    name = LabelField()
    path = PathField(max_length=255)
    permissions = 1  # stub: FK to permission set — see tracker 'projects-permissions-relation'
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "project_file"
        table_verbose = "Project File"
        table_verbose_plural = "Project Files"



class Project(BaseModel, TimestampMixin):
    """Database model for a project."""

    name = LabelField()
    description = DescriptionField(null=True)
    project_dir = PathField(max_length=255)
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "project"
        table_verbose = "Project"
        table_verbose_plural = "Projects"
        unique_together = ("name", "project_dir")
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["name", "project_dir"]),
        ]
