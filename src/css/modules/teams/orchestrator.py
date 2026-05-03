"""Team orchestrator pool management."""
from tortoise import fields, models

class OrchestratorPoolEntry(models.Model):
    """Orchestrator in team pool."""
    id = fields.BigIntField(primary_key=True)
    team = fields.ForeignKeyField("models.Team", related_name="orchestrators", on_delete=fields.CASCADE)
    orchestrator_id = fields.BigIntField(db_index=True)
    status = fields.CharField(max_length=16, default="idle")
    assigned_tasks = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "orchestrator_pool_entries"
        indexes = [models.Index(fields=["team_id", "status"])]
