"""
Tests for agent_hooks: baseline snapshotting, change detection, and ruff scoping.
"""
import json
import tempfile
from pathlib import Path

import pytest

# Adjust path for imports
import sys
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks import agent_hooks


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    project = tmp_path / "project"
    project.mkdir()
    
    # Create sample Python files
    (project / "file1.py").write_text("def foo():\n    pass\n")
    (project / "file2.py").write_text("def bar():\n    pass\n")
    (project / "file3.py").write_text("# Unchanged\n")
    
    # Create .git directory (minimal)
    git_dir = project / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("")
    
    # Set up environment to use project as root
    orig_get_project_dir = agent_hooks.get_project_dir
    
    def mock_get_project_dir():
        return project
    
    agent_hooks.get_project_dir = mock_get_project_dir
    
    yield project
    
    agent_hooks.get_project_dir = orig_get_project_dir


@pytest.fixture
def baseline_dir(tmp_path):
    """Create temporary baseline directory."""
    baseline = tmp_path / "baselines"
    baseline.mkdir()
    
    orig_baseline_dir = agent_hooks.BASELINE_DIR
    agent_hooks.BASELINE_DIR = baseline
    
    yield baseline
    
    agent_hooks.BASELINE_DIR = orig_baseline_dir


class TestComputeFileHash:
    """Test file hash computation."""
    
    def test_compute_hash_existing_file(self, temp_project):
        """Hash should be consistent for same file content."""
        file_path = temp_project / "file1.py"
        hash1 = agent_hooks.compute_file_hash(file_path)
        hash2 = agent_hooks.compute_file_hash(file_path)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256
    
    def test_compute_hash_nonexistent_file(self):
        """Non-existent files should have NOTFOUND hash."""
        hash_val = agent_hooks.compute_file_hash(Path("/nonexistent/file"))
        assert hash_val == "NOTFOUND"
    
    def test_hash_changes_on_content_change(self, temp_project):
        """Hash should change when file content changes."""
        file_path = temp_project / "file1.py"
        hash1 = agent_hooks.compute_file_hash(file_path)
        
        file_path.write_text("def bar():\n    pass\n")
        hash2 = agent_hooks.compute_file_hash(file_path)
        
        assert hash1 != hash2


class TestSnapshotBaseline:
    """Test baseline snapshot creation."""
    
    def test_snapshot_baseline_creates_file(self, temp_project, baseline_dir):
        """Baseline snapshot should create a JSON file."""
        target_files = ["file1.py", "file2.py"]
        baseline = agent_hooks.snapshot_baseline("test_agent", "session123", target_files)
        
        assert len(baseline) == 2
        assert "file1.py" in baseline
        assert "file2.py" in baseline
        
        # Check baseline file was created
        baseline_file = agent_hooks.get_baseline_file("test_agent", "session123")
        assert baseline_file.exists()
        
        stored = json.loads(baseline_file.read_text())
        assert stored == baseline
    
    def test_snapshot_baseline_handles_missing_files(self, temp_project, baseline_dir):
        """Baseline should mark missing files appropriately."""
        target_files = ["file1.py", "nonexistent.py"]
        baseline = agent_hooks.snapshot_baseline("test_agent", "session123", target_files)
        
        assert baseline["file1.py"] != "NOTFOUND"
        assert baseline["nonexistent.py"] == "NOTFOUND"


