from tortoise.indexes import Index
from tortoise.models import Model
from tortoise import fields



class ProjectFile(Model):
    """Database model for a project file."""

    id = fields.BigIntField(max_length=255, primary_key=True)
    name = fields.CharField(max_length=255)
    path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "project_file"
        table_verbose = "Project File"
        table_verbose_plural = "Project Files"



class Project(Model):
    """Database model for a project."""

    id = fields.BigIntField(max_length=255, primary_key=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    project_dir = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "project"
        table_verbose = "Project"
        table_verbose_plural = "Projects"
        unique_together = ("name", "project_dir")
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["name", "project_dir"]),
        ]
