"""Format serializer base contracts — string/file serialization boundary.

Every format-specific serializer (JSON, YAML frontmatter, Markdown, …)
inherits from ``BaseSerializer``, which defines four fundamental
operations:

* ``from_string(cls, data: str)`` — parse string input
* ``from_file(cls, path: str | Path)`` — read & parse a file
* ``to_string(self) -> str`` — serialize to string
* ``to_file(self, path: str | Path)`` — serialize to file

Subclasses **must** override ``from_string`` and ``to_string``; the file
methods default to delegating to the string methods.
"""

from pathlib import Path


class BaseSerializer:
    """Abstract base for format-specific serializers.

    Provides the canonical serialization contract:

    * ``from_string`` / ``from_file`` for deserialization
    * ``to_string`` / ``to_file`` for serialization

    The file variants default to delegating to their string counterparts.
    Subclasses **must** implement ``from_string`` and ``to_string``.
    """

    @classmethod
    def from_string(cls, data: str) -> BaseSerializer:
        """Parse *data* (a string) into the serializer.

        Subclasses must override this method.
        """
        raise NotImplementedError

    @classmethod
    def from_file(cls, path: str | Path) -> BaseSerializer:
        """Read the file at *path* and parse its contents.

        Default implementation: read the file as UTF-8 and call
        ``from_string``. Override when you need binary I/O or streaming.
        """
        raw = Path(path).read_text(encoding="utf-8")
        return cls.from_string(raw)

    def to_string(self) -> str:
        """Serialize to a string.

        Subclasses must override this method.
        """
        raise NotImplementedError

    def to_file(self, path: str | Path) -> None:
        """Serialize into the file at *path*.

        Default implementation: call ``to_string`` and write the result
        as UTF-8. Override when you need binary I/O or streaming.
        """
        Path(path).write_text(self.to_string(), encoding="utf-8")


class BaseModelSerializer(BaseSerializer):
    """Base for ORM model ↔ format serializers — adds domain conversion.

    Extends ``BaseSerializer`` with two additional operations for
    converting ORM model instances to/from serializable form:

    * ``from_model(cls, model: object)`` — construct from an ORM model
      instance.
    * ``to_model(self) -> object`` — convert back to an ORM model
      instance.

    Subclasses **must** override ``from_model`` and ``to_model``, as
    well as ``from_string`` and ``to_string`` from the parent.
    """

    @classmethod
    def from_model(cls, model: object) -> BaseModelSerializer:
        """Construct a serializer from an ORM model instance.

        Subclasses must override this method.
        """
        raise NotImplementedError

    def to_model(self) -> object:
        """Convert the serializer back to an ORM model instance.

        Subclasses must override this method.
        """
        raise NotImplementedError
