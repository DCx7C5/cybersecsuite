"""
Kernel models — kernel snapshots and loaded modules.
"""
from css.core.db.models.base import BaseModel
from tortoise import fields

from db.models.enums import ModuleStatus
from db.models.scope import ScopedEntry


class Kernel(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    captured_at = fields.DatetimeField(auto_now_add=True)
    version = fields.CharField(max_length=256, db_index=True)
    release = fields.CharField(max_length=256, default="", db_index=True)
    is_tainted = fields.BooleanField(default=False, db_index=True)
    cmdline = fields.TextField(default="")
    taint_value = fields.IntField(default=0)
    taint_reason = fields.TextField(default="")
    lsm_status = fields.CharField(max_length=128, default="")
    ebpf_program_count = fields.IntField(default=0)
    notes = fields.TextField(default="")

    class Meta:
        table = "kernels"
        ordering = ["-captured_at"]


class KernelModule(BaseModel):
    id = fields.BigIntField(primary_key=True)
    kernel = fields.ForeignKeyField("models.Kernel", related_name="modules", on_delete=fields.CASCADE)
    name = fields.CharField(max_length=256, db_index=True)
    size = fields.BigIntField(default=0)
    status = fields.CharEnumField(ModuleStatus, default=ModuleStatus.LOADED, db_index=True)
    is_signed = fields.BooleanField(default=False)
    is_suspect = fields.BooleanField(default=False, db_index=True)
    notes = fields.TextField(default="")

    class Meta:
        table = "kernel_modules"
        unique_together = [("kernel_id", "name")]
