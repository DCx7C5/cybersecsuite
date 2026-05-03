from tortoise import fields
from tortoise.models import Model


class ApiServiceProvider(Model):
    id = fields.BigIntField(primary_key=True)
