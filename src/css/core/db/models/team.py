"""TeamScope model — team isolation, orchestrator pool, task queues, resource quotas."""

from tortoise import fields, models


class Team(models.Model):
    """Team scope — isolated team context with orchestrator pool and task queue.
    
    Fields:
        id: BigInt PK
        session_id: FK to SessionScope (parent)
        team_name: Team name (unique per session)
        status: one of (pending, active, paused, completed)
        orchestrator_mode: Strategy for task distribution (round-robin, least-busy, weighted)
        max_orchestrators: Pool size limit
        current_orchestrators: Active orchestrators in pool
        max_tasks: Task queue limit
        completed_tasks: Successfully completed tasks count
        created_at: Creation timestamp
        paused_at: Pause timestamp (null if active)
    """
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="teams",
        on_delete=fields.CASCADE,
        db_index=True,
    )
    team_name = fields.CharField(max_length=256, db_index=True)
    status = fields.CharField(
        max_length=16,
        default="pending",
        db_index=True,
        description="Status: pending, active, paused, completed",
    )
    orchestrator_mode = fields.CharField(
        max_length=32,
        default="round-robin",
        description="Orchestrator selection strategy",
    )
    max_orchestrators = fields.IntField(default=5)
    current_orchestrators = fields.IntField(default=0)
    max_tasks = fields.IntField(default=100)
    completed_tasks = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    paused_at = fields.DatetimeField(null=True)

    class Meta:
        table = "teams"
        table_description_singular = "Team"
        table_description_plural = "Teams"
        indexes = [
            models.Index(fields=["session_id", "team_name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        unique_together = [["session_id", "team_name"]]
