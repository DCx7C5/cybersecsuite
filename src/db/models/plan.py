"""Plan and task management models."""
from tortoise import fields
from tortoise.models import Model


class Plan(Model):
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
    id = fields.IntField(primary_key=True)
    plan = fields.ForeignKeyField("models.Plan", related_name="tasks", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=256)
    description = fields.TextField(default="")
    status = fields.CharField(max_length=32, default="pending")  # pending, in_progress, done, blocked
    depends_on = fields.ManyToManyField("models.Task", related_name="dependents", through="task_deps")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"

    def __str__(self) -> str:
        return f"Task({self.id}, {self.title!r}, status={self.status})"


class ExecutionLog(Model):
    id = fields.IntField(primary_key=True)
    task = fields.ForeignKeyField("models.Task", related_name="logs", on_delete=fields.CASCADE)
    message = fields.TextField()
    level = fields.CharField(max_length=16, default="info")  # info, warning, error
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "execution_logs"

    def __str__(self) -> str:
        return f"ExecutionLog({self.id}, level={self.level})"
