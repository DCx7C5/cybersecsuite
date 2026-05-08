from tortoise import fields
from css.core.db.models.base import BaseModel


class ApiServiceProvider(BaseModel):
    id = fields.BigIntField(primary_key=True)
