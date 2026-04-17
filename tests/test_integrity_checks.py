"""Tests for integrity checks — model FK consistency, fixture coverage, config validation."""

import pytest

from checks.integrity import run_all_checks, check_models, check_fixtures, check_config


class TestIntegrityChecks:
    """Test the integrity check system."""

    def test_run_all_checks_returns_dict(self):
        """Test that run_all_checks returns structured report."""
        report = run_all_checks()
        assert isinstance(report, dict)
        assert "models" in report
        assert "fixtures" in report
        assert "config" in report
        assert "summary" in report

    def test_summary_has_counts(self):
        """Test that summary contains error/warning counts."""
        report = run_all_checks()
        summary = report["summary"]
        assert "errors" in summary
        assert "warnings" in summary
        assert isinstance(summary["errors"], int)
        assert isinstance(summary["warnings"], int)


class TestModelCheck:
    """Test model FK consistency checking."""

    def test_check_models_returns_list(self):
        """Test that check_models returns list of findings."""
        findings = check_models()
        assert isinstance(findings, list)
        # Each finding should have level, check, message
        for finding in findings:
            assert "level" in finding
            assert "check" in finding
            assert "message" in finding
            assert finding["level"] in ["error", "warning", "info"]

    def test_model_findings_structure(self):
        """Test structure of model findings."""
        findings = check_models()
        for finding in findings:
            assert isinstance(finding["message"], str)
            assert len(finding["message"]) > 0


class TestFixtureCheck:
    """Test fixture file coverage checking."""

    def test_check_fixtures_returns_list(self):
        """Test that check_fixtures returns list of findings."""
        findings = check_fixtures()
        assert isinstance(findings, list)
        for finding in findings:
            assert "level" in finding
            assert "check" in finding
            assert "message" in finding


class TestConfigCheck:
    """Test configuration file consistency checking."""

    def test_check_config_returns_list(self):
        """Test that check_config returns list of findings."""
        findings = check_config()
        assert isinstance(findings, list)
        for finding in findings:
            assert "level" in finding
            assert "check" in finding
            assert "message" in finding

    def test_config_file_validation(self):
        """Test that config checks validate critical files."""
        findings = check_config()
        # Should check at least: mcp.json, docker-compose.yml, settings.json
        checks_performed = set(f["check"] for f in findings)
        assert len(checks_performed) > 0


class TestIntegrityCheckFiltering:
    """Test filtering and summarizing integrity findings."""

    def test_error_count_accuracy(self):
        """Test that error count matches actual errors."""
        report = run_all_checks()
        all_findings = report["models"] + report["fixtures"] + report["config"]
        error_findings = [f for f in all_findings if f["level"] == "error"]
        assert len(error_findings) == report["summary"]["errors"]

    def test_warning_count_accuracy(self):
        """Test that warning count matches actual warnings."""
        report = run_all_checks()
        all_findings = report["models"] + report["fixtures"] + report["config"]
        warning_findings = [f for f in all_findings if f["level"] == "warning"]
        assert len(warning_findings) == report["summary"]["warnings"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
