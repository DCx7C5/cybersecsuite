"""
Network models — IP addresses, domains, hosts, certificates, connections.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.scope import ScopedEntry


class IPAddress(Model):
    id = fields.BigIntField(primary_key=True)
    address = fields.CharField(max_length=45, unique=True, db_index=True)
    version = fields.SmallIntField(default=4)
    is_private = fields.BooleanField(default=False, db_index=True)
    geo_country = fields.CharField(max_length=3, default="")
    first_seen_at = fields.DatetimeField(auto_now_add=True)
    last_seen_at = fields.DatetimeField(auto_now=True)
    notes = fields.TextField(default="")

    class Meta:
        table = "ip_addresses"
        indexes = [("version",), ("geo_country",)]


class Host(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    hostname = fields.CharField(max_length=253, db_index=True)
    os_name = fields.CharField(max_length=128, default="")
    os_version = fields.CharField(max_length=128, default="")
    architecture = fields.CharField(max_length=32, default="")
    is_localhost = fields.BooleanField(default=False, db_index=True)
    is_systemhost = fields.BooleanField(default=False, db_index=True)
    is_target = fields.BooleanField(default=True, db_index=True)
    is_compromised = fields.BooleanField(default=False, db_index=True)
    notes = fields.TextField(default="")

    ip_addresses: fields.ManyToManyRelation["IPAddress"] = fields.ManyToManyField(
        "models.IPAddress", related_name="hosts", through="host_ip_addresses"
    )

    class Meta:
        table = "hosts"
        unique_together = [("project_id", "hostname")]


class Domain(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, db_index=True)
    tld = fields.CharField(max_length=63, default="")
    host = fields.ForeignKeyField("models.Host", related_name="domains", null=True, on_delete=fields.SET_NULL)
    is_active = fields.BooleanField(default=True, db_index=True)
    notes = fields.TextField(default="")

    class Meta:
        table = "domains"
        unique_together = [("project_id", "name")]


class Certificate(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    subject_cn = fields.CharField(max_length=255, db_index=True)
    sha256_fingerprint = fields.CharField(max_length=64, unique=True, db_index=True)
    not_after = fields.DatetimeField(null=True)
    is_expired = fields.BooleanField(default=False, db_index=True)
    domain = fields.ForeignKeyField("models.Domain", related_name="certificates", null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "certificates"


class NetworkConnection(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    src_ip = fields.CharField(max_length=45, db_index=True)
    dst_ip = fields.CharField(max_length=45, db_index=True)
    src_port = fields.IntField(default=0)
    dst_port = fields.IntField(default=0, db_index=True)
    protocol = fields.CharField(max_length=16, default="tcp", db_index=True)
    state = fields.CharField(max_length=32, default="")
    is_suspicious = fields.BooleanField(default=False, db_index=True)
    notes = fields.TextField(default="")

    class Meta:
        table = "network_connections"
        indexes = [("src_ip", "dst_ip"), ("dst_port",)]
