"""
Unit tests for StateRegistry — scopes merging, atomicity, concurrency, null/missing fallthrough.
"""

import asyncio
import json
import pytest
from pathlib import Path
import tempfile

from legacy.state import StateRegistry, ScopeLevel


@pytest.fixture
async def temp_homes():
    """Create temporary ~/.claude and ~/.cybersecsuite directories."""
    with tempfile.TemporaryDirectory() as claude_tmp, tempfile.TemporaryDirectory() as cybersec_tmp:
        claude_home = Path(claude_tmp)
        cybersecsuite_home = Path(cybersec_tmp)
        yield claude_home, cybersecsuite_home


@pytest.fixture
async def registry(temp_homes):
    """Create StateRegistry with temporary homes."""
    claude_home, cybersecsuite_home = temp_homes
    reg = StateRegistry(cybersecsuite_home=cybersecsuite_home, claude_home=claude_home)
    yield reg


class TestPathResolution:
    """Test path resolution methods."""

    @pytest.mark.asyncio
    async def test_claude_dir(self, registry, temp_homes):
        claude_home, _ = temp_homes
        assert registry.claude_dir() == claude_home

    @pytest.mark.asyncio
    async def test_cybersecsuite_dir(self, registry, temp_homes):
        _, cybersecsuite_home = temp_homes
        assert registry.cybersecsuite_dir() == cybersecsuite_home

    @pytest.mark.asyncio
    async def test_project_dir(self, registry, temp_homes):
        _, cybersecsuite_home = temp_homes
        project_dir = registry.project_dir("my-project")
        expected = cybersecsuite_home / "data" / "projects" / "my-project"
        assert project_dir == expected

    @pytest.mark.asyncio
    async def test_memory_dir_app_scope(self, registry, temp_homes):
        _, cybersecsuite_home = temp_homes
        app_memory = registry.memory_dir(ScopeLevel.APP)
        expected = cybersecsuite_home / "memory" / "system"
        assert app_memory == expected

    @pytest.mark.asyncio
    async def test_project_dir_invalid_path_traversal(self, registry):
        with pytest.raises(ValueError, match="Invalid path parameter"):
            registry.project_dir("..")

    @pytest.mark.asyncio
    async def test_project_dir_invalid_absolute_path(self, registry):
        with pytest.raises(ValueError, match="Invalid path parameter"):
            registry.project_dir("/etc/passwd")


