from tortoise.indexes import Index
from css.core.db.fields import DescriptionField, PathField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from css.core.db.fields import LabelField


class ProjectFile(BaseModel, TimestampMixin):
    """Database model for a project file."""

    name = LabelField()
    path = PathField(max_length=255)
    permissions = 1 # TODO: relation to PermissionTable
    class Meta:
        table = "project_file"
        table_verbose = "Project File"
        table_verbose_plural = "Project Files"



class Project(BaseModel, TimestampMixin):
    """Database model for a project."""

    name = LabelField()
    description = DescriptionField(null=True)
    project_dir = PathField(max_length=255)
    class Meta:
        table = "project"
        table_verbose = "Project"
        table_verbose_plural = "Projects"
        unique_together = ("name", "project_dir")
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["name", "project_dir"]),
        ]