class TestGetChangedFiles:
    """Test detection of changed files."""
    
    def test_get_changed_files_no_baseline(self, temp_project, baseline_dir):
        """Without baseline, should return all target files."""
        target_files = ["file1.py", "file2.py"]
        changed = agent_hooks.get_changed_files("test_agent", "session456", target_files)
        
        assert set(changed) == set(target_files)
    
    def test_get_changed_files_detects_modifications(self, temp_project, baseline_dir):
        """Should detect modified files."""
        target_files = ["file1.py", "file2.py", "file3.py"]
        
        # Create baseline
        agent_hooks.snapshot_baseline("test_agent", "session456", target_files)
        
        # Modify one file
        (temp_project / "file1.py").write_text("def modified():\n    pass\n")
        
        # Get changed files
        changed = agent_hooks.get_changed_files("test_agent", "session456", target_files)
        
        assert "file1.py" in changed
        assert "file3.py" not in changed
    
    def test_get_changed_files_handles_new_files(self, temp_project, baseline_dir):
        """Should handle files that didn't exist in baseline."""
        target_files = ["file1.py"]
        
        # Create baseline with file1 only
        agent_hooks.snapshot_baseline("test_agent", "session456", target_files)
        
        # Create new file that's in target list
        new_file = temp_project / "file4.py"
        new_file.write_text("def new():\n    pass\n")
        
        # Get changed files (including the new file in targets)
        changed = agent_hooks.get_changed_files("test_agent", "session456", ["file1.py", "file4.py"])
        
        assert "file4.py" in changed


class TestRunRuffDryRun:
    """Test ruff dry-run functionality."""
    
    def test_run_ruff_dry_run_empty_files(self):
        """Dry run with no files should return empty."""
        output, count = agent_hooks.run_ruff_dry_run([])
        
        assert output == ""
        assert count == 0
    
    def test_run_ruff_dry_run_with_files(self, temp_project):
        """Dry run should execute ruff check --diff."""
        # Create a file with intentional style issues
        bad_file = temp_project / "bad_style.py"
        bad_file.write_text("import os\nimport sys\ndef f( x ):\n    pass\n")
        
        output, count = agent_hooks.run_ruff_dry_run(["bad_style.py"])
        
        # Should return some output (diff or empty if no issues)
        assert isinstance(output, str)
        assert count == 1


class TestRunRuffFix:
    """Test ruff fix functionality."""
    
    def test_run_ruff_fix_empty_files(self):
        """Fix with no files should return 0."""
        count, summary = agent_hooks.run_ruff_fix([])
        
        assert count == 0
        assert summary == ""
    
    def test_run_ruff_fix_with_files(self, temp_project):
        """Fix should apply ruff fixes."""
        # Create a file with potential issues
        file_to_fix = temp_project / "to_fix.py"
        original = "x=1\ny=2\n"
        file_to_fix.write_text(original)
        
        count, summary = agent_hooks.run_ruff_fix(["to_fix.py"])
        
        # Should return file count
        assert count == 1
        assert isinstance(summary, str)


class TestAgentStartHook:
    """Test on_agent_start hook."""
    
    @pytest.mark.asyncio
    async def test_on_agent_start_creates_baseline(self, temp_project, baseline_dir, monkeypatch):
        """on_agent_start should create baseline snapshot."""
        # Mock session directory
        session_dir = Path(tempfile.mkdtemp())
        monkeypatch.setenv("CYBERSEC_SESSION_ID", "test_session")
        
        orig_get_session_dir = agent_hooks.get_session_dir
        agent_hooks.get_session_dir = lambda: session_dir
        
        target_files = ["file1.py", "file2.py"]
        await agent_hooks.on_agent_start("test_agent", "test_session", target_files)
        
        # Verify baseline was created
        baseline_file = agent_hooks.get_baseline_file("test_agent", "test_session")
        assert baseline_file.exists()
        
        baseline = json.loads(baseline_file.read_text())
        assert len(baseline) == 2
        
        agent_hooks.get_session_dir = orig_get_session_dir
    
    @pytest.mark.asyncio
    async def test_on_agent_start_no_target_files(self, temp_project, baseline_dir, monkeypatch):
        """on_agent_start should work without target files."""
        session_dir = Path(tempfile.mkdtemp())
        monkeypatch.setenv("CYBERSEC_SESSION_ID", "test_session2")
        
        orig_get_session_dir = agent_hooks.get_session_dir
        agent_hooks.get_session_dir = lambda: session_dir
        
        # Should not raise
        await agent_hooks.on_agent_start("test_agent", "test_session2")
        
        agent_hooks.get_session_dir = orig_get_session_dir