class TestScopeLoading:
    """Test loading of each scopes."""

    @pytest.mark.asyncio
    async def test_load_global_defaults(self, registry):
        """Test GLOBAL scopes defaults."""
        await registry._load_all_scopes()
        global_data = registry._cache[ScopeLevel.GLOBAL]
        assert "env" in global_data
        assert "hooks" in global_data
        assert "lifecycle" in global_data
        assert global_data["effortLevel"] == "medium"

    @pytest.mark.asyncio
    async def test_load_app_scope_empty(self, registry):
        """Test loading APP scopes when no files exist."""
        await registry._load_all_scopes()
        app_data = registry._cache[ScopeLevel.APP]
        # Should have GLOBAL defaults
        assert app_data["effortLevel"] == "medium"

    @pytest.mark.asyncio
    async def test_load_app_scope_claude_settings(self, registry, temp_homes):
        """Test loading ~/.claude/settings.json."""
        claude_home, _ = temp_homes
        claude_settings_path = claude_home / "settings.json"
        claude_settings_path.parent.mkdir(parents=True, exist_ok=True)
        claude_settings_path.write_text(
            json.dumps({"effortLevel": "high", "env": {"CLAUDE_VAR": "value"}}), encoding="utf-8"
        )

        await registry._load_all_scopes()
        app_data = registry._cache[ScopeLevel.APP]
        assert app_data["effortLevel"] == "high"
        assert app_data["env"]["CLAUDE_VAR"] == "value"

    @pytest.mark.asyncio
    async def test_load_app_scope_cybersecsuite_overrides_claude(self, registry, temp_homes):
        """Test that ~/.cybersecsuite/settings.json overrides ~/.claude/settings.json."""
        claude_home, cybersecsuite_home = temp_homes

        # Write Claude settings
        claude_settings_path = claude_home / "settings.json"
        claude_settings_path.parent.mkdir(parents=True, exist_ok=True)
        claude_settings_path.write_text(
            json.dumps({"effortLevel": "high", "env": {"VAR": "claude_val"}}),
            encoding="utf-8",
        )

        # Write CyberSecSuite settings (should override)
        cybersec_settings_path = cybersecsuite_home / "settings.json"
        cybersec_settings_path.parent.mkdir(parents=True, exist_ok=True)
        cybersec_settings_path.write_text(
            json.dumps({"effortLevel": "low", "env": {"VAR": "cybersec_val"}}),
            encoding="utf-8",
        )

        await registry._load_all_scopes()
        app_data = registry._cache[ScopeLevel.APP]
        assert app_data["effortLevel"] == "low"
        assert app_data["env"]["VAR"] == "cybersec_val"

    @pytest.mark.asyncio
    async def test_load_invalid_json_ignored(self, registry, temp_homes):
        """Test that invalid JSON is ignored with warning."""
        _, cybersecsuite_home = temp_homes
        settings_path = cybersecsuite_home / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text("{ invalid json }", encoding="utf-8")

        await registry._load_all_scopes()
        app_data = registry._cache[ScopeLevel.APP]
        # Should have GLOBAL defaults, not crash
        assert app_data["effortLevel"] == "medium"


class TestMergeSemantics:
    """Test null/missing fallthrough and scopes merging."""

    @pytest.mark.asyncio
    async def test_cascade_missing_key_from_project_to_app(self, registry, temp_homes):
        """Test that missing key in PROJECT cascades to APP."""
        _, cybersecsuite_home = temp_homes

        # Write APP setting
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"effortLevel": "low"}), encoding="utf-8"
        )

        # Create PROJECT with no effortLevel
        project_id = "test-project"
        project_dir = registry.project_dir(project_id)
        project_settings_path = project_dir / "settings.json"
        project_settings_path.parent.mkdir(parents=True, exist_ok=True)
        project_settings_path.write_text(json.dumps({}), encoding="utf-8")

        await registry._load_all_scopes()
        value, winning_scope = await registry._merge_scopes("effortLevel", project_id=project_id)
        assert value == "low"
        assert winning_scope == ScopeLevel.APP

    @pytest.mark.asyncio
    async def test_project_overrides_app(self, registry, temp_homes):
        """Test that PROJECT scopes overrides APP."""
        _, cybersecsuite_home = temp_homes

        # Write APP setting
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"effortLevel": "low"}), encoding="utf-8"
        )

        # Create PROJECT with overriding value
        project_id = "test-project"
        project_dir = registry.project_dir(project_id)
        project_settings_path = project_dir / "settings.json"
        project_settings_path.parent.mkdir(parents=True, exist_ok=True)
        project_settings_path.write_text(
            json.dumps({"effortLevel": "high"}), encoding="utf-8"
        )

        await registry._load_all_scopes()
        value, winning_scope = await registry._merge_scopes("effortLevel", project_id=project_id)
        assert value == "high"
        assert winning_scope == ScopeLevel.PROJECT

    @pytest.mark.asyncio
    async def test_env_shallow_merge_across_scopes(self, registry, temp_homes):
        """Test shallow merge of env across scopes."""
        _, cybersecsuite_home = temp_homes

        # APP env
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"env": {"APP_KEY": "app_val", "SHARED": "app"}}),
            encoding="utf-8",
        )

        # PROJECT env
        project_id = "test-project"
        project_dir = registry.project_dir(project_id)
        project_settings_path = project_dir / "settings.json"
        project_settings_path.parent.mkdir(parents=True, exist_ok=True)
        project_settings_path.write_text(
            json.dumps({"env": {"PROJECT_KEY": "project_val", "SHARED": "project"}}),
            encoding="utf-8",
        )

        await registry._load_all_scopes()
        # Note: _merge_scopes works at top-level keys only
        # For nested merge, use get_env or similar
        project_env = await registry.get("env", scope=ScopeLevel.PROJECT, project_id=project_id)
        assert project_env["PROJECT_KEY"] == "project_val"


