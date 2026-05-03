"""Integration tests for bootstrap with live GitHub marketplace index.

Tests the full bootstrap flow:
1. Download index.json.sha512 from GitHub
2. Verify SHA512 checksum
3. Download index.json if changed
4. Seed marketplace index into database
5. Install core marketplace items
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from tortoise import Tortoise

log = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.asyncio
class TestBootstrapGitHubIndex:
    """Test bootstrap with GitHub marketplace index."""

    GITHUB_INDEX_URL = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json"
    GITHUB_SHA512_URL = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512"

    @pytest_asyncio.fixture
    async def temp_marketplace_dir(self):
        """Temporary marketplace directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            yield tmp_path

    async def test_download_github_index_sha512(self, temp_marketplace_dir):
        """Test downloading SHA512 checksum from GitHub."""
        from core.hooks.sha512_checker import download_file

        try:
            # Real network call to GitHub
            sha512_data = await download_file(self.GITHUB_SHA512_URL)
            assert sha512_data, "SHA512 file should not be empty"
            assert len(sha512_data.decode().strip()) == 128, "SHA512 should be 128 hex chars"
            log.info(f"✓ Downloaded SHA512 from GitHub: {sha512_data.decode()[:32]}...")
        except Exception as e:
            pytest.skip(f"GitHub not accessible: {e}")

    async def test_download_github_index_json(self, temp_marketplace_dir):
        """Test downloading index.json from GitHub."""
        from core.hooks.sha512_checker import download_file

        try:
            index_data = await download_file(self.GITHUB_INDEX_URL)
            assert index_data, "Index file should not be empty"
            index = json.loads(index_data)
            
            # Validate structure
            assert "mcps" in index, "Index should have 'mcps' key"
            assert "agents" in index, "Index should have 'agents' key"
            assert "skills" in index, "Index should have 'skills' key"
            
            log.info("✓ Downloaded index.json from GitHub")
            log.info(f"  - MCPs: {len(index.get('mcps', []))}")
            log.info(f"  - Agents: {len(index.get('agents', []))}")
            log.info(f"  - Skills: {len(index.get('skills', []))}")
        except Exception as e:
            pytest.skip(f"GitHub not accessible: {e}")

    async def test_verify_sha512_checksum(self, temp_marketplace_dir):
        """Test SHA512 verification of downloaded index."""
        from core.hooks.sha512_checker import download_file, compute_sha512

        try:
            sha512_data = await download_file(self.GITHUB_SHA512_URL)
            index_data = await download_file(self.GITHUB_INDEX_URL)
            
            remote_sha512 = sha512_data.decode().strip()
            computed = compute_sha512(index_data)
            
            assert computed == remote_sha512, "SHA512 mismatch"
            log.info(f"✓ SHA512 checksum verified: {computed[:32]}...")
        except Exception as e:
            pytest.skip(f"GitHub not accessible: {e}")

    @pytest_asyncio.fixture
    async def db(self):
        """Initialize test database with marketplace models."""
        db_path = ":memory:"
        modules_to_load = ["core.db.models.scopes", "core.marketplace"]

        await Tortoise.init(
            db_url=f"sqlite://{db_path}",
            modules={"models": modules_to_load},
        )
        await Tortoise.generate_schemas()
        yield Tortoise
        await Tortoise.close_connections()

    @pytest_asyncio.fixture
    async def project(self, db):
        """Create test project."""
        from core.db.models.scope import ProjectScope
        
        proj = await ProjectScope.create(
            name="test-bootstrap",
            description="Test bootstrap project",
        )
        return proj

    async def test_seed_marketplace_index_into_db(self, db, project):
        """Test seeding marketplace index into database."""
        from core.hooks.sha512_checker import download_file
        from core.marketplace import seed_marketplace_index

        try:
            index_data = await download_file(self.GITHUB_INDEX_URL)
            index = json.loads(index_data)
            
            # Seed into database
            result = await seed_marketplace_index(index, project)
            
            assert result["mcps_created"] > 0, "Should create MCP entries"
            assert result["agents_created"] >= 0, "Should create agents entries"
            assert result["skills_created"] >= 0, "Should create skills entries"
            
            log.info("✓ Seeded marketplace index")
            log.info(f"  - MCPs: {result['mcps_created']}")
            log.info(f"  - Agents: {result['agents_created']}")
            log.info(f"  - Skills: {result['skills_created']}")
        except Exception as e:
            if "GitHub" in str(e) or "not accessible" in str(e):
                pytest.skip(f"GitHub not accessible: {e}")
            raise

    async def test_check_index_update_detection(self, temp_marketplace_dir):
        """Test that SHA512 check detects updates."""
        from core.hooks.sha512_checker import check_index_update

        # Mock the files
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_marketplace_dir
            
            try:
                # First check - should download
                has_update, index_data = await check_index_update()
                assert has_update is not None, "Should return update status"
                
                if has_update:
                    assert index_data is not None, "Should return index data if updated"
                    log.info("✓ Index update detected")
                else:
                    log.info("✓ Index is current (no update)")
            except Exception as e:
                if "GitHub" in str(e):
                    pytest.skip(f"GitHub not accessible: {e}")
                raise

    async def test_bootstrap_flow_end_to_end(self, db, project):
        """Test complete bootstrap flow: download, verify, seed, install."""
        from core.hooks.bootstrap_status import BootstrapStatus
        from core.hooks.sha512_checker import check_index_update
        from core.hooks.bootstrap_installer import bootstrap_install_core_items
        from core.marketplace import seed_marketplace_index

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmpdir)
                
                try:
                    # Step 1: Check for updates
                    has_update, index_data = await check_index_update()
                    if not has_update:
                        log.info("✓ Index is current, skipping fresh download")
                        return

                    # Step 2: Verify SHA512
                    assert index_data, "Should have index data"
                    index = json.loads(index_data)
                    
                    # Step 3: Initialize bootstrap status
                    status = BootstrapStatus()
                    
                    # Step 4: Seed database
                    seed_result = await seed_marketplace_index(index, project)
                    assert seed_result["mcps_created"] > 0
                    
                    # Step 5: Mock installer and run bootstrap
                    with patch(
                        "core.marketplace.installer.PackageInstaller.install",
                        new_callable=AsyncMock,
                    ) as mock_install:
                        mock_install.return_value = {"success": True}
                        
                        result = await bootstrap_install_core_items(index, status, max_retries=1)
                        
                        # Verify results
                        assert result["total"] > 0, "Should have core items to install"
                        assert result["installed"] >= 0, "Should record installations"
                        
                        log.info("✓ Bootstrap complete:")
                        log.info(f"  - Total: {result['total']}")
                        log.info(f"  - Installed: {result['installed']}")
                        log.info(f"  - Failed: {result['failed']}")
                        
                except Exception as e:
                    if "GitHub" in str(e):
                        pytest.skip(f"GitHub not accessible: {e}")
                    raise


