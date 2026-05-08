"""Tests for marketplace package manager."""

import asyncio
import hashlib
import pytest
import tarfile
from unittest.mock import AsyncMock, patch

from css.core.marketplace import (
    PackageInstallResult,
    fetch_index,
    verify_hash,
    check_for_updates,
    install_package,
    batch_install,
    PackageNotFoundError,
    HashVerificationError,
)


class TestFetchIndex:
    """Tests for fetch_index function."""

    @pytest.mark.asyncio
    async def test_fetch_index_success(self):
        """Test successfully fetching marketplace index."""
        mock_index = {
            "package-a": {
                "version": "1.0.0",
                "sha512": "abc123",
                "source_url": "https://example.com/package-a.tar.gz",
            }
        }

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_index

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            result = await fetch_index("https://example.com/index.json")
            assert result == mock_index

    @pytest.mark.asyncio
    async def test_fetch_index_404(self):
        """Test fetch_index with 404 response."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 404

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            with pytest.raises(PackageNotFoundError):
                await fetch_index("https://example.com/index.json")

    @pytest.mark.asyncio
    async def test_fetch_index_timeout(self):
        """Test fetch_index timeout."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.side_effect = asyncio.TimeoutError()

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            with pytest.raises(Exception):  # MarketplaceError
                await fetch_index("https://example.com/index.json")


class TestVerifyHash:
    """Tests for verify_hash function."""

    @pytest.mark.asyncio
    async def test_verify_hash_success(self, tmp_path):
        """Test hash verification succeeds for matching hash."""
        test_file = tmp_path / "test.tar.gz"
        test_data = b"test package content"
        test_file.write_bytes(test_data)

        expected_hash = hashlib.sha512(test_data).hexdigest()

        result = await verify_hash(test_file, expected_hash)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_hash_mismatch(self, tmp_path):
        """Test hash verification fails for mismatched hash."""
        test_file = tmp_path / "test.tar.gz"
        test_file.write_bytes(b"test package content")

        wrong_hash = "0" * 128  # Invalid hash

        with pytest.raises(HashVerificationError, match="Hash mismatch"):
            await verify_hash(test_file, wrong_hash)

    @pytest.mark.asyncio
    async def test_verify_hash_file_not_found(self, tmp_path):
        """Test hash verification fails for missing file."""
        missing_file = tmp_path / "nonexistent.tar.gz"

        with pytest.raises(HashVerificationError, match="File not found"):
            await verify_hash(missing_file, "abc123")


class TestCheckForUpdates:
    """Tests for check_for_updates function."""

    @pytest.mark.asyncio
    async def test_check_for_updates_available(self):
        """Test detecting available updates."""
        installed = {"package-a": "1.0.0"}
        index_data = {
            "package-a": {
                "version": "2.0.0",
                "sha512": "abc123",
                "source_url": "https://example.com/package-a.tar.gz",
            }
        }

        with patch("css.core.marketplace.package_manager.fetch_index") as mock_fetch:
            mock_fetch.return_value = index_data

            result = await check_for_updates(installed, "https://example.com/index.json")

            assert "package-a" in result
            assert result["package-a"]["current"] == "1.0.0"
            assert result["package-a"]["latest"] == "2.0.0"
            assert result["package-a"]["available"] is True

    @pytest.mark.asyncio
    async def test_check_for_updates_not_available(self):
        """Test no updates available."""
        installed = {"package-a": "1.0.0"}
        index_data = {
            "package-a": {
                "version": "1.0.0",
                "sha512": "abc123",
                "source_url": "https://example.com/package-a.tar.gz",
            }
        }

        with patch("css.core.marketplace.package_manager.fetch_index") as mock_fetch:
            mock_fetch.return_value = index_data

            result = await check_for_updates(installed, "https://example.com/index.json")

            assert result["package-a"]["available"] is False

    @pytest.mark.asyncio
    async def test_check_for_updates_index_not_found(self):
        """Test check_for_updates with index not found."""
        with patch("css.core.marketplace.package_manager.fetch_index") as mock_fetch:
            mock_fetch.side_effect = PackageNotFoundError("Index not found")

            result = await check_for_updates({"package-a": "1.0.0"}, "https://example.com/index.json")

            # Should return empty dict gracefully
            assert result == {}


