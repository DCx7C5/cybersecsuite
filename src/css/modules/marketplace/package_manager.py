"""Marketplace package manager — fetch, verify, and install packages.

Core functions:
- fetch_index: Download marketplace index
- verify_hash: Verify package checksums
- check_for_updates: Check if updates are available
- install_package: Install a single package
- batch_install: Install multiple packages

Error handling:
- 404: Package or index not found
- Checksum mismatch: Hash verification failed
- Extraction failure: Archive extraction error
"""

import asyncio
import hashlib
import logging
import tarfile
from pathlib import Path
from typing import AsyncIterator
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PackageMetadata:
    """Package metadata from index."""
    name: str
    version: str
    sha512: str
    source_url: str
    description: str = ""
    release_date: str = ""


@dataclass
class PackageInstallResult:
    """Result of package installation."""
    package_name: str
    version: str
    success: bool
    install_path: str | None = None
    error: str | None = None
    installed_at: datetime | None = None


class MarketplaceError(Exception):
    """Base marketplace error."""
    pass


class PackageNotFoundError(MarketplaceError):
    """Package or index not found (404)."""
    pass


class HashVerificationError(MarketplaceError):
    """Checksum verification failed."""
    pass


class ExtractionError(MarketplaceError):
    """Archive extraction failed."""
    pass


async def fetch_index(index_url: str) -> dict:
    """Fetch marketplace index from remote URL.
    
    Args:
        index_url: URL to marketplace index (JSON format)
        
    Returns:
        Dictionary containing package metadata by name
        
    Raises:
        PackageNotFoundError: If index URL returns 404 or is unreachable
    """
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(index_url, timeout=30) as resp:
                if resp.status == 404:
                    raise PackageNotFoundError(f"Marketplace index not found: {index_url}")
                if resp.status != 200:
                    raise MarketplaceError(f"Failed to fetch index: {resp.status}")
                return await resp.json()
    except asyncio.TimeoutError:
        raise MarketplaceError(f"Timeout fetching marketplace index")
    except Exception as e:
        if isinstance(e, (PackageNotFoundError, MarketplaceError)):
            raise
        raise MarketplaceError(f"Error fetching marketplace index: {str(e)}")


async def verify_hash(file_path: Path, expected_hash: str, algorithm: str = "sha512") -> bool:
    """Verify file hash matches expected value.
    
    Args:
        file_path: Path to file to verify
        expected_hash: Expected hash value (hex string)
        algorithm: Hash algorithm (default sha512)
        
    Returns:
        True if hash matches, False otherwise
        
    Raises:
        HashVerificationError: If verification fails
    """
    if not file_path.exists():
        raise HashVerificationError(f"File not found: {file_path}")
    
    hasher = hashlib.new(algorithm)
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        
        actual_hash = hasher.hexdigest()
        if actual_hash != expected_hash.lower():
            raise HashVerificationError(
                f"Hash mismatch for {file_path.name}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        return True
    except FileNotFoundError:
        raise HashVerificationError(f"File not found during verification: {file_path}")
    except Exception as e:
        if isinstance(e, HashVerificationError):
            raise
        raise HashVerificationError(f"Hash verification error: {str(e)}")


async def check_for_updates(
    installed_packages: dict[str, str],
    index_url: str
) -> dict[str, dict]:
    """Check if updates are available for installed packages.
    
    Args:
        installed_packages: Dict mapping package name to installed version
        index_url: URL to marketplace index
        
    Returns:
        Dict of packages with updates available:
        {package_name: {current: str, latest: str, available: bool}}
    """
    try:
        index = await fetch_index(index_url)
    except PackageNotFoundError:
        logger.warning(f"Could not check for updates: index not found")
        return {}
    
    updates = {}
    for package_name, current_version in installed_packages.items():
        if package_name in index:
            latest_version = index[package_name].get("version", "0.0.0")
            updates[package_name] = {
                "current": current_version,
                "latest": latest_version,
                "available": latest_version != current_version,
            }
    
    return updates


async def extract_archive(archive_path: Path, extract_to: Path) -> None:
    """Extract tar/tar.gz archive.
    
    Args:
        archive_path: Path to archive file
        extract_to: Directory to extract into
        
    Raises:
        ExtractionError: If extraction fails
    """
    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, "r:*") as tar:
            tar.extractall(path=extract_to)
    except tarfile.TarError as e:
        raise ExtractionError(f"Failed to extract archive {archive_path.name}: {str(e)}")
    except Exception as e:
        raise ExtractionError(f"Extraction error: {str(e)}")


async def install_package(
    package_name: str,
    package_url: str,
    package_hash: str,
    install_path: Path
) -> PackageInstallResult:
    """Install a single package from marketplace.
    
    Args:
        package_name: Name of package
        package_url: URL to download package from
        package_hash: Expected SHA512 hash
        install_path: Path to install into
        
    Returns:
        PackageInstallResult with success status and details
    """
    try:
        download_path = install_path.parent / f"{package_name}.tar.gz"
        
        # Download package
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(package_url, timeout=60) as resp:
                    if resp.status == 404:
                        raise PackageNotFoundError(f"Package not found: {package_url}")
                    if resp.status != 200:
                        raise MarketplaceError(f"Download failed: {resp.status}")
                    
                    with open(download_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(65536):
                            f.write(chunk)
        except asyncio.TimeoutError:
            raise MarketplaceError(f"Timeout downloading package")
        except PackageNotFoundError:
            raise
        
        # Verify hash
        await verify_hash(download_path, package_hash)
        
        # Extract archive
        extract_path = install_path / package_name
        await extract_archive(download_path, extract_path)
        
        # Clean up archive
        download_path.unlink()
        
        return PackageInstallResult(
            package_name=package_name,
            version="0.1.0",
            success=True,
            install_path=str(extract_path),
            installed_at=datetime.now(),
        )
    except (PackageNotFoundError, HashVerificationError, ExtractionError) as e:
        return PackageInstallResult(
            package_name=package_name,
            version="0.1.0",
            success=False,
            error=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error installing {package_name}: {e}")
        return PackageInstallResult(
            package_name=package_name,
            version="0.1.0",
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


async def batch_install(
    packages: list[tuple[str, str, str]],
    install_base: Path,
    max_concurrent: int = 3
) -> AsyncIterator[PackageInstallResult]:
    """Install multiple packages concurrently with rate limiting.
    
    Args:
        packages: List of (package_name, url, hash) tuples
        install_base: Base directory for installations
        max_concurrent: Maximum concurrent downloads
        
    Yields:
        PackageInstallResult for each installed package
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def install_with_limit(package_name: str, url: str, hash_val: str):
        async with semaphore:
            result = await install_package(
                package_name=package_name,
                package_url=url,
                package_hash=hash_val,
                install_path=install_base
            )
            return result
    
    tasks = [
        install_with_limit(pkg_name, url, hash_val)
        for pkg_name, url, hash_val in packages
    ]
    
    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            yield result
        except Exception as e:
            logger.exception(f"Error during batch installation: {e}")


__all__ = [
    "PackageMetadata",
    "PackageInstallResult",
    "MarketplaceError",
    "PackageNotFoundError",
    "HashVerificationError",
    "ExtractionError",
    "fetch_index",
    "verify_hash",
    "check_for_updates",
    "install_package",
    "batch_install",
]