class TestAgentStopHook:
    """Test on_agent_stop hook."""
    
    @pytest.mark.asyncio
    async def test_on_agent_stop_dry_run_mode(self, temp_project, baseline_dir, monkeypatch):
        """on_agent_stop with dry_run=True should not apply fixes."""
        session_dir = Path(tempfile.mkdtemp())
        monkeypatch.setenv("CYBERSEC_SESSION_ID", "test_session3")
        
        orig_get_session_dir = agent_hooks.get_session_dir
        agent_hooks.get_session_dir = lambda: session_dir
        
        target_files = ["file1.py", "file2.py"]
        
        # Create baseline
        agent_hooks.snapshot_baseline("test_agent", "test_session3", target_files)
        
        # Modify a file
        (temp_project / "file1.py").write_text("def modified():\n    pass\n")
        
        # Call on_agent_stop with dry_run=True
        await agent_hooks.on_agent_stop("test_agent", "test_session3", target_files, dry_run=True)
        
        # Should not raise
        agent_hooks.get_session_dir = orig_get_session_dir
    
    @pytest.mark.asyncio
    async def test_on_agent_stop_detects_changes(self, temp_project, baseline_dir, monkeypatch):
        """on_agent_stop should detect which files changed."""
        session_dir = Path(tempfile.mkdtemp())
        monkeypatch.setenv("CYBERSEC_SESSION_ID", "test_session4")
        
        orig_get_session_dir = agent_hooks.get_session_dir
        agent_hooks.get_session_dir = lambda: session_dir
        
        target_files = ["file1.py", "file2.py", "file3.py"]
        
        # Create baseline
        agent_hooks.snapshot_baseline("test_agent", "test_session4", target_files)
        
        # Modify file1 only
        (temp_project / "file1.py").write_text("def changed():\n    pass\n")
        
        # Call on_agent_stop
        await agent_hooks.on_agent_stop("test_agent", "test_session4", target_files, dry_run=True)
        
        # Cleanup
        agent_hooks.get_session_dir = orig_get_session_dir


class TestIntegration:
    """Integration tests for full agent lifecycle."""
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle_snapshot_to_change_detection(self, temp_project, baseline_dir, monkeypatch):
        """Full lifecycle: start, modify file, stop."""
        session_dir = Path(tempfile.mkdtemp())
        session_id = "integration_test"
        agent_name = "lifecycle_agent"
        monkeypatch.setenv("CYBERSEC_SESSION_ID", session_id)
        
        orig_get_session_dir = agent_hooks.get_session_dir
        agent_hooks.get_session_dir = lambda: session_dir
        
        target_files = ["file1.py", "file2.py", "file3.py"]
        
        # Agent starts
        await agent_hooks.on_agent_start(agent_name, session_id, target_files)
        
        # Baseline should exist
        baseline_file = agent_hooks.get_baseline_file(agent_name, session_id)
        assert baseline_file.exists()
        baseline = json.loads(baseline_file.read_text())
        assert len(baseline) == 3
        
        # Simulate agent modifying files
        (temp_project / "file1.py").write_text("def modified1():\n    pass\n")
        (temp_project / "file2.py").write_text("def modified2():\n    pass\n")
        
        # Get changed files
        changed = agent_hooks.get_changed_files(agent_name, session_id, target_files)
        assert len(changed) >= 2
        assert "file1.py" in changed
        assert "file2.py" in changed
        
        # Agent stops
        await agent_hooks.on_agent_stop(agent_name, session_id, target_files, dry_run=True)
        
        # State file should be cleaned up
        project_dir = agent_hooks.get_project_dir()
        state_file = project_dir / ".agent_active.json"
        assert not state_file.exists()
        
        agent_hooks.get_session_dir = orig_get_session_dir
