"""Strict frontmatter + body parser using YAML.

``FrontMatterSerializer`` splits Markdown on ``---`` delimiters, parses
the frontmatter block as YAML, and returns a ``BaseFrontmatterHeader``.
Output is deterministic: sorted YAML keys + body unchanged.
"""

from pathlib import Path
from typing import override

import msgspec.yaml

from css.core.base.frontmatter_header import BaseFrontmatterHeader
from css.core.base.serializer import BaseSerializer


_FM_DELIMITER = "---"
_DELIMITER_LEN = len(_FM_DELIMITER)


class FrontMatterSerializer(BaseSerializer):
    """Serialize/deserialize YAML frontmatter + body documents."""

    def __init__(self, header: BaseFrontmatterHeader) -> None:
        self.header = header

    @classmethod
    @override
    def from_string(cls, data: str) -> FrontMatterSerializer:
        """Parse a string with ``---<yaml>---<body>`` layout."""
        stripped = data.lstrip()
        if not stripped.startswith(_FM_DELIMITER):
            raise ValueError("Document must start with '---' frontmatter delimiter")

        rest = stripped[_DELIMITER_LEN:]
        end_delimiter = rest.find(_FM_DELIMITER)
        if end_delimiter == -1:
            raise ValueError("Missing closing '---' frontmatter delimiter")

        yaml_block = rest[:end_delimiter].strip()
        body = rest[end_delimiter + _DELIMITER_LEN:].lstrip("\n\r")

        frontmatter = msgspec.yaml.decode(yaml_block) or {}

        header = BaseFrontmatterHeader(
            name=str(frontmatter.get("name", "")),
            description=str(frontmatter.get("description", "")),
            hash=str(frontmatter.get("hash", "")),
            signature=str(frontmatter.get("signature", "")),
            body=body,
        )
        return cls(header)

    @classmethod
    @override
    def from_file(cls, path: str | Path) -> FrontMatterSerializer:
        raw = Path(path).read_text(encoding="utf-8")
        return cls.from_string(raw)

    @override
    def to_string(self) -> str:
        """Serialize with deterministic YAML frontmatter."""
        fm = {
            "name": self.header.name,
            "description": self.header.description,
        }
        if self.header.hash:
            fm["hash"] = self.header.hash
        if self.header.signature:
            fm["signature"] = self.header.signature

        yaml_block = msgspec.yaml.encode(fm).decode("utf-8").strip()
        body = self.header.body or ""
        return f"{_FM_DELIMITER}\n{yaml_block}\n{_FM_DELIMITER}\n{body}"

