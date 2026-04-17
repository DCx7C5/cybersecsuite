"""NIST Cybersecurity Framework 2.0 control model."""

from tortoise import fields
from tortoise.models import Model


class NistCsfControl(Model):
    """NIST CSF 2.0 subcategory — 185 entries across 6 functions."""

    id = fields.IntField(primary_key=True)
    control_id = fields.CharField(max_length=32, unique=True, db_index=True)
    title = fields.TextField()
    function = fields.CharField(max_length=32, db_index=True)       # GOVERN/IDENTIFY/PROTECT/DETECT/RESPOND/RECOVER
    function_code = fields.CharField(max_length=4, db_index=True)   # GV/ID/PR/DE/RS/RC
    function_description = fields.TextField(default="")
    category = fields.CharField(max_length=128, db_index=True)
    category_description = fields.TextField(default="")
    implementation_examples = fields.JSONField(default=list)
    informative_references = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "compliance_nist_csf"
        ordering = ["control_id"]
        indexes = (("function",), ("function_code",), ("category",))

    def __str__(self) -> str:
        return f"{self.control_id}: {self.title[:60]}"
