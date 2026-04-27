"""
tests/test_src_cleanup.py
─────────────────────────────────────────────────────────────────────────────
Regression tests for the src/ cleanup changes:

  • scripts/fix_skills.py and worktree-session-manager.py moved to scripts/
  • src/dashboard/api/opensearch_stats.py renamed to openobserve_stats.py
  • src/hooks/*.md (6 hook docs) moved to docs/hooks/
  • Dead code removed: src/db/opensearch/, src/a2a/checks/, llm/db::persist_call(),
    src/llm/schema.sql, src/dashboard/templates/_panels.py.bak
  • src/manage/_commands.py import updated to `from checks.integrity import …`
  • docs/architecture/flowchart.md created

All tests are fast (no DB, no Docker, no network calls).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Generator

import pytest

# ── Resolve project root ──────────────────────────────────────────────────────
# conftest.py already adds src/ to sys.path; derive PROJECT_ROOT from __file__
# so the file works even when run in isolation.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
SRC_ROOT: Path = PROJECT_ROOT / "src"

# Guarantee src/ is on the path for all import tests in this module.
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


# ══════════════════════════════════════════════════════════════════════════════
# §1  FILE-LOCATION / STRUCTURE TESTS
#     Marked `integrity` — pure filesystem assertions, zero imports.
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integrity
class TestScriptsMoved:
    """Scripts must live in scripts/, NOT in the repo root."""

    def test_worktree_session_manager_in_scripts(self) -> None:
        """scripts/worktree-session-manager.py must exist after the move."""
        target = PROJECT_ROOT / "scripts" / "worktree-session-manager.py"
        assert target.exists(), f"Expected file at {target}"

    def test_fix_skills_in_scripts(self) -> None:
        """scripts/fix_skills.py must exist after the move."""
        target = PROJECT_ROOT / "scripts" / "fix_skills.py"
        assert target.exists(), f"Expected file at {target}"

    def test_worktree_session_manager_not_at_root(self) -> None:
        """worktree-session-manager.py must NOT remain at the repo root."""
        stale = PROJECT_ROOT / "worktree-session-manager.py"
        assert not stale.exists(), (
            f"Stale root-level script found at {stale}; should be in scripts/"
        )

    def test_fix_skills_not_at_root(self) -> None:
        """fix_skills.py must NOT remain at the repo root."""
        stale = PROJECT_ROOT / "fix_skills.py"
        assert not stale.exists(), (
            f"Stale root-level script found at {stale}; should be in scripts/"
        )


@pytest.mark.integrity
class TestDashboardApiRename:
    """openobserve_stats.py must exist; the old opensearch_stats.py must not."""

    def test_openobserve_stats_exists(self) -> None:
        """src/dashboard/api/openobserve_stats.py must be present."""
        target = SRC_ROOT / "dashboard" / "api" / "openobserve_stats.py"
        assert target.exists(), f"Renamed module not found at {target}"

    def test_opensearch_stats_removed(self) -> None:
        """src/dashboard/api/opensearch_stats.py must not exist (old name)."""
        stale = SRC_ROOT / "dashboard" / "api" / "opensearch_stats.py"
        assert not stale.exists(), (
            f"Old module name still present at {stale}; should have been renamed"
        )


@pytest.mark.integrity
class TestHookDocsMoved:
    """Six hook Markdown docs must be under docs/hooks/, NOT src/hooks/."""

    _HOOK_DOCS: tuple[str, ...] = (
        "RootCommandExecuted.md",
        "SessionEnd.md",
        "SessionStart.md",
        "YaraRuleGeneration.md",
        "YaraRuleOptimization.md",
        "YaraRuleTesting.md",
    )

    @pytest.mark.parametrize("filename", _HOOK_DOCS)
    def test_hook_doc_exists_in_docs_hooks(self, filename: str) -> None:
        """docs/hooks/<filename> must exist."""
        target = PROJECT_ROOT / "docs" / "hooks" / filename
        assert target.exists(), f"Hook doc not found at {target}"

    @pytest.mark.parametrize("filename", _HOOK_DOCS)
    def test_hook_doc_absent_from_src_hooks(self, filename: str) -> None:
        """src/hooks/<filename> must NOT exist (was moved to docs/hooks/)."""
        stale = SRC_ROOT / "hooks" / filename
        assert not stale.exists(), (
            f"Stale hook doc still at {stale}; should have been moved to docs/hooks/"
        )


@pytest.mark.integrity
class TestDeadCodeRemoved:
    """Deleted modules / directories / files must not be present."""

    def test_db_opensearch_dir_removed(self) -> None:
        """src/db/opensearch/ directory must not exist."""
        stale_dir = SRC_ROOT / "db" / "opensearch"
        assert not stale_dir.exists(), (
            f"Dead directory {stale_dir} still present; should have been deleted"
        )

    def test_a2a_checks_dir_removed(self) -> None:
        """src/a2a/checks/ directory must not exist."""
        stale_dir = SRC_ROOT / "a2a" / "checks"
        assert not stale_dir.exists(), (
            f"Dead directory {stale_dir} still present; should have been deleted"
        )

    def test_llm_schema_sql_removed(self) -> None:
        """src/llm/schema.sql must not exist."""
        stale = SRC_ROOT / "llm" / "schema.sql"
        assert not stale.exists(), (
            f"Dead file {stale} still present; should have been deleted"
        )

    def test_panels_bak_removed(self) -> None:
        """src/dashboard/templates/_panels.py.bak must not exist."""
        stale = SRC_ROOT / "dashboard" / "templates" / "_panels.py.bak"
        assert not stale.exists(), (
            f"Backup file {stale} still present; should have been deleted"
        )


@pytest.mark.integrity
class TestArchitectureDocCreated:
    """The Mermaid architecture flowchart must be present."""

    def test_flowchart_md_exists(self) -> None:
        """docs/architecture/flowchart.md must exist."""
        target = PROJECT_ROOT / "docs" / "architecture" / "flowchart.md"
        assert target.exists(), f"Architecture flowchart not found at {target}"


# ══════════════════════════════════════════════════════════════════════════════
# §2  IMPORT CORRECTNESS TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestOpenobserveStatsImport:
    """dashboard.api.openobserve_stats must be importable and export api_opensearch."""

    def test_direct_module_import(self) -> None:
        """Import directly from the renamed module path."""
        # Guard against stale cached module from any prior partial import
        mod_name = "dashboard.api.openobserve_stats"
        module: ModuleType = importlib.import_module(mod_name)
        assert hasattr(module, "api_opensearch"), (
            f"{mod_name} must export 'api_opensearch'"
        )

    def test_api_opensearch_is_callable(self) -> None:
        """api_opensearch imported from module must be an async callable."""
        import inspect

        module = importlib.import_module("dashboard.api.openobserve_stats")
        fn = module.api_opensearch
        assert callable(fn), "api_opensearch must be callable"
        assert inspect.iscoroutinefunction(fn), "api_opensearch must be async"

    def test_package_init_reexport(self) -> None:
        """dashboard.api __init__ must re-export api_opensearch."""
        pkg = importlib.import_module("dashboard.api")
        assert hasattr(pkg, "api_opensearch"), (
            "dashboard.api.__init__ must re-export api_opensearch"
        )
        # Must be the same object (not a copy)
        from dashboard.api.openobserve_stats import api_opensearch as direct_ref

        assert pkg.api_opensearch is direct_ref, (
            "dashboard.api.api_opensearch must be the identical object as "
            "dashboard.api.openobserve_stats.api_opensearch"
        )


class TestChecksIntegrityImport:
    """checks.integrity.run_all_checks must be reachable via three valid paths."""

    def test_import_from_checks_integrity(self) -> None:
        """from checks.integrity import run_all_checks must work."""
        from checks.integrity import run_all_checks  # noqa: F401 (import test)

        assert callable(run_all_checks)

    def test_import_from_checks_package(self) -> None:
        """from checks import run_all_checks must work (via __init__ re-export)."""
        from checks import run_all_checks  # noqa: F401

        assert callable(run_all_checks)

    def test_run_all_checks_returns_dict(self) -> None:
        """run_all_checks() must return a dict with the expected top-level keys."""
        from checks.integrity import run_all_checks

        result = run_all_checks()
        assert isinstance(result, dict), "run_all_checks() must return a dict"
        for key in ("models", "fixtures", "config", "summary"):
            assert key in result, f"Result dict missing key: {key!r}"

    def test_a2a_checks_integrity_raises_import_error(self) -> None:
        """from a2a.checks.integrity import … must raise ImportError (module deleted)."""
        # Remove any cached sub-modules to ensure a clean lookup
        for cached_key in list(sys.modules.keys()):
            if "a2a.checks" in cached_key:
                del sys.modules[cached_key]

        with pytest.raises(ImportError):
            importlib.import_module("a2a.checks.integrity")


# ══════════════════════════════════════════════════════════════════════════════
# §3  llm/db.py — persist_call REMOVED, core functions RETAINED
# ══════════════════════════════════════════════════════════════════════════════


class TestLlmDbPersistCallRemoved:
    """persist_call must not exist; session helpers must still be present."""

    @pytest.fixture(scope="class")
    def ldb(self) -> Generator[ModuleType, None, None]:
        """Import llm.db once for the class, then clean up."""
        module = importlib.import_module("llm.db")
        yield module

    def test_persist_call_removed(self, ldb: ModuleType) -> None:
        """llm.db must NOT expose persist_call — dead code was deleted."""
        assert not hasattr(ldb, "persist_call"), (
            "persist_call still exists in llm.db; dead code was not cleaned up"
        )

    def test_open_session_retained(self, ldb: ModuleType) -> None:
        """llm.db.open_session must still exist."""
        assert hasattr(ldb, "open_session"), (
            "open_session was accidentally removed from llm.db"
        )

    def test_open_session_is_coroutine(self, ldb: ModuleType) -> None:
        """open_session must be an async function."""
        import inspect

        assert inspect.iscoroutinefunction(ldb.open_session), (
            "llm.db.open_session must be async"
        )

    def test_close_session_retained(self, ldb: ModuleType) -> None:
        """llm.db.close_session must still exist."""
        assert hasattr(ldb, "close_session"), (
            "close_session was accidentally removed from llm.db"
        )

    def test_close_session_is_coroutine(self, ldb: ModuleType) -> None:
        """close_session must be an async function."""
        import inspect

        assert inspect.iscoroutinefunction(ldb.close_session), (
            "llm.db.close_session must be async"
        )

    def test_cost_report_retained(self, ldb: ModuleType) -> None:
        """llm.db.cost_report must still exist."""
        assert hasattr(ldb, "cost_report"), (
            "cost_report was accidentally removed from llm.db"
        )

    def test_cost_report_is_coroutine(self, ldb: ModuleType) -> None:
        """cost_report must be an async function."""
        import inspect

        assert inspect.iscoroutinefunction(ldb.cost_report), (
            "llm.db.cost_report must be async"
        )

    def test_no_schema_sql_reference_in_source(self) -> None:
        """llm/db.py source must not import or reference schema.sql."""
        db_source = (SRC_ROOT / "llm" / "db.py").read_text(encoding="utf-8")
        assert "schema.sql" not in db_source, (
            "llm/db.py still references schema.sql; the file was deleted"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §4  manage/_commands.py — IMPORT-STATEMENT CORRECTNESS (source grep)
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integrity
class TestManageCommandsImport:
    """manage/_commands.py must use the new import path, not the deleted one."""

    @pytest.fixture(scope="class")
    def commands_source(self) -> str:
        """Read _commands.py once for the whole class."""
        path = SRC_ROOT / "manage" / "_commands.py"
        assert path.exists(), f"_commands.py not found at {path}"
        return path.read_text(encoding="utf-8")

    def test_new_import_present(self, commands_source: str) -> None:
        """_commands.py must contain 'from checks.integrity import run_all_checks'."""
        assert "from checks.integrity import run_all_checks" in commands_source, (
            "_commands.py does not have the updated import "
            "'from checks.integrity import run_all_checks'"
        )

    def test_old_a2a_checks_import_absent(self, commands_source: str) -> None:
        """_commands.py must NOT reference 'from a2a.checks' (deleted package)."""
        assert "from a2a.checks" not in commands_source, (
            "_commands.py still contains 'from a2a.checks'; "
            "the deleted module path must be removed"
        )

    def test_a2a_checks_string_absent(self, commands_source: str) -> None:
        """_commands.py must not contain any bare 'a2a.checks' reference."""
        assert "a2a.checks" not in commands_source, (
            "_commands.py references 'a2a.checks' which no longer exists"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §5  docs/architecture/flowchart.md — MERMAID COMPLETENESS
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integrity
class TestFlowchartCompleteness:
    """flowchart.md must be a valid, complete Mermaid diagram covering all layers."""

    @pytest.fixture(scope="class")
    def flowchart(self) -> str:
        """Read flowchart.md once for the whole class."""
        path = PROJECT_ROOT / "docs" / "architecture" / "flowchart.md"
        assert path.exists(), f"Flowchart not found at {path}"
        return path.read_text(encoding="utf-8")

    # ── Mermaid fence ────────────────────────────────────────────────────────

    def test_has_mermaid_fence(self, flowchart: str) -> None:
        """The document must open a ```mermaid code fence."""
        assert "```mermaid" in flowchart, (
            "flowchart.md is missing the ```mermaid opening fence"
        )

    # ── Layer labels (Layer 0 … Layer 19 = 20 labels total) ─────────────────

    @pytest.mark.parametrize("layer_num", range(20))  # 0 through 19 inclusive
    def test_layer_label_present(self, flowchart: str, layer_num: int) -> None:
        """Every layer label 'Layer N' must appear in the flowchart."""
        label = f"Layer {layer_num}"
        assert label in flowchart, (
            f"flowchart.md is missing layer label: {label!r}"
        )

    # ── Key component names ──────────────────────────────────────────────────

    @pytest.mark.parametrize(
        "component",
        [
            "ai_proxy",
            "a2a",
            "csmcp",
            "OpenObserve",
            "PostgreSQL",
            "claude_agent_sdk",
        ],
    )
    def test_key_component_present(self, flowchart: str, component: str) -> None:
        """Each major component name must appear in the flowchart."""
        assert component in flowchart, (
            f"flowchart.md is missing key component name: {component!r}"
        )

    # ── Routing strategy names (all 13) ─────────────────────────────────────

    @pytest.mark.parametrize(
        "strategy",
        [
            "priority",
            "round-robin",
            "cost-optimized",
            "weighted",
            "random",
            "least-used",
            "fill-first",
            "p2c",
            "strict-random",
            "auto",
            "lkgp",
            "context-optimized",
            "context-relay",
        ],
    )
    def test_strategy_name_present(self, flowchart: str, strategy: str) -> None:
        """Every routing strategy name must appear in the flowchart."""
        assert strategy in flowchart, (
            f"flowchart.md is missing routing strategy: {strategy!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §6  scripts/gwt-aliases.sh — PATH UPDATE
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integrity
class TestGwtAliasesPathUpdate:
    """gwt-aliases.sh must reference the new scripts/ location, not the repo root."""

    @pytest.fixture(scope="class")
    def gwt_source(self) -> str:
        """Read gwt-aliases.sh once for the whole class."""
        path = PROJECT_ROOT / "scripts" / "gwt-aliases.sh"
        assert path.exists(), f"gwt-aliases.sh not found at {path}"
        return path.read_text(encoding="utf-8")

    def test_references_scripts_subdir(self, gwt_source: str) -> None:
        """gwt-aliases.sh must reference scripts/worktree-session-manager.py."""
        assert "scripts/worktree-session-manager.py" in gwt_source, (
            "gwt-aliases.sh does not reference scripts/worktree-session-manager.py; "
            "the path may not have been updated after the script was moved"
        )

    def test_no_bare_root_reference(self, gwt_source: str) -> None:
        """gwt-aliases.sh must NOT reference the manager at root level (e.g. $root/worktree-session-manager.py)."""
        # A root-level reference would look like: "$root/worktree-session-manager.py"
        # without an intervening "scripts" component.
        import re

        # Match patterns like:  $root/worktree-session-manager.py
        #                  or:  "${root}/worktree-session-manager.py"
        # but NOT:              $root/scripts/worktree-session-manager.py
        bare_root_pattern = re.compile(
            r'\$\{?root\}?/worktree-session-manager\.py(?!\s*#)',
        )
        # Filter out any line that also contains "scripts/"
        offending_lines = [
            line
            for line in gwt_source.splitlines()
            if bare_root_pattern.search(line) and "scripts/" not in line
        ]
        assert not offending_lines, (
            "gwt-aliases.sh references worktree-session-manager.py without the "
            f"scripts/ prefix on line(s): {offending_lines}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §7  docs/hooks/ — CONTENT COMPLETENESS
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integrity
class TestHookDocsContent:
    """Every .md file in docs/hooks/ must be non-empty and have meaningful content."""

    @pytest.fixture(scope="class")
    def hook_doc_paths(self) -> list[Path]:
        """Return all .md paths under docs/hooks/."""
        hooks_dir = PROJECT_ROOT / "docs" / "hooks"
        assert hooks_dir.exists(), f"docs/hooks/ directory not found at {hooks_dir}"
        paths = sorted(hooks_dir.glob("*.md"))
        assert paths, "docs/hooks/ contains no .md files"
        return paths

    def test_all_expected_hook_docs_present(self, hook_doc_paths: list[Path]) -> None:
        """All six expected hook documentation files must be present."""
        expected = {
            "RootCommandExecuted.md",
            "SessionEnd.md",
            "SessionStart.md",
            "YaraRuleGeneration.md",
            "YaraRuleOptimization.md",
            "YaraRuleTesting.md",
        }
        found = {p.name for p in hook_doc_paths}
        missing = expected - found
        assert not missing, (
            f"Missing hook doc(s) in docs/hooks/: {missing}"
        )

    @pytest.mark.parametrize(
        "filename",
        [
            "RootCommandExecuted.md",
            "SessionEnd.md",
            "SessionStart.md",
            "YaraRuleGeneration.md",
            "YaraRuleOptimization.md",
            "YaraRuleTesting.md",
        ],
    )
    def test_hook_doc_is_non_empty(self, filename: str) -> None:
        """Each hook doc must have actual text content (not a zero-byte placeholder)."""
        path = PROJECT_ROOT / "docs" / "hooks" / filename
        assert path.exists(), f"Hook doc not found: {path}"
        content = path.read_text(encoding="utf-8").strip()
        assert content, f"docs/hooks/{filename} is empty"

    @pytest.mark.parametrize(
        "filename",
        [
            "RootCommandExecuted.md",
            "SessionEnd.md",
            "SessionStart.md",
            "YaraRuleGeneration.md",
            "YaraRuleOptimization.md",
            "YaraRuleTesting.md",
        ],
    )
    def test_hook_doc_has_heading(self, filename: str) -> None:
        """Each hook doc must contain at least one Markdown heading (# …)."""
        path = PROJECT_ROOT / "docs" / "hooks" / filename
        content = path.read_text(encoding="utf-8")
        has_heading = any(line.startswith("#") for line in content.splitlines())
        assert has_heading, (
            f"docs/hooks/{filename} has no Markdown heading; "
            "expected at least one '# …' line"
        )

    @pytest.mark.parametrize(
        "filename",
        [
            "RootCommandExecuted.md",
            "SessionEnd.md",
            "SessionStart.md",
            "YaraRuleGeneration.md",
            "YaraRuleOptimization.md",
            "YaraRuleTesting.md",
        ],
    )
    def test_hook_doc_min_length(self, filename: str) -> None:
        """Each hook doc must have at least 5 non-blank lines (sanity check)."""
        path = PROJECT_ROOT / "docs" / "hooks" / filename
        content = path.read_text(encoding="utf-8")
        non_blank = [ln for ln in content.splitlines() if ln.strip()]
        assert len(non_blank) >= 5, (
            f"docs/hooks/{filename} has only {len(non_blank)} non-blank lines; "
            "expected ≥ 5 (content may be a stub)"
        )
