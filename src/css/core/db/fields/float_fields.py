from tortoise.fields import FloatField
from tortoise.validators import MinValueValidator, MaxValueValidator


class NonNegativeFloatField(FloatField):
    """Float field constrained to values >= 0."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(MinValueValidator(0.0))


class UnitIntervalFloatField(FloatField):
    """Float field constrained to values in the [0.0, 1.0] range."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.extend([
            MinValueValidator(0.0),
            MaxValueValidator(1.0),
        ])


class TemperatureFloatField(FloatField):
    """Float field constrained to model-temperature range [0.0, 2.0]."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.extend([
            MinValueValidator(0.0),
            MaxValueValidator(2.0),
        ])


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
