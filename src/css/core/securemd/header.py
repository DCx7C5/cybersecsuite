"""SecureMD FrontMatterHeader — re-export of the canonical base type."""

from css.core.base.frontmatter_header import BaseFrontmatterHeader


class FrontMatterHeader(BaseFrontmatterHeader, frozen=True):
    """SecureMD frontmatter header.

    Inherits all behavior from ``BaseFrontmatterHeader``, including
    config-aware sign/verify/verify_and_get_body and minimum-required-field
    enforcement.
    """

