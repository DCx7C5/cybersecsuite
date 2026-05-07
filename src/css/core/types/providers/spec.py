"""Typed provider YAML schema (Phase 6)."""

from __future__ import annotations

from pathlib import Path

import msgspec


class ProviderAuth(msgspec.Struct, frozen=True):
    """Authentication settings for a provider."""

    api_key_env: str | None = None
    header: str = "Authorization"
    scheme: str = "Bearer"


class ProviderEndpoint(msgspec.Struct, frozen=True):
    """Provider endpoint paths."""

    completion: str = "/chat/completions"


class ProviderCapabilities(msgspec.Struct, frozen=True):
    """Provider feature capabilities."""

    streaming: bool = True
    vision: bool = False
    tool_use: bool = False


class ProviderSpec(msgspec.Struct, frozen=True):
    """Provider declaration used by HttpProviderAdapter and registry."""

    name: str
    display_name: str
    base_url: str
    api_type: str = "openai_compatible"
    models: list[str] = msgspec.field(default_factory=list)
    auth: ProviderAuth = msgspec.field(default_factory=ProviderAuth)
    endpoints: ProviderEndpoint = msgspec.field(default_factory=ProviderEndpoint)
    capabilities: ProviderCapabilities = msgspec.field(default_factory=ProviderCapabilities)

    @property
    def api_key_env(self) -> str | None:
        return self.auth.api_key_env

    @property
    def completion_endpoint(self) -> str:
        return self.endpoints.completion

    @property
    def streaming(self) -> bool:
        return self.capabilities.streaming

    @property
    def vision(self) -> bool:
        return self.capabilities.vision

    @property
    def tool_use(self) -> bool:
        return self.capabilities.tool_use


def decode_provider_spec_yaml(payload: bytes | str) -> ProviderSpec:
    """Decode one ProviderSpec from YAML content."""
    try:
        import msgspec.yaml as msgspec_yaml
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("YAML decoding requires msgspec[yaml] support") from exc
    return msgspec_yaml.decode(payload, type=ProviderSpec)


def decode_provider_spec_file(path: str | Path) -> ProviderSpec:
    """Decode one ProviderSpec from a YAML file."""
    payload = Path(path).read_bytes()
    return decode_provider_spec_yaml(payload)


__all__ = [
    "ProviderAuth",
    "ProviderEndpoint",
    "ProviderCapabilities",
    "ProviderSpec",
    "decode_provider_spec_yaml",
    "decode_provider_spec_file",
]
