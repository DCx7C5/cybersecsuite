from enum import Enum
from functools import lru_cache
from pathlib import Path


class SDKType(str, Enum):
    SDKLIBRARY = "sdklibrary"
    CUSTOMSDK = "customsdk"
    LOCALSDK = "localsdk"


class APIEndpointType(str, Enum):
    OPENAPI = "openapi"
    WEBLLM = "webllm"
    LOCAL = "local"
    SPECIFIC = "specific"


def _normalize_provider_slug(slug: str) -> str:
    """Normalize provider slugs to canonical runtime IDs."""
    normalized = slug.strip().lower()
    alias_map = {
        "lambda_api": "lambda",
    }
    return alias_map.get(normalized, normalized)


def _read_provider_slug_from_spec(spec_file: Path) -> str | None:
    """Read top-level `name:` from spec.yaml without importing provider code."""
    try:
        for line in spec_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("name:"):
                value = stripped.split(":", 1)[1].strip().strip("'\"")
                if value:
                    return _normalize_provider_slug(value)
                return None
    except OSError:
        return None
    return None


def _provider_slug_from_path(provider_dir: Path) -> str:
    """Resolve runtime provider slug from directory and optional spec.yaml."""
    spec_file = provider_dir / "spec.yaml"
    if spec_file.exists():
        spec_slug = _read_provider_slug_from_spec(spec_file)
        if spec_slug:
            return spec_slug
    return _normalize_provider_slug(provider_dir.name.lower())


@lru_cache(maxsize=1)
def discover_provider_ids() -> tuple[str, ...]:
    """Return provider IDs discovered from api_services directories/specs."""
    api_services_path = Path(__file__).resolve().parent
    providers = {
        _provider_slug_from_path(provider_dir)
        for provider_dir in api_services_path.iterdir()
        if provider_dir.is_dir() and not provider_dir.name.startswith("_")
    }
    return tuple(sorted(providers))
