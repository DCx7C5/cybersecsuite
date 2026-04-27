"""
YARA Rule models — persistent storage for generated, optimized, and tested YARA rules.

Lifecycle:
  DRAFT → (yara_rule_generator.py) → TESTED → (yara_rule_optimizer.py) → OPTIMIZED → ACTIVE
                                           ↘ (yara_rule_tester.py) ↗
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import (
    YaraRuleStatus,
    YaraRuleSource,
    SeverityLevel,
    ConfidenceLevel,
)


class YaraRule(Model):
    """A YARA rule generated or imported during a forensic investigation."""

    id = fields.BigIntField(primary_key=True)
    rule_id = fields.CharField(max_length=100, unique=True, db_index=True,
                               description="Stable ID, e.g. YARA-20260407-0001")

    # Identity
    name = fields.CharField(max_length=255, db_index=True,
                            description="Rule name as it appears in the .yar file")
    description = fields.TextField(default="")
    author = fields.CharField(max_length=255, default="cybersec-agent")
    tags = fields.JSONField(default=list, description="Free-form tags, e.g. ['rootkit', 'ebpf']")

    # Content
    rule_text = fields.TextField(description="Full YARA rule source (one or more rules)")
    rule_file_path = fields.CharField(max_length=500, null=True,
                                      description="Path on disk, relative to project root")

    # Classification
    status = fields.CharEnumField(YaraRuleStatus, default=YaraRuleStatus.DRAFT, db_index=True)
    source = fields.CharEnumField(YaraRuleSource, default=YaraRuleSource.GENERATED, db_index=True)
    severity = fields.CharEnumField(SeverityLevel, default=SeverityLevel.MEDIUM, db_index=True)
    confidence = fields.CharEnumField(ConfidenceLevel, default=ConfidenceLevel.MEDIUM, db_index=True)

    # MITRE / IOC linkage
    mitre_techniques = fields.JSONField(default=list,
                                        description="MITRE ATT&CK technique IDs, e.g. ['T1055', 'T1014']")
    mitre_tactics = fields.JSONField(default=list,
                                     description="MITRE tactics, e.g. ['defense_evasion']")
    ioc_source_ids = fields.JSONField(default=list,
                                      description="IOCEntry.ioc_id values that generated this rule")

    # Session linkage
    generated_by_session = fields.ForeignKeyField(
        "models.ForensicSession",
        related_name="yara_rules_generated",
        null=True,
        on_delete=fields.SET_NULL,
        description="Session in which this rule was first generated",
    )
    project = fields.ForeignKeyField(
        "models.ForensicProject",
        related_name="yara_rules",
        null=True,
        on_delete=fields.SET_NULL,
        db_index=True
    )

    # Test results (populated by yara_rule_tester.py)
    last_tested_at = fields.DatetimeField(null=True)
    test_target = fields.CharField(max_length=500, null=True,
                                   description="Path or artifact that was scanned")
    test_hits = fields.IntField(default=0, description="True-positive hits from last test run")
    test_false_positives = fields.IntField(default=0)
    test_notes = fields.TextField(default="")

    # Optimization metadata (populated by yara_rule_optimizer.py)
    optimization_notes = fields.TextField(default="")
    performance_score = fields.FloatField(null=True,
                                          description="0.0–1.0: higher = faster / fewer FPs")

    # Lifecycle
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "yara_rules"
        ordering = ["-created_at"]
        indexes = [
            ("project_id", "status"),
            ("project_id", "severity"),
            ("source", "status"),
        ]

    def __str__(self):
        return f"YaraRule({self.rule_id}: {self.name} [{self.status}])"


class YaraTestRun(Model):
    """Individual test run record — one row per yara-test invocation."""

    id = fields.BigIntField(primary_key=True)
    run_id = fields.CharField(max_length=100, unique=True, db_index=True)

    rule = fields.ForeignKeyField(
        "models.YaraRule",
        related_name="test_runs",
        on_delete=fields.CASCADE,
    )
    session = fields.ForeignKeyField(
        "models.ForensicSession",
        related_name="yara_test_runs",
        null=True,
        on_delete=fields.SET_NULL,
    )

    target_path = fields.CharField(max_length=500, description="Scanned path / artifact")
    hits = fields.IntField(default=0)
    false_positives = fields.IntField(default=0)
    scan_duration_ms = fields.IntField(null=True)
    raw_output = fields.TextField(default="", description="Raw yara CLI output")
    verdict = fields.CharField(max_length=50, default="",
                               description="pass / fail / fp_heavy / inconclusive")
    run_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "yara_test_runs"
        ordering = ["-run_at"]
        indexes = [
            ("rule_id", "verdict"),
        ]

    def __str__(self):
        return f"YaraTestRun({self.run_id}: {self.verdict} on {self.target_path})"