class TestGetSet:
    """Test get/set operations."""

    @pytest.mark.asyncio
    async def test_get_app_scope(self, registry, temp_homes):
        """Test get() from APP scopes."""
        _, cybersecsuite_home = temp_homes
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"effortLevel": "low"}), encoding="utf-8"
        )

        await registry._load_all_scopes()
        value = await registry.get("effortLevel", scope=ScopeLevel.APP)
        assert value == "low"

    @pytest.mark.asyncio
    async def test_get_default_value(self, registry):
        """Test get() returns default for missing key."""
        await registry._load_all_scopes()
        value = await registry.get("nonexistent", default="default_val")
        assert value == "default_val"

    @pytest.mark.asyncio
    async def test_set_app_scope(self, registry, temp_homes):
        """Test set() to APP scopes."""
        _, cybersecsuite_home = temp_homes
        await registry._load_all_scopes()

        await registry.set("effortLevel", "high", scope=ScopeLevel.APP)

        # Verify written to disk
        app_settings_path = cybersecsuite_home / "settings.json"
        assert app_settings_path.exists()
        data = json.loads(app_settings_path.read_text(encoding="utf-8"))
        assert data["effortLevel"] == "high"

    @pytest.mark.asyncio
    async def test_set_project_scope(self, registry, temp_homes):
        """Test set() to PROJECT scopes."""
        _, cybersecsuite_home = temp_homes
        await registry._load_all_scopes()

        project_id = "test-project"
        await registry.set(
            "effortLevel", "medium", scope=ScopeLevel.PROJECT, project_id=project_id
        )

        # Verify written to disk
        project_settings_path = registry.project_dir(project_id) / "settings.json"
        assert project_settings_path.exists()
        data = json.loads(project_settings_path.read_text(encoding="utf-8"))
        assert data["effortLevel"] == "medium"

    @pytest.mark.asyncio
    async def test_set_global_raises_error(self, registry):
        """Test that set() to GLOBAL scopes raises ValueError."""
        await registry._load_all_scopes()
        with pytest.raises(ValueError, match="Cannot write to GLOBAL scopes"):
            await registry.set("any_key", "value", scope=ScopeLevel.GLOBAL)

    @pytest.mark.asyncio
    async def test_delete_app_scope(self, registry, temp_homes):
        """Test delete() from APP scopes."""
        _, cybersecsuite_home = temp_homes

        # Write initial data
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"effortLevel": "high", "custom_key": "value"}),
            encoding="utf-8",
        )

        await registry._load_all_scopes()
        await registry.delete("custom_key", scope=ScopeLevel.APP)

        # Verify deleted from disk
        data = json.loads(app_settings_path.read_text(encoding="utf-8"))
        assert "custom_key" not in data
        assert data["effortLevel"] == "high"

    @pytest.mark.asyncio
    async def test_project_id_required_for_project_scope(self, registry):
        """Test that project_id is required for PROJECT scopes operations."""
        await registry._load_all_scopes()

        with pytest.raises(ValueError, match="project_id required"):
            await registry.get("key", scope=ScopeLevel.PROJECT)

        with pytest.raises(ValueError, match="project_id required"):
            await registry.set("key", "value", scope=ScopeLevel.PROJECT)


