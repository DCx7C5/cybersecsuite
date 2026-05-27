"""Markdown serializer — inherits frontmatter parsing.

``MarkdownSerializer`` extends ``FrontMatterSerializer`` with the same
``from_string`` / ``to_string`` / ``from_file`` / ``to_file`` contract
for full ``.md`` documents with YAML frontmatter.
"""

from css.core.serializers.frontmatter import FrontMatterSerializer


class MarkdownSerializer(FrontMatterSerializer):
    """Serialize/deserialize Markdown documents with YAML frontmatter.

    All parsing and serialization behaviour is inherited from
    ``FrontMatterSerializer``. This class exists as a semantic alias so
    that callers can write ``MarkdownSerializer.from_file(...)`` for
    ``.md`` files and ``FrontMatterSerializer.from_file(...)`` for
    generic frontmatter documents.
    """

