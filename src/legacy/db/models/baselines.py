"""
Baseline models — known-good snapshots for delta comparison.
Network, Process, Kernel, and Persistence baselines.
"""
from tortoise import fields

from db.models.scope import ScopedEntry


class NetworkBaseline(ScopedEntry):
    """Network configuration baseline."""
    id = fields.BigIntField(primary_key=True)
    captured_at = fields.DatetimeField(auto_now_add=True)
    is_active_baseline = fields.BooleanField(default=True, db_index=True)
    snapshot_hash = fields.CharField(max_length=128, default="")
    confirmed_clean = fields.BooleanField(default=False)

    interfaces = fields.JSONField(default=list)
    arp_table = fields.JSONField(default=list)
    listening_ports = fields.JSONField(default=list)
    established_connections = fields.JSONField(default=list)
    routes = fields.JSONField(default=list)
    firewall_rules_hash = fields.CharField(max_length=128, default="")
    notes = fields.TextField(default="")

    class Meta:
        table = "network_baselines"
        ordering = ["-captured_at"]
        indexes = [
            ("project_id", "is_active_baseline"),
        ]


class ProcessBaseline(ScopedEntry):
    """Process and service baseline."""
    id = fields.BigIntField(primary_key=True)
    captured_at = fields.DatetimeField(auto_now_add=True)
    is_active_baseline = fields.BooleanField(default=True, db_index=True)
    snapshot_hash = fields.CharField(max_length=128, default="")
    confirmed_clean = fields.BooleanField(default=False)

    ps_count = fields.IntField(default=0)
    proc_count = fields.IntField(default=0)
    process_delta = fields.IntField(default=0)
    running_processes = fields.JSONField(default=list)
    deleted_executables = fields.JSONField(default=list)
    known_services = fields.JSONField(default=list)
    kernel_modules = fields.JSONField(default=list)
    lsmod_count = fields.IntField(default=0)
    proc_modules_count = fields.IntField(default=0)
    module_delta = fields.IntField(default=0)
    notes = fields.TextField(default="")

    class Meta:
        table = "process_baselines"
        ordering = ["-captured_at"]
        indexes = [
            ("project_id", "is_active_baseline"),
        ]


class KernelBaseline(ScopedEntry):
    """Kernel and eBPF baseline."""
    id = fields.BigIntField(primary_key=True)
    captured_at = fields.DatetimeField(auto_now_add=True)
    is_active_baseline = fields.BooleanField(default=True, db_index=True)
    snapshot_hash = fields.CharField(max_length=128, default="")
    confirmed_clean = fields.BooleanField(default=False)

    kernel_version = fields.CharField(max_length=255, default="")
    kernel_cmdline = fields.TextField(default="")
    taint_value = fields.IntField(default=0)
    taint_reason = fields.TextField(default="")
    lsm_status = fields.CharField(max_length=128, default="")
    ebpf_programs = fields.JSONField(default=list)
    ebpf_maps = fields.JSONField(default=list)
    security_settings = fields.JSONField(default=dict)
    notes = fields.TextField(default="")

    class Meta:
        table = "kernel_baselines"
        ordering = ["-captured_at"]
        indexes = [
            ("project_id", "is_active_baseline"),
        ]


class PersistenceBaseline(ScopedEntry):
    """Persistence mechanism baseline."""
    id = fields.BigIntField(primary_key=True)
    captured_at = fields.DatetimeField(auto_now_add=True)
    is_active_baseline = fields.BooleanField(default=True, db_index=True)
    snapshot_hash = fields.CharField(max_length=128, default="")
    confirmed_clean = fields.BooleanField(default=False)

    systemd_system_units = fields.JSONField(default=list)
    systemd_user_units = fields.JSONField(default=list)
    package_hooks = fields.JSONField(default=list)
    shell_configs = fields.JSONField(default=list)
    autostart_entries = fields.JSONField(default=list)
    cron_entries = fields.JSONField(default=list)
    udev_rules = fields.JSONField(default=list)
    notes = fields.TextField(default="")

    class Meta:
        table = "persistence_baselines"
        ordering = ["-captured_at"]
        indexes = [
            ("project_id", "is_active_baseline"),
        ]
