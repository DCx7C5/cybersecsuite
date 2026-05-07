from css.core.exceptions import BaseModuleException

class BaseMarketplaceException(BaseModuleException):
    """Base exception for the marketplace module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="marketplace", **kwargs)


class InstallationError(BaseMarketplaceException):
    """Raised when package installation fails."""
    
    def __init__(self, message: str = None, item_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if item_id:
            ctx["item_id"] = item_id
        super().__init__(
            message or f"Installation failed for item: {item_id}" if item_id else "Installation failed",
            context=ctx,
            **kwargs
        )


class DependencyResolutionError(InstallationError):
    """Raised when dependency resolution fails."""
    
    def __init__(self, message: str = None, missing_deps: list[str] = None, **kwargs):
        ctx = kwargs.get("context", {})
        if missing_deps:
            ctx["missing_dependencies"] = missing_deps
        super().__init__(
            message or f"Dependency resolution failed. Missing: {missing_deps}" if missing_deps else "Dependency resolution failed",
            context=ctx,
            **kwargs
        )


class ManifestValidationError(InstallationError):
    """Raised when manifest validation fails."""
    
    def __init__(self, message: str = None, manifest_path: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if manifest_path:
            ctx["manifest_path"] = manifest_path
        super().__init__(
            message or f"Manifest validation failed: {manifest_path}" if manifest_path else "Manifest validation failed",
            context=ctx,
            **kwargs
        )


class PackageNotFoundError(BaseMarketplaceException):
    """Raised when marketplace item is not found."""
    
    def __init__(self, item_id: str, **kwargs):
        ctx = kwargs.get("context", {})
        ctx["item_id"] = item_id
        super().__init__(
            f"Package not found: {item_id}",
            context=ctx,
            **kwargs
        )


class PackageStateError(BaseMarketplaceException):
    """Raised when package state is invalid."""
    
    def __init__(self, message: str = None, current_status: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if current_status:
            ctx["current_status"] = current_status
        super().__init__(
            message or f"Invalid package state: {current_status}" if current_status else "Invalid package state",
            context=ctx,
            **kwargs
        )


class MarketplaceSeedingError(BaseMarketplaceException):
    """Raised when marketplace seeding fails."""
    
    def __init__(self, message: str = None, url: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if url:
            ctx["url"] = url
        super().__init__(
            message or f"Marketplace seeding failed: {url}" if url else "Marketplace seeding failed",
            context=ctx,
            **kwargs
        )
