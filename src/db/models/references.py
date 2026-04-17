"""Cross-reference intelligence models that belong together."""

from tortoise import fields
from tortoise.models import Model


class CVECWEReference(Model):
    """Many-to-many mapping between CVE and CWE records."""

    id = fields.IntField(primary_key=True)
    cve = fields.ForeignKeyField("models.CVEIntel", related_name="cwe_links")
    cwe = fields.ForeignKeyField("models.CWEIntel", related_name="cve_links")
    source = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_cve_cwe_refs"
        unique_together = (("cve", "cwe"),)


class CVEMitreTechniqueReference(Model):
    """Many-to-many mapping between CVE and MITRE technique records."""

    id = fields.IntField(primary_key=True)
    cve = fields.ForeignKeyField("models.CVEIntel", related_name="mitre_links")
    technique = fields.ForeignKeyField("models.MitreTechniqueIntel", related_name="cve_links")
    source = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_cve_mitre_refs"
        unique_together = (("cve", "technique"),)


class CWECAPECReference(Model):
    """Mapping between CWE weaknesses and CAPEC attack patterns."""

    id = fields.IntField(primary_key=True)
    cwe = fields.ForeignKeyField("models.CWEIntel", related_name="capec_links")
    capec = fields.ForeignKeyField("models.CapecAttackPatternIntel", related_name="cwe_links")
    source = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_cwe_capec_refs"
        unique_together = (("cwe", "capec"),)


class CAPECMitreTechniqueReference(Model):
    """Mapping between CAPEC attack patterns and ATT&CK techniques."""

    id = fields.IntField(primary_key=True)
    capec = fields.ForeignKeyField("models.CapecAttackPatternIntel", related_name="mitre_links")
    technique = fields.ForeignKeyField("models.MitreTechniqueIntel", related_name="capec_links")
    source = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_capec_mitre_refs"
        unique_together = (("capec", "technique"),)


class ThreatActorTechniqueReference(Model):
    """Mapping between threat actors and techniques they are associated with."""

    id = fields.IntField(primary_key=True)
    actor = fields.ForeignKeyField("models.MitreThreatActorIntel", related_name="technique_links")
    technique = fields.ForeignKeyField("models.MitreTechniqueIntel", related_name="actor_links")
    confidence = fields.FloatField(null=True)
    evidence = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_actor_technique_refs"
        unique_together = (("actor", "technique"),)


class ThreatActorSoftwareReference(Model):
    """Mapping between threat actors and the software families they use."""

    id = fields.IntField(primary_key=True)
    actor = fields.ForeignKeyField("models.MitreThreatActorIntel", related_name="software_links")
    software = fields.ForeignKeyField("models.MitreSoftwareFamilyIntel", related_name="actor_links")
    relationship_type = fields.CharField(max_length=64, default="uses")
    confidence = fields.FloatField(null=True)
    evidence = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_actor_software_refs"
        unique_together = (("actor", "software", "relationship_type"),)


class SoftwareTechniqueReference(Model):
    """Mapping between ATT&CK software families and techniques they use."""

    id = fields.IntField(primary_key=True)
    software = fields.ForeignKeyField("models.MitreSoftwareFamilyIntel", related_name="technique_links")
    technique = fields.ForeignKeyField("models.MitreTechniqueIntel", related_name="software_links")
    relationship_type = fields.CharField(max_length=64, default="uses")
    confidence = fields.FloatField(null=True)
    evidence = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_software_technique_refs"
        unique_together = (("software", "technique", "relationship_type"),)


