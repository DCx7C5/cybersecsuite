"""Strict JSON serializer — ``BaseSerializer`` for JSON format.

Uses ``msgspec.json`` for fast, validated encoding/decoding.
"""

from pathlib import Path
from typing import Any, override

import msgspec

from css.core.base.serializer import BaseSerializer


class JSONSerializer(BaseSerializer):
    """Strict JSON encode/decode serializer backed by ``msgspec``."""

    def __init__(self, data: Any = None) -> None:
        self._data = data

    @classmethod
    @override
    def from_string(cls, data: str) -> JSONSerializer:
        return cls(msgspec.json.decode(data.encode("utf-8")))

    @classmethod
    @override
    def from_file(cls, path: str | Path) -> JSONSerializer:
        raw = Path(path).read_bytes()
        return cls(msgspec.json.decode(raw))

    @override
    def to_string(self) -> str:
        return msgspec.json.format(
            msgspec.json.encode(self._data),
            indent=2,
        ).decode("utf-8")

    @override
    def to_file(self, path: str | Path) -> None:
        Path(path).write_bytes(msgspec.json.format(
            msgspec.json.encode(self._data),
            indent=2,
        ))

    @property
    def data(self) -> Any:
        return self._data

