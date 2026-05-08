from decimal import Decimal, InvalidOperation

from tortoise.fields import DecimalField
from tortoise.validators import MaxValueValidator, MinValueValidator


class CostField(DecimalField):
    """
    Decimal field for non-negative costs/prices.
    - Backed by PostgreSQL NUMERIC(12,8)
    - Non-negative, exact arithmetic (no float)
    - Rejects values that exceed precision/scale constraints
    """

    def __init__(self, *args, **kwargs):
        max_digits = kwargs.setdefault("max_digits", 12)
        decimal_places = kwargs.setdefault("decimal_places", 8)
        super().__init__(*args, **kwargs)
        self.validators.append(MinValueValidator(Decimal("0")))
        max_integral_digits = max_digits - decimal_places
        max_value = Decimal(
            f"{'9' * max_integral_digits}.{('9' * decimal_places) if decimal_places else '0'}"
        )
        self.validators.append(MaxValueValidator(max_value))

    def _coerce_decimal(self, value: Decimal | str | int | float | None) -> Decimal | None:
        """

        :param value:
        :return:
        """
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        try:
            # str() avoids binary floating representation artifacts from float.
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid decimal value: {value!r}") from exc

    def _validate_postgres_numeric_bounds(self, value: Decimal) -> None:
        """

        :param value:
        :return:
        """
        if not value.is_finite():
            raise ValueError(f"Invalid cost value {value!r}; NaN/Infinity are not allowed.")

        exponent = value.as_tuple().exponent
        scale = -exponent if exponent < 0 else 0
        if scale > self.decimal_places:
            raise ValueError(
                "Invalid cost precision for "
                f"{value!r}; expected up to {self.decimal_places} decimal places."
            )

    def _quantize(self, value: Decimal) -> Decimal:
        """

        :param value:
        :return:
        """
        quantum = Decimal(1).scaleb(-self.decimal_places)
        try:
            return value.quantize(quantum)
        except InvalidOperation as exc:
            raise ValueError(
                "Invalid cost precision for "
                f"{value!r}; expected up to {self.decimal_places} decimal places."
            ) from exc

    def to_db_value(self, value: Decimal | str | int | float | None, instance) -> Decimal | None:
        """

        :param value:
        :param instance:
        :return:
        """
        decimal_value = self._coerce_decimal(value)
        if decimal_value is None:
            return None
        self._validate_postgres_numeric_bounds(decimal_value)
        normalized = self._quantize(decimal_value)
        return super().to_db_value(normalized, instance)

    def to_python_value(self, value: Decimal | str | int | float | None) -> Decimal | None:
        """

        :param value:
        :return:
        """
        decimal_value = self._coerce_decimal(value)
        if decimal_value is None:
            return None
        self._validate_postgres_numeric_bounds(decimal_value)
        return self._quantize(decimal_value)
