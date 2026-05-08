from tortoise.fields import FloatField
from tortoise.validators import MinValueValidator, MaxValueValidator



class QualityScoreField(FloatField):
    """
    A FloatField that validates that the value is between 0.0 and 1.0.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.extend([
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ])

    
