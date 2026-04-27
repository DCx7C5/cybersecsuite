from tortoise import Model, fields



class PublicApi(Model):
    id = fields.IntField(primary_key=True)
    url = fields.CharField(max_length=256, unique=True)
    description = fields.CharField(max_length=512)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    auth_methods = fields.ManyToManyField(
        "models.AuthMethod",
        related_name="public_apis",
        through="publicapi_authmethod",
    )
    