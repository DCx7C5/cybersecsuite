"""Typed provider YAML schema (Phase 6)."""

from pathlib import Path
from typing import Literal

import msgspec
import msgspec.yaml as msgspec_yaml


AuthMethod = Literal["api_key", "oauth2", "device_flow"]
OAuthFlow = Literal["authorization_code", "device_code"]


class ProviderOAuthFlow(msgspec.Struct, frozen=True, kw_only=True):
    """Declared OAuth flow metadata; token acquisition is owned by core/authentication."""

    flow: OAuthFlow
    token_url: str
    authorization_url: str | None = None
    device_authorization_url: str | None = None
    scopes: list[str] = msgspec.field(default_factory=list)


class ProviderAuth(msgspec.Struct, frozen=True, kw_only=True):
    """Authentication settings for a provider."""

    methods: list[AuthMethod] = msgspec.field(default_factory=lambda: ["api_key"])
    api_key_env: str | None = None
    header: str = "Authorization"
    scheme: str = "Bearer"
    oauth_flows: list[ProviderOAuthFlow] = msgspec.field(default_factory=list)


class ProviderEndpoint(msgspec.Struct, frozen=True, kw_only=True):
    """Provider endpoint paths."""

    completion: str = "/chat/completions"


class ProviderCapabilities(msgspec.Struct, frozen=True, kw_only=True):
    """Provider feature capabilities."""

    streaming: bool = True
    vision: bool = False
    tool_use: bool = False


class ProviderSpec(msgspec.Struct, frozen=True, kw_only=True):
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
    return msgspec_yaml.decode(payload, type=ProviderSpec)


def decode_provider_spec_file(path: str | Path) -> ProviderSpec:
    """Decode one ProviderSpec from a YAML file."""
    payload = Path(path).read_bytes()
    return decode_provider_spec_yaml(payload)
