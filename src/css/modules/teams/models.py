"""Team models integration."""
from tortoise import models, fields

class TeamModel(models.Model):
    """Integrated team model."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256)
    
    class Meta:
        table = "teams_integration"
