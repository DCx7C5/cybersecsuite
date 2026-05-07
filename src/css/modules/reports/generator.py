"""Report rendering for Markdown, HTML, and PDF-like output."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any


class ReportGenerator:
    """Generates reports from structured cybersecurity data."""

    def render_markdown(self, title: str, sections: list[dict[str, Any]]) -> str:
        lines = [f"# {title}", "", f"_Generated: {datetime.utcnow().isoformat()}_", ""]
        for section in sections:
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(str(section.get("content", "")))
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def render_html(self, title: str, sections: list[dict[str, Any]]) -> str:
        body_sections = []
        for section in sections:
            body_sections.append(
                f"<section><h2>{escape(section['title'])}</h2><pre>{escape(str(section.get('content', '')))}</pre></section>"
            )
        return (
            "<!doctype html>"
            "<html><head><meta charset='utf-8'><title>"
            f"{escape(title)}"
            "</title></head><body>"
            f"<h1>{escape(title)}</h1>"
            f"<p>Generated: {escape(datetime.utcnow().isoformat())}</p>"
            f"{''.join(body_sections)}"
            "</body></html>"
        )

    def render_pdf(self, title: str, sections: list[dict[str, Any]]) -> bytes:
        # Placeholder binary representation. Can be swapped with real PDF backend later.
        text = self.render_markdown(title=title, sections=sections)
        return text.encode("utf-8")
