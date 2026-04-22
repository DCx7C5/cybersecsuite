"""
tests/test_worktree_manager.py — Integration tests for worktree-session-manager.py

Run with:
    python3 -m pytest tests/test_worktree_manager.py -v

These tests create real temporary git repositories and worktrees on disk.
They require git >= 2.20 and bash to be available on the system.
"""
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

# Import the manager module directly (filename has hyphens — use importlib)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "wsm",
    Path(__file__).parent.parent / "scripts" / "worktree-session-manager.py",
)
wsm = _ilu.module_from_spec(_spec)  # type: ignore[assignment]
_spec.loader.exec_module(wsm)  # type: ignore[union-attr]

SID_RE = re.compile(r"^[0-9a-f]{12}$")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_repo(path: Path) -> None:
    """Initialise a bare-minimum git repo with one commit."""
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test.com"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"],
                   check=True, capture_output=True)
    (path / "README.md").write_text("# test\n")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


def _make_template_dir(base: Path) -> Path:
    """Create a minimal hook template directory."""
    tpl = base / "hooks"
    tpl.mkdir(parents=True, exist_ok=True)
    (tpl / "pre-commit.tpl").write_text(
        "#!/usr/bin/env bash\n# session @@SID@@\nexit 0\n"
    )
    (tpl / "pre-push.tpl").write_text(
        "#!/usr/bin/env bash\n# session @@SID@@\nexit 0\n"
    )
    return tpl


# ---------------------------------------------------------------------------
# SID generation and validation
# ---------------------------------------------------------------------------

class TestSIDGeneration(unittest.TestCase):

    def test_generate_sid_format(self):
        sid = wsm.generate_sid()
        self.assertRegex(sid, r"^[0-9a-f]{12}$")

    def test_generate_sid_length(self):
        self.assertEqual(len(wsm.generate_sid()), 12)

    def test_generate_sid_uniqueness(self):
        sids = {wsm.generate_sid() for _ in range(100)}
        self.assertEqual(len(sids), 100)

    def test_validate_sid_accepts_valid(self):
        wsm.validate_sid("a3f1c8d20b4e")

    def test_validate_sid_rejects_uppercase(self):
        with self.assertRaises(ValueError):
            wsm.validate_sid("A3F1C8D20B4E")

    def test_validate_sid_rejects_short(self):
        with self.assertRaises(ValueError):
            wsm.validate_sid("a3f1c8d")

    def test_validate_sid_rejects_long(self):
        with self.assertRaises(ValueError):
            wsm.validate_sid("a3f1c8d20b4exx")

    def test_validate_sid_rejects_non_hex(self):
        with self.assertRaises(ValueError):
            wsm.validate_sid("gggggggggggg")

    def test_validate_sid_rejects_empty(self):
        with self.assertRaises(ValueError):
            wsm.validate_sid("")


# ---------------------------------------------------------------------------
# Worktree creation
# ---------------------------------------------------------------------------

