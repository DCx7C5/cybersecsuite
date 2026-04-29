"""
Tortoise ORM settings — consumed by external tooling (aerich, etc).
Runtime config is built dynamically in db.bootstrap.get_tortoise_config().
"""
from db.bootstrap import get_tortoise_config

TORTOISE_ORM = get_tortoise_config()

