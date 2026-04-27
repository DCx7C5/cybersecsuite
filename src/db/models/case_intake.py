"""
Phase 0 — Case Intake model.

Captures the initial problem statement, attack hypothesis, known facts,
scope constraints, and priority before any investigation phase begins.
Stored per-session so every investigation has a traceable origin record.
"""
from tortoise import fields

from db.models.enums import Severity, RedBlueMode
from db.models.scope import ScopedEntry


class CaseIntake(ScopedEntry):
    """Phase 0 case opening record — structured threat-hunting intake."""

    id = fields.IntField(primary_key=True)

    # Core intake fields
    title = fields.CharField(max_length=512, db_index=True)
    problem_statement = fields.TextField(
        description="What happened? What is the user concerned about?"
    )
    attack_hypothesis = fields.TextField(
        default="",
        description="Initial theory: suspected attack type, vector, or actor."
    )

    # Structured facts for threat hunting
    known_facts = fields.JSONField(
        default=list,
        description="List of confirmed facts: IPs, hashes, timestamps, symptoms."
    )
    suspected_iocs = fields.JSONField(
        default=list,
        description="Preliminary IOC candidates before formal triage."
    )
    affected_assets = fields.JSONField(
        default=list,
        description="Hosts, services, accounts, or network segments involved."
    )
    timeline_hints = fields.JSONField(
        default=list,
        description="Known timestamps: first seen, last seen, anomaly window."
    )

    # Scope and constraints
    scope_in = fields.JSONField(
        default=list,
        description="What IS in scope for investigation."
    )
    scope_out = fields.JSONField(
        default=list,
        description="What is explicitly OUT of scope."
    )
    priority = fields.CharEnumField(
        Severity, default=Severity.MEDIUM, db_index=True,
        description="Case priority / urgency level."
    )
    mode = fields.CharEnumField(
        RedBlueMode, default=RedBlueMode.BLUE, db_index=True,
        description="Team posture for this case."
    )

    # Enrichment
    mitre_hypotheses = fields.JSONField(
        default=list,
        description="Suspected MITRE ATT&CK techniques (T-codes)."
    )
    data_sources = fields.JSONField(
        default=list,
        description="Available data sources: pcaps, logs, disk images, memory dumps."
    )
    tags = fields.JSONField(default=list)
    analyst_notes = fields.TextField(default="")

    # Lifecycle
    opened_by = fields.CharField(max_length=256, default="user")
    reviewed_by = fields.CharField(max_length=256, default="")
    closed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "case_intakes"
        ordering = ["-created_at"]
        indexes = [
            ("project_id", "priority"),
            ("session_id", "created_at"),
        ]

