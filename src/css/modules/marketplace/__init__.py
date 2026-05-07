"""Marketplace module — package management and installation."""

from .package_manager import (
    PackageMetadata,
    PackageInstallResult,
    MarketplaceError,
    PackageNotFoundError,
    HashVerificationError,
    ExtractionError,
    fetch_index,
    verify_hash,
    check_for_updates,
    install_package,
    batch_install,
)

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