class TestWorktreeCreate(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.sid = wsm.generate_sid()

    def tearDown(self):
        self._tmp.cleanup()

    def _create(self, sid=None) -> Path:
        sid = sid or self.sid
        return wsm.create_worktree(
            sid, "main",
            repo_root=self.repo,
            hooks_template_dir=self.tpl,
        )

    def test_create_returns_path(self):
        path = self._create()
        self.assertIsInstance(path, Path)

    def test_create_directory_name(self):
        path = self._create()
        self.assertEqual(path.name, f"worktree-{self.sid}")

    def test_create_directory_exists(self):
        path = self._create()
        self.assertTrue(path.is_dir())

    def test_create_marker_file_exists(self):
        path = self._create()
        marker = path / ".worktree-session"
        self.assertTrue(marker.exists())

    def test_create_marker_file_contains_sid(self):
        path = self._create()
        marker = path / ".worktree-session"
        self.assertEqual(marker.read_text().strip(), self.sid)

    def test_create_hooks_path_config_set(self):
        path = self._create()
        result = subprocess.run(
            ["git", "-C", str(path), "config", "--local", "core.hooksPath"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            # core.hooksPath may be in the worktree-specific config
            result = subprocess.run(
                ["git", "-C", str(path), "config", "core.hooksPath"],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0)
        hooks_path = result.stdout.strip()
        self.assertTrue(hooks_path.endswith("hooks"), f"Unexpected hooksPath: {hooks_path}")

    def test_create_hooks_installed(self):
        path = self._create()
        hooks_dir = wsm.resolve_worktree_git_hooks_dir(path)
        installed = list(hooks_dir.glob("*"))
        non_sample = [h for h in installed if not h.name.endswith(".sample")]
        self.assertGreater(len(non_sample), 0, "No hooks installed")

    def test_create_hooks_executable(self):
        path = self._create()
        hooks_dir = wsm.resolve_worktree_git_hooks_dir(path)
        for hook in hooks_dir.iterdir():
            if not hook.name.endswith(".sample"):
                self.assertTrue(
                    os.access(hook, os.X_OK),
                    f"Hook not executable: {hook}"
                )

    def test_create_hooks_no_unreplaced_tokens(self):
        path = self._create()
        hooks_dir = wsm.resolve_worktree_git_hooks_dir(path)
        for hook in hooks_dir.iterdir():
            if not hook.name.endswith(".sample"):
                content = hook.read_text()
                self.assertNotIn("@@SID@@", content, f"@@SID@@ found in {hook.name}")

    def test_create_idempotent(self):
        path1 = self._create()
        path2 = self._create()  # second call with same SID
        self.assertEqual(path1, path2)

    def test_worktree_registered_in_git(self):
        self._create()
        result = subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "list"],
            capture_output=True, text=True,
        )
        self.assertIn(f"worktree-{self.sid}", result.stdout)

    def test_extensions_worktree_config_enabled(self):
        self._create()
        result = subprocess.run(
            ["git", "-C", str(self.repo), "config", "--get", "extensions.worktreeConfig"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().lower(), "true")


# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------

class TestWorktreeTeardown(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.sid = wsm.generate_sid()
        wsm.create_worktree(self.sid, "main", repo_root=self.repo, hooks_template_dir=self.tpl)

    def tearDown(self):
        self._tmp.cleanup()

    def test_teardown_removes_directory(self):
        wt_path = wsm.get_worktree_root(self.sid, self.repo)
        self.assertTrue(wt_path.exists())
        wsm.teardown_worktree(self.sid, repo_root=self.repo)
        self.assertFalse(wt_path.exists())

    def test_teardown_deregisters_from_git(self):
        wsm.teardown_worktree(self.sid, repo_root=self.repo)
        result = subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "list"],
            capture_output=True, text=True,
        )
        self.assertNotIn(f"worktree-{self.sid}", result.stdout)

    def test_teardown_idempotent(self):
        wsm.teardown_worktree(self.sid, repo_root=self.repo)
        # Second call should not raise
        wsm.teardown_worktree(self.sid, repo_root=self.repo)

    def test_teardown_prunes_stale_entries(self):
        # Manually delete the directory to create a stale entry, then teardown
        wt_path = wsm.get_worktree_root(self.sid, self.repo)
        if wt_path.exists():
            shutil.rmtree(str(wt_path))
        # Now the git worktree entry is stale; teardown should handle it
        wsm.teardown_worktree(self.sid, repo_root=self.repo, force=True)
        result = subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "list"],
            capture_output=True, text=True,
        )
        self.assertNotIn(f"worktree-{self.sid}", result.stdout)


# ---------------------------------------------------------------------------
# Hook isolation between two worktrees
# ---------------------------------------------------------------------------

