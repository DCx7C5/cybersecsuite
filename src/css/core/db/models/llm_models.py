
from tortoise.fields import ManyToManyField
from tortoise.indexes import Index
from css.core.db.fields.char_fields import DescriptionField, NameField
from css.core.db.models.base import BaseModel
from .mixins import TimestampMixin


class LLMModel(BaseModel, TimestampMixin):
    """
    Database model for LLM models.
    """
    name = NameField(unique=True)
    description = DescriptionField(null=True)
    capabilities = ManyToManyField(
        to='Capability',
        related_name='llm_models',
        through='llm_model_capability',
        through_fields=('llm_model', 'capability')
    )



    class Meta:
        table = "llm_model"
        table_verbose = "LLM Model"
        table_verbose_plural = "LLM Models"
        ordering = ["id", "name"]
        indexes = (
            Index(fields=["name", "id"]),
        )
        unique_together = (
            ("name", "version"),

        )