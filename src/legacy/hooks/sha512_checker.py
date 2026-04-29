"""SHA512 verification for marketplace index to ensure integrity and update detection."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

log = logging.getLogger(__name__)

MARKETPLACE_ROOT = Path.home() / ".cybersecsuite" / "marketplace"
SHA512_CACHE_FILE = MARKETPLACE_ROOT / "index.json.sha512"
INDEX_CACHE_FILE = MARKETPLACE_ROOT / "index.json"


async def download_file(url: str) -> bytes:
    """Download a file from URL and return its contents."""
    try:
        import httpx
    except ImportError:
        raise ImportError("httpx required for downloading; install via 'uv add httpx'")

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30.0)
        resp.raise_for_status()
        return resp.content


def compute_sha512(data: bytes) -> str:
    """Compute SHA512 hash of data."""
    return hashlib.sha512(data).hexdigest()


async def check_index_update(
    remote_sha512_url: str = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512",
    remote_index_url: str = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json",
) -> tuple[bool, Optional[bytes]]:
    """Check if marketplace index has been updated.
    
    Returns:
        (has_update: bool, index_data: bytes | None)
        - If True: index_data is the new index.json content
        - If False: index_data is None (use cached version)
    """
    MARKETPLACE_ROOT.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download remote SHA512
        remote_sha512_data = await download_file(remote_sha512_url)
        remote_sha512 = remote_sha512_data.decode('utf-8').strip()
        
        log.debug(f"Remote SHA512: {remote_sha512[:16]}...")
        
        # Check if we have cached SHA512
        if SHA512_CACHE_FILE.exists():
            cached_sha512 = SHA512_CACHE_FILE.read_text().strip()
            log.debug(f"Cached SHA512: {cached_sha512[:16]}...")
            
            if cached_sha512 == remote_sha512:
                log.info("Marketplace index is up-to-date")
                return False, None
            else:
                log.info(f"Marketplace index has update: {cached_sha512[:16]}... → {remote_sha512[:16]}...")
        else:
            log.info("No cached marketplace index SHA512; downloading fresh")
        
        # Download and verify new index
        index_data = await download_file(remote_index_url)
        computed_sha512 = compute_sha512(index_data)
        
        if computed_sha512 != remote_sha512:
            raise ValueError(
                f"Index SHA512 mismatch! Expected {remote_sha512}, got {computed_sha512}. "
                "Possible security issue or corrupted download."
            )
        
        # Cache the new SHA512
        SHA512_CACHE_FILE.write_text(remote_sha512)
        log.info("Verified and cached new marketplace index SHA512")
        
        return True, index_data
        
    except Exception as e:
        log.error(f"SHA512 check failed: {e}")
        raise


async def verify_and_cache_index(
    index_data: bytes,
    remote_sha512_url: str = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512",
) -> dict:
    """Verify index against remote SHA512 and cache it.
    
    Returns:
        Parsed index as dict
    
    Raises:
        ValueError: If SHA512 verification fails
    """
    MARKETPLACE_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Download expected SHA512
    remote_sha512_data = await download_file(remote_sha512_url)
    remote_sha512 = remote_sha512_data.decode('utf-8').strip()
    
    # Verify the index
    computed_sha512 = compute_sha512(index_data)
    if computed_sha512 != remote_sha512:
        raise ValueError(
            f"Index SHA512 mismatch! Expected {remote_sha512}, got {computed_sha512}. "
            "Possible security issue or corrupted download."
        )
    
    # Parse and cache
    try:
        index_dict = json.loads(index_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in marketplace index: {e}")
    
    # Cache both files
    INDEX_CACHE_FILE.write_bytes(index_data)
    SHA512_CACHE_FILE.write_text(remote_sha512)
    
    log.info("Marketplace index verified, parsed, and cached")
    return index_dict


def get_cached_index() -> Optional[dict]:
    """Load cached marketplace index, if available."""
    if not INDEX_CACHE_FILE.exists():
        return None
    
    try:
        return json.loads(INDEX_CACHE_FILE.read_text())
    except (json.JSONDecodeError, IOError) as e:
        log.warning(f"Failed to load cached marketplace index: {e}")
        return None


def get_core_items(index: dict) -> list[dict]:
    """Extract core (mandatory) items from index."""
    return [item for item in index.get("index", []) if item.get("tier") == "core"]


def get_recommended_items(index: dict) -> list[dict]:
    """Extract recommended items from index."""
    return [item for item in index.get("index", []) if item.get("tier") == "recommended"]
