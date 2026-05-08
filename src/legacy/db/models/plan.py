"""Plan and task management models (3-level schema: Plan → PlanTask → PlanTodo)."""
from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField


class Plan(BaseModel):
    """Top-level plan container."""
    id = fields.BigIntField(primary_key=True)
    title = fields.CharField(max_length=256)
    description = DescriptionField(default="")
    scope = fields.CharField(max_length=128, default="general")
    status = fields.CharField(max_length=32, default="draft")  # draft, active, complete, archived
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "plans"

    def __str__(self) -> str:
        return f"Plan({self.id}, {self.title!r}, status={self.status})"


class PlanTask(BaseModel):
    """Tasks grouped by plan, with optional sequencing and assignment."""
    id = fields.BigIntField(primary_key=True)
    plan = fields.ForeignKeyField("models.Plan", related_name="tasks", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=256)
    description = DescriptionField(default="")
    assigned_to = fields.CharField(max_length=128, null=True, default=None)  # User or team assignment
    sequence = fields.IntField(default=0)  # For ordering tasks within plan
    status = fields.CharField(max_length=32, default="pending")  # pending, in_progress, done, blocked
    depends_on = fields.ManyToManyField("models.PlanTask", related_name="dependents", through="task_deps")
    claimed_by = fields.CharField(max_length=256, default="")  # Agent name or session ID
    claimed_at = fields.DatetimeField(null=True)  # When claimed
    lease_expires_at = fields.DatetimeField(null=True)  # Optional lease expiry for orphaned tasks
    target_files = fields.TextField(default="")  # JSON list of file paths agent will modify
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"

    def __str__(self) -> str:
        return f"PlanTask({self.id}, {self.title!r}, status={self.status})"

    def get_target_files(self) -> list[str]:
        """Extract target files from JSON field. Returns empty list if not set."""
        if not self.target_files:
            return []
        try:
            import json
            return json.loads(self.target_files)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_target_files(self, files: list[str]) -> None:
        """Set target files as JSON."""
        import json
        self.target_files = json.dumps(files)


class PlanTodo(BaseModel):
    """Sub-task items within a PlanTask for granular tracking."""
    id = fields.BigIntField(primary_key=True)
    task = fields.ForeignKeyField("models.PlanTask", related_name="todos", on_delete=fields.CASCADE)
    content = fields.TextField()  # Todo item description
    assignee = fields.CharField(max_length=128, null=True, default=None)  # Individual assignee
    status = fields.CharField(max_length=32, default="pending")  # pending, done, blocked
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "todos"

    def __str__(self) -> str:
        return f"PlanTodo({self.id}, {self.content[:50]!r}, status={self.status})"


# Backward compatibility aliases (for migration period)
Task = PlanTask
Todo = PlanTodo
