from typing import override
import re
from ipaddress import IPv6Address, AddressValueError
from pathlib import Path
from urllib.parse import urlparse

from tortoise.fields import CharField, TextField


class NameField(CharField):
    """
    Identifier-style field: validates that the value is a valid Python identifier and is unique.

    Use for programmatic identifiers (e.g., tool names, scope keys, model codenames).
    For human-readable display names, use ``LabelField`` instead.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique = True
        self.validators.append(self._validate_name)

    @staticmethod
    def _validate_name(value: str | None):
        if value is None:
            return
        if not value.isascii():
            raise ValueError(f"Name must contain only ASCII characters: {value}")
        if not value.isidentifier():
            raise ValueError(f"Invalid Python identifier: {value}")


class LabelField(CharField):
    """
    Display-name / label field for human-readable names.

    Unlike ``NameField``, this does not enforce Python-identifier rules or uniqueness.
    Use for entity names that are displayed to users (project names, webhook labels,
    human names, etc.). Input validation (trimming, sanitization) belongs at the
    application boundary, not in the ORM field layer.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)


class UrlField(CharField):
    """
    A CharField that validates that the value is a valid URL.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(self._validate_url)

    @staticmethod
    def _validate_url(value: str | None):
        if value is None:
            return
        if not value.isascii():
            raise ValueError(f"URL must contain only ASCII characters: {value}")
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"Invalid URL: {value}")


class PathField(CharField):
    """
    A CharField that validates that the value is a valid path.
    """

    def __init__(self, *args, must_exist: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_exist = must_exist
        self.validators.append(self._validate_path)

    def _validate_path(self, value: str | None):
        if value is None:
            return
        if not value.isascii():
            raise ValueError(f"Path must contain only ASCII characters: {value}")
        p = Path(value)
        if self.must_exist and not p.exists():
            raise ValueError(f"Path does not exist: {value}")


class DescriptionField(TextField):
    """
    Clean description field with sensible defaults.
    - Default max_length = 2000 characters
    - Automatically strips whitespace
    - Allows Unicode (international content, markdown, etc.)
    """
    def __init__(self, max_length: int = 2000, *args, **kwargs):
        super().__init__(*args, max_length=max_length, **kwargs)

    @override
    def to_db_value(self, value: str | None, instance) -> str | None:
        if isinstance(value, str):
            value = value.strip()
        return super().to_db_value(value, instance)


class IPv6Field(CharField):
    """
    Validated IPv6 address field (ASCII only).
    Max length 45
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 45)
        super().__init__(*args, **kwargs)
        self.validators.append(self._validate_ipv6)

    @staticmethod
    def _validate_ipv6(value: str | None):
        if value:
            if not value.isascii():
                raise ValueError(f"IPv6 address must contain only ASCII characters: {value}")
            try:
                IPv6Address(value)
            except AddressValueError:
                raise ValueError(f"Invalid IPv6 address: {value}")


class VersionField(CharField):
    """
    Semantic Version field with default 0.1.0.
    - Stores as string (e.g. "1.2.3", "2.0.0-beta.1")
    - Validates basic semver format (major.minor.patch)
    - Default value = "0.1.0"
    """
    SEMVER_REGEX = re.compile(
        r'^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
    )

    def __init__(self, *args, max_length: int = 32, **kwargs):
        kwargs.setdefault("default", "0.1.0")
        super().__init__(*args, max_length=max_length, **kwargs)
        self.validators.append(self._validate_version)

    @staticmethod
    def _validate_version(value: str | None):
        if value and not VersionField.SEMVER_REGEX.match(value):
            raise ValueError(
                f"Invalid semantic version: {value}. "
                "Expected format: major.minor.patch (e.g. 1.2.3 or 2.0.0-beta)"
            )


class SHA512SumField(CharField):
    """
    SHA-512 checksum field (hex encoded).
    - Fixed length: 128 characters
    - Validates that value is a valid SHA-512 hex digest
    - Recommended for storing checksums of model files, prompts, results, etc.
    """
    SHA512_REGEX = re.compile(r'^[0-9a-fA-F]{128}$')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 128)
        super().__init__(*args, **kwargs)
        self.validators.append(self._validate_sha512)

    @staticmethod
    def _validate_sha512(value: str | None):
        if value and not SHA512SumField.SHA512_REGEX.match(value):
            raise ValueError(
                f"Invalid SHA-512 sum: {value}. "
                "Must be exactly 128 hexadecimal characters (0-9, a-f)."
            )


class SlugField(CharField):
    """
    URL-friendly slug field.
    - Lowercase letters, numbers, hyphens (and optional underscores)
    - Default max_length = 100
    - Automatically converts to lowercase on save
    """
    SLUG_REGEX = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

    def __init__(self, allow_underscores: bool = False, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        super().__init__(*args, **kwargs)

        if allow_underscores:
            self.SLUG_REGEX = re.compile(r'^[a-z0-9_-]+$')

        self.validators.append(self._validate_slug)

    @override
    def to_db_value(self, value: str | None, instance) -> str | None:
        if value:
            value = value.lower().strip()
        return super().to_db_value(value, instance)

    @staticmethod
    def _validate_slug(value: str | None):
        if value and not SlugField.SLUG_REGEX.match(value):
            raise ValueError(
                f"Invalid slug: {value}. "
                "Only lowercase letters, numbers, and hyphens allowed "
                "(use allow_underscores=True to permit underscores)."
            )
