from tortoise import Model, fields



class PublicApi(Model):
    id = fields.IntField(primary_key=True)
    url = fields.CharField(max_length=256, unique=True)
    description = fields.CharField()