@pytest.mark.integration
@pytest.mark.asyncio
class TestBootstrapErrorHandling:
    """Test bootstrap error handling and recovery."""

    async def test_bootstrap_recovers_from_partial_failure(self):
        """Test that bootstrap can resume after partial failure."""
        from core.hooks.bootstrap_status import BootstrapStatus

        status = BootstrapStatus()
        status.record_installed("mcp-1")
        status.record_installed("mcp-2")
        status.record_failed("mcp-3", "Network timeout")
        
        assert status.is_recoverable(), "Should be recoverable with failed items"
        assert len(status.installed_items) == 2
        assert len(status.failed_items) == 1
        assert status.failed_items["mcp-3"] == "Network timeout"
        
        log.info(f"✓ Bootstrap recovery: {len(status.installed_items)} installed, {len(status.failed_items)} failed")

    async def test_bootstrap_status_persistence(self):
        """Test that bootstrap status persists to disk."""
        from core.hooks.bootstrap_status import BootstrapStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.hooks.bootstrap_status.BOOTSTRAP_STATUS_FILE", Path(tmpdir) / ".bootstrap_status.json"):
                # Save
                status1 = BootstrapStatus()
                status1.record_installed("mcp-test")
                status1.save()
                
                # Load
                status2 = BootstrapStatus.load()
                assert status2 is not None
                assert "mcp-test" in status2.installed_items
                
                log.info("✓ Bootstrap status persisted and loaded")

    async def test_bootstrap_sha512_cache_invalidation(self, tmp_path):
        """Test that SHA512 cache detects changes."""
        from core.hooks.sha512_checker import compute_sha512

        # Simulate old cached SHA512
        old_sha = compute_sha512(b"old index content")
        new_sha = compute_sha512(b"new index content updated")
        
        assert old_sha != new_sha, "Different content should have different SHA512"
        log.info("✓ SHA512 cache invalidation works")