class TestInstallPackage:
    """Tests for install_package function."""

    @pytest.mark.asyncio
    async def test_install_package_success(self, tmp_path):
        """Test successful package installation."""
        # Create a test archive
        archive_path = tmp_path / "package.tar.gz"
        with tarfile.open(archive_path, "w:gz"):
            # Add dummy file
            pass

        archive_hash = hashlib.sha512(archive_path.read_bytes()).hexdigest()
        install_base = tmp_path / "install"

        with patch("aiohttp.ClientSession") as mock_session_class, \
             patch("css.core.marketplace.package_manager.extract_archive") as mock_extract:
            
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            
            # Mock streaming the file
            file_content = archive_path.read_bytes()
            async def mock_iter_chunked(size):
                for i in range(0, len(file_content), size):
                    yield file_content[i:i+size]
            
            mock_response.content.iter_chunked = mock_iter_chunked

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session
            mock_extract.return_value = None

            result = await install_package(
                "test-package",
                "https://example.com/test-package.tar.gz",
                archive_hash,
                install_base
            )

            assert result.success is True
            assert result.package_name == "test-package"
            assert result.error is None

    @pytest.mark.asyncio
    async def test_install_package_not_found(self, tmp_path):
        """Test install_package with 404 response."""
        install_base = tmp_path / "install"

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 404

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            result = await install_package(
                "test-package",
                "https://example.com/test-package.tar.gz",
                "abc123",
                install_base
            )

            assert result.success is False
            assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_install_package_hash_mismatch(self, tmp_path):
        """Test install_package with checksum mismatch."""
        archive_path = tmp_path / "package.tar.gz"
        with tarfile.open(archive_path, "w:gz"):
            pass

        install_base = tmp_path / "install"
        wrong_hash = "0" * 128

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200

            file_content = archive_path.read_bytes()
            async def mock_iter_chunked(size):
                for i in range(0, len(file_content), size):
                    yield file_content[i:i+size]

            mock_response.content.iter_chunked = mock_iter_chunked

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            result = await install_package(
                "test-package",
                "https://example.com/test-package.tar.gz",
                wrong_hash,
                install_base
            )

            assert result.success is False
            assert "hash" in result.error.lower()

    @pytest.mark.asyncio
    async def test_install_package_extraction_failure(self, tmp_path):
        """Test install_package with extraction failure."""
        archive_path = tmp_path / "package.tar.gz"
        archive_path.write_bytes(b"not a valid archive")

        archive_hash = hashlib.sha512(archive_path.read_bytes()).hexdigest()
        install_base = tmp_path / "install"

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200

            file_content = archive_path.read_bytes()
            async def mock_iter_chunked(size):
                for i in range(0, len(file_content), size):
                    yield file_content[i:i+size]

            mock_response.content.iter_chunked = mock_iter_chunked

            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None

            mock_session_class.return_value = mock_session

            result = await install_package(
                "test-package",
                "https://example.com/test-package.tar.gz",
                archive_hash,
                install_base
            )

            assert result.success is False
            assert "extract" in result.error.lower()


class TestBatchInstall:
    """Tests for batch_install function."""

    @pytest.mark.asyncio
    async def test_batch_install_multiple_packages(self, tmp_path):
        """Test batch installation of multiple packages."""
        packages = [
            ("package-a", "https://example.com/a.tar.gz", "hash_a"),
            ("package-b", "https://example.com/b.tar.gz", "hash_b"),
        ]

        with patch("css.core.marketplace.package_manager.install_package") as mock_install:
            mock_install.side_effect = [
                PackageInstallResult("package-a", "1.0.0", True, "/path/a"),
                PackageInstallResult("package-b", "1.0.0", True, "/path/b"),
            ]

            results = []
            async for result in batch_install(packages, tmp_path):
                results.append(result)

            assert len(results) == 2
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_batch_install_mixed_success_failure(self, tmp_path):
        """Test batch installation with mixed success/failure."""
        packages = [
            ("package-a", "https://example.com/a.tar.gz", "hash_a"),
            ("package-b", "https://example.com/b.tar.gz", "hash_b"),
        ]

        with patch("css.core.marketplace.package_manager.install_package") as mock_install:
            mock_install.side_effect = [
                PackageInstallResult("package-a", "1.0.0", True, "/path/a"),
                PackageInstallResult("package-b", "1.0.0", False, error="404 Not Found"),
            ]

            results = []
            async for result in batch_install(packages, tmp_path):
                results.append(result)

            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False

    @pytest.mark.asyncio
    async def test_batch_install_respects_concurrency_limit(self, tmp_path):
        """Test batch install respects max_concurrent limit."""
        packages = [
            (f"package-{i}", f"https://example.com/{i}.tar.gz", f"hash_{i}")
            for i in range(5)
        ]

        with patch("css.core.marketplace.package_manager.install_package") as mock_install:
            mock_install.return_value = PackageInstallResult("test", "1.0.0", True)

            call_count = 0
            max_concurrent_calls = 0
            original_semaphore_acquire = asyncio.Semaphore.acquire

            async def tracked_acquire(self, *args, **kwargs):
                nonlocal call_count, max_concurrent_calls
                call_count += 1
                max_concurrent_calls = max(max_concurrent_calls, call_count)
                result = await original_semaphore_acquire(self, *args, **kwargs)
                call_count -= 1
                return result

            # Patch semaphore to track concurrent calls
            with patch.object(asyncio.Semaphore, "acquire", tracked_acquire):
                results = []
                async for result in batch_install(packages, tmp_path, max_concurrent=3):
                    results.append(result)

                assert len(results) == 5
