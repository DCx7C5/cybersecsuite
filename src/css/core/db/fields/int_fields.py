from typing import override
from ipaddress import AddressValueError, IPv4Address
from tortoise.fields import BigIntField, IntField
from tortoise.validators import MaxValueValidator, MinValueValidator



class IPv4Field(BigIntField):
    """
    IPv4 address stored as BIGINT (decimal) in the database.
    - Python side: works with normal dotted string ("192.168.1.1")
    - Database side: stores as unsigned 32-bit integer (0 - 4294967295)
    - Benefits: smaller size, faster indexes, easy subnet/range queries
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(self._validate_ipv4)

    @staticmethod
    def _validate_ipv4(value: str | None):
        if value:
            try:
                IPv4Address(value)
            except AddressValueError:
                raise ValueError(f"Invalid IPv4 address: {value}")

    @override
    def to_db_value(self, value: str | None, instance) -> int | None:
        if value is None:
            return None
        return int(IPv4Address(value))

    @override
    def to_python_value(self, value: int | None) -> str | None:
        if value is None:
            return None
        return str(IPv4Address(value))


class NonNegativeIntField(IntField):
    """Integer field constrained to values >= 0."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(MinValueValidator(0))


class PositiveIntField(IntField):
    """Integer field constrained to values >= 1."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(MinValueValidator(1))


class PortField(IntField):
    """TCP/UDP port field constrained to 1..65535."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.extend([MinValueValidator(1), MaxValueValidator(65535)])