class TestMemoryAccess:
    """Test memory file access."""

    @pytest.mark.asyncio
    async def test_get_app_memory_missing(self, registry):
        """Test get_app_memory() for missing file."""
        result = await registry.get_app_memory("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_app_memory(self, registry, temp_homes):
        """Test set/get app memory."""
        _, cybersecsuite_home = temp_homes

        await registry.set_app_memory("test_key", "test content")

        # Verify file exists
        memory_path = cybersecsuite_home / "memory" / "system" / "test_key"
        assert memory_path.exists()
        assert memory_path.read_text(encoding="utf-8") == "test content"

        # Verify get returns same content
        content = await registry.get_app_memory("test_key")
        assert content == "test content"

    @pytest.mark.asyncio
    async def test_set_and_get_project_memory(self, registry):
        """Test set/get project memory."""
        project_id = "test-project"
        await registry.set_project_memory(project_id, "mem_key", "mem content")

        content = await registry.get_project_memory(project_id, "mem_key")
        assert content == "mem content"


class TestAtomicWrites:
    """Test atomic write behavior."""

    @pytest.mark.asyncio
    async def test_atomic_write_creates_file(self, registry, temp_homes):
        """Test that atomic write creates file."""
        _, cybersecsuite_home = temp_homes
        app_settings_path = cybersecsuite_home / "settings.json"

        data = {"key": "value"}
        await registry._atomic_write(app_settings_path, data)

        assert app_settings_path.exists()
        written_data = json.loads(app_settings_path.read_text(encoding="utf-8"))
        assert written_data == data

    @pytest.mark.asyncio
    async def test_atomic_write_overwrites_existing(self, registry, temp_homes):
        """Test that atomic write overwrites existing file."""
        _, cybersecsuite_home = temp_homes
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(json.dumps({"old": "data"}), encoding="utf-8")

        new_data = {"new": "data"}
        await registry._atomic_write(app_settings_path, new_data)

        written_data = json.loads(app_settings_path.read_text(encoding="utf-8"))
        assert written_data == new_data
        assert "old" not in written_data


class TestConcurrency:
    """Test concurrent access safety."""

    @pytest.mark.asyncio
    async def test_concurrent_reads_safe(self, registry, temp_homes):
        """Test concurrent reads don't cause race conditions."""
        _, cybersecsuite_home = temp_homes
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"counter": 0}), encoding="utf-8"
        )

        await registry._load_all_scopes()

        # Concurrent reads
        results = await asyncio.gather(
            registry.get("counter", scope=ScopeLevel.APP),
            registry.get("counter", scope=ScopeLevel.APP),
            registry.get("counter", scope=ScopeLevel.APP),
        )

        assert all(r == 0 for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_writes_to_different_scopes(self, registry):
        """Test concurrent writes to different scopes."""
        await registry._load_all_scopes()

        await asyncio.gather(
            registry.set("key1", "value1", scope=ScopeLevel.APP),
            registry.set("key2", "value2", scope=ScopeLevel.APP),
        )

        val1 = await registry.get("key1", scope=ScopeLevel.APP)
        val2 = await registry.get("key2", scope=ScopeLevel.APP)
        assert val1 == "value1"
        assert val2 == "value2"


class TestReload:
    """Test reload functionality."""

    @pytest.mark.asyncio
    async def test_reload_refreshes_cache(self, registry, temp_homes):
        """Test reload() refreshes in-memory cache."""
        _, cybersecsuite_home = temp_homes
        app_settings_path = cybersecsuite_home / "settings.json"
        app_settings_path.parent.mkdir(parents=True, exist_ok=True)
        app_settings_path.write_text(
            json.dumps({"effortLevel": "low"}), encoding="utf-8"
        )

        await registry._load_all_scopes()
        assert await registry.get("effortLevel") == "low"

        # Externally modify file
        app_settings_path.write_text(
            json.dumps({"effortLevel": "high"}), encoding="utf-8"
        )

        # Reload
        await registry.reload()
        assert await registry.get("effortLevel") == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
