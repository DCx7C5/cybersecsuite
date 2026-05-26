from css.core.db.models.base import BaseModel
from fields import LabelField
from models import TimestampMixin


class ApiServiceProvider(BaseModel, TimestampMixin):
    name = LabelField(max_length=255, unique=True, db_index=True)

