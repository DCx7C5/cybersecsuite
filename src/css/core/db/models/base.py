from tortoise.fields import BigIntField
from tortoise.models import Model



class BaseModel(Model):
    id = BigIntField(primary_key=True)
