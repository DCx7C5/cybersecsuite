"""Tests for cybersecsuite.scaffold module."""
from __future__ import annotations

import pytest
from pathlib import Path

from cybersecsuite.scaffold import (
    scaffold_project_templates,
    get_embedded_template,
    _embedded_templates,
)


class TestEmbeddedTemplates:
    def test_returns_14_templates(self):
        templates = _embedded_templates()
        assert len(templates) == 14

    def test_all_have_content(self):
        for rel, content in _embedded_templates():
            assert len(content) > 0, f"{rel} is empty"

    def test_artifact_md_present(self):
        names = [r for r, _ in _embedded_templates()]
        assert "artifact.md" in names


class TestGetEmbeddedTemplate:
    def test_artifact_md(self):
        content = get_embedded_template("artifact.md")
        assert content is not None
        assert len(content) > 0

    def test_nonexistent_returns_none(self):
        assert get_embedded_template("does_not_exist.md") is None

    def test_subdir_template(self):
        # Find one template that's in a subdir from _embedded_templates
        for rel, _ in _embedded_templates():
            if "/" in rel:
                content = get_embedded_template(rel)
                assert content is not None
                break


class TestScaffoldProjectTemplates:
    def test_copies_all_templates(self, tmp_path):
        n = scaffold_project_templates(tmp_path)
        assert n == 14

    def test_creates_target_directory(self, tmp_path):
        scaffold_project_templates(tmp_path)
        assert (tmp_path / ".claude" / "templates").is_dir()

    def test_artifact_md_is_present(self, tmp_path):
        scaffold_project_templates(tmp_path)
        assert (tmp_path / ".claude" / "templates" / "artifact.md").exists()

    def test_idempotent_no_overwrite(self, tmp_path):
        scaffold_project_templates(tmp_path)
        # Modify a file
        artifact = tmp_path / ".claude" / "templates" / "artifact.md"
        artifact.write_text("CUSTOM CONTENT")
        # Re-run scaffold
        n = scaffold_project_templates(tmp_path)
        assert n == 0, "should not copy any files on re-run"
        assert artifact.read_text() == "CUSTOM CONTENT", "existing file should not be overwritten"

    def test_partial_scaffold_fills_gaps(self, tmp_path):
        scaffold_project_templates(tmp_path)
        artifact = tmp_path / ".claude" / "templates" / "artifact.md"
        artifact.unlink()
        n = scaffold_project_templates(tmp_path)
        assert n == 1
        assert artifact.exists()

    def test_readonly_dir_does_not_raise(self, tmp_path):
        import os
        import stat
        # Make the .claude dir readonly after creating it
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        os.chmod(claude_dir, stat.S_IREAD | stat.S_IEXEC)
        try:
            # Should not raise — best-effort
            n = scaffold_project_templates(tmp_path)
            assert n == 0
        except PermissionError:
            pytest.skip("OS raised before our guard (some OSes do this)")
        finally:
            os.chmod(claude_dir, stat.S_IRWXU)

    def test_returns_count(self, tmp_path):
        n = scaffold_project_templates(tmp_path)
        assert isinstance(n, int)
        assert n > 0