class TestHookIsolation(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.sid_a = wsm.generate_sid()
        self.sid_b = wsm.generate_sid()
        self.wt_a = wsm.create_worktree(self.sid_a, "main", repo_root=self.repo, hooks_template_dir=self.tpl)
        self.wt_b = wsm.create_worktree(self.sid_b, "main", repo_root=self.repo, hooks_template_dir=self.tpl)

    def tearDown(self):
        try:
            wsm.teardown_worktree(self.sid_a, repo_root=self.repo, force=True)
        except Exception:
            pass
        try:
            wsm.teardown_worktree(self.sid_b, repo_root=self.repo, force=True)
        except Exception:
            pass
        self._tmp.cleanup()

    def test_each_worktree_has_own_hooks_dir(self):
        hooks_a = wsm.resolve_worktree_git_hooks_dir(self.wt_a)
        hooks_b = wsm.resolve_worktree_git_hooks_dir(self.wt_b)
        self.assertNotEqual(hooks_a, hooks_b)
        self.assertTrue(hooks_a.is_dir())
        self.assertTrue(hooks_b.is_dir())

    def test_hooks_contain_correct_sid(self):
        hooks_a = wsm.resolve_worktree_git_hooks_dir(self.wt_a)
        hooks_b = wsm.resolve_worktree_git_hooks_dir(self.wt_b)
        for hook in hooks_a.iterdir():
            if not hook.name.endswith(".sample"):
                self.assertIn(self.sid_a, hook.read_text())
                self.assertNotIn(self.sid_b, hook.read_text())
        for hook in hooks_b.iterdir():
            if not hook.name.endswith(".sample"):
                self.assertIn(self.sid_b, hook.read_text())
                self.assertNotIn(self.sid_a, hook.read_text())

    def test_each_worktree_hooksPath_points_to_own_dir(self):
        for wt, sid in [(self.wt_a, self.sid_a), (self.wt_b, self.sid_b)]:
            result = subprocess.run(
                ["git", "-C", str(wt), "config", "core.hooksPath"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            hooks_path = result.stdout.strip()
            self.assertIn(f"worktree-{sid}", hooks_path)

    def test_remove_hooks_for_one_does_not_affect_other(self):
        wsm.remove_hooks(self.sid_a, self.wt_a)
        hooks_a = wsm.resolve_worktree_git_hooks_dir(self.wt_a)
        hooks_b = wsm.resolve_worktree_git_hooks_dir(self.wt_b)
        non_sample_a = [h for h in hooks_a.iterdir() if not h.name.endswith(".sample")]
        non_sample_b = [h for h in hooks_b.iterdir() if not h.name.endswith(".sample")]
        self.assertEqual(len(non_sample_a), 0, "Hooks not removed from wt_a")
        self.assertGreater(len(non_sample_b), 0, "Hooks incorrectly removed from wt_b")


# ---------------------------------------------------------------------------
# get_current_worktree_sid
# ---------------------------------------------------------------------------

class TestGetCurrentSID(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.sid = wsm.generate_sid()
        self.wt = wsm.create_worktree(self.sid, "main", repo_root=self.repo, hooks_template_dir=self.tpl)

    def tearDown(self):
        try:
            wsm.teardown_worktree(self.sid, repo_root=self.repo, force=True)
        except Exception:
            pass
        self._tmp.cleanup()

    def test_returns_correct_sid_in_managed_worktree(self):
        result = wsm.get_current_worktree_sid(cwd=self.wt)
        self.assertEqual(result, self.sid)

    def test_returns_none_in_non_managed_directory(self):
        result = wsm.get_current_worktree_sid(cwd=self.base)
        self.assertIsNone(result)

    def test_returns_none_in_repo_root_without_marker(self):
        result = wsm.get_current_worktree_sid(cwd=self.repo)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# list_worktrees
# ---------------------------------------------------------------------------

class TestListWorktrees(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.sid1 = wsm.generate_sid()
        self.sid2 = wsm.generate_sid()
        wsm.create_worktree(self.sid1, "main", repo_root=self.repo, hooks_template_dir=self.tpl)
        wsm.create_worktree(self.sid2, "main", repo_root=self.repo, hooks_template_dir=self.tpl)

    def tearDown(self):
        for sid in (self.sid1, self.sid2):
            try:
                wsm.teardown_worktree(sid, repo_root=self.repo, force=True)
            except Exception:
                pass
        self._tmp.cleanup()

    def test_list_includes_both_sids(self):
        worktrees = wsm.list_worktrees(repo_root=self.repo)
        sids = {wt["sid"] for wt in worktrees if wt.get("sid")}
        self.assertIn(self.sid1, sids)
        self.assertIn(self.sid2, sids)

    def test_list_returns_dicts_with_required_keys(self):
        worktrees = wsm.list_worktrees(repo_root=self.repo)
        for wt in worktrees:
            self.assertIn("path", wt)
            self.assertIn("name", wt)


# ---------------------------------------------------------------------------
# enable_worktree_config idempotency
# ---------------------------------------------------------------------------

class TestEnableWorktreeConfig(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_enable_is_idempotent(self):
        wsm.enable_worktree_config(self.repo)
        wsm.enable_worktree_config(self.repo)  # should not raise
        result = subprocess.run(
            ["git", "-C", str(self.repo), "config", "--get", "extensions.worktreeConfig"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.stdout.strip().lower(), "true")


# ---------------------------------------------------------------------------
# Hook template token replacement safety
# ---------------------------------------------------------------------------

class TestHookInstallSafety(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.tpl = self.base / "hooks"
        self.tpl.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_broken_template_raises_error(self):
        """A template with a bash syntax error should abort install."""
        bad_tpl = self.tpl / "pre-commit.tpl"
        bad_tpl.write_text("#!/usr/bin/env bash\n# @@SID@@\nif [\n")  # broken syntax
        fake_wt = self.base / "fake-wt"
        fake_wt.mkdir()
        fake_git = fake_wt / ".git"
        # Create an admin dir
        admin = self.base / "admin"
        admin.mkdir()
        (admin / "hooks").mkdir()
        fake_git.write_text(f"gitdir: {admin}\n")
        sid = wsm.generate_sid()
        with self.assertRaises(RuntimeError):
            wsm.install_hooks(sid, fake_wt, self.tpl)

    def test_template_without_sid_token_installs_fine(self):
        """A template that has no @@SID@@ is still valid."""
        tpl = self.tpl / "commit-msg.tpl"
        tpl.write_text("#!/usr/bin/env bash\nexit 0\n")
        fake_wt = self.base / "fake-wt2"
        fake_wt.mkdir()
        admin = self.base / "admin2"
        admin.mkdir()
        (admin / "hooks").mkdir()
        (fake_wt / ".git").write_text(f"gitdir: {admin}\n")
        sid = wsm.generate_sid()
        wsm.install_hooks(sid, fake_wt, self.tpl)
        hook = admin / "hooks" / "commit-msg"
        self.assertTrue(hook.exists())
        self.assertTrue(os.access(hook, os.X_OK))


# ---------------------------------------------------------------------------
# Concurrency — two sessions created simultaneously
# ---------------------------------------------------------------------------

class TestConcurrency(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def test_concurrent_create_both_succeed(self):
        """Two threads creating separate sessions simultaneously should both succeed."""
        results: list[Path | Exception] = []
        lock = threading.Lock()

        sids = [wsm.generate_sid(), wsm.generate_sid()]

        def worker(sid: str) -> None:
            try:
                path = wsm.create_worktree(
                    sid, "main",
                    repo_root=self.repo,
                    hooks_template_dir=self.tpl,
                )
                with lock:
                    results.append(path)
            except Exception as exc:
                with lock:
                    results.append(exc)

        threads = [threading.Thread(target=worker, args=(sid,)) for sid in sids]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        errors = [r for r in results if isinstance(r, Exception)]
        self.assertEqual(errors, [], f"Concurrent create raised: {errors}")
        self.assertEqual(len(results), 2)

        # Cleanup
        for sid in sids:
            try:
                wsm.teardown_worktree(sid, repo_root=self.repo, force=True)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# CLI integration via subprocess
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.tpl = _make_template_dir(self.base)
        self.manager = Path(__file__).parent.parent / "scripts" / "worktree-session-manager.py"

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, *args, cwd=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.manager), *args],
            capture_output=True, text=True,
            cwd=str(cwd or self.repo),
        )

    def test_create_prints_sid_to_stdout(self):
        result = self._run(
            "create", "--branch", "main",
            "--hooks-template", str(self.tpl),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        sid = result.stdout.strip()
        self.assertRegex(sid, r"^[0-9a-f]{12}$")
        # Cleanup
        wsm.teardown_worktree(sid, repo_root=self.repo, force=True)

    def test_sid_command_prints_sid(self):
        # Create first
        create = self._run("create", "--branch", "main", "--hooks-template", str(self.tpl))
        self.assertEqual(create.returncode, 0, create.stderr)
        sid = create.stdout.strip()
        wt = wsm.get_worktree_root(sid, self.repo)

        result = self._run("sid", cwd=wt)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), sid)

        wsm.teardown_worktree(sid, repo_root=self.repo, force=True)

    def test_list_command_exits_zero(self):
        result = self._run("list")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_sid_exits_nonzero(self):
        result = self._run("teardown", "not-a-valid-sid")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
