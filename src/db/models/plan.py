"""Plan and task management models (3-level schema: Plan → Task → Todo)."""
from tortoise import fields
from tortoise.models import Model


class Plan(Model):
    """Top-level plan container."""
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=256)
    description = fields.TextField(default="")
    scope = fields.CharField(max_length=128, default="general")
    status = fields.CharField(max_length=32, default="draft")  # draft, active, complete, archived
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "plans"

    def __str__(self) -> str:
        return f"Plan({self.id}, {self.title!r}, status={self.status})"


class Task(Model):
    """Tasks grouped by plan, with optional sequencing and assignment."""
    id = fields.IntField(primary_key=True)
    plan = fields.ForeignKeyField("models.Plan", related_name="tasks", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=256)
    description = fields.TextField(default="")
    assigned_to = fields.CharField(max_length=128, null=True, default=None)  # User or team assignment
    sequence = fields.IntField(default=0)  # For ordering tasks within plan
    status = fields.CharField(max_length=32, default="pending")  # pending, in_progress, done, blocked
    depends_on = fields.ManyToManyField("models.Task", related_name="dependents", through="task_deps")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"

    def __str__(self) -> str:
        return f"Task({self.id}, {self.title!r}, status={self.status})"


class Todo(Model):
    """Sub-task items within a Task for granular tracking."""
    id = fields.IntField(primary_key=True)
    task = fields.ForeignKeyField("models.Task", related_name="todos", on_delete=fields.CASCADE)
    content = fields.TextField()  # Todo item description
    assignee = fields.CharField(max_length=128, null=True, default=None)  # Individual assignee
    status = fields.CharField(max_length=32, default="pending")  # pending, done
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "todos"

    def __str__(self) -> str:
        return f"Todo({self.id}, {self.content[:50]!r}, status={self.status})"
