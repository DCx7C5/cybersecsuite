"""Provider schema types."""

from .spec import (
    ProviderAuth,
    ProviderCapabilities,
    ProviderEndpoint,
    ProviderOAuthFlow,
    ProviderSpec,
    decode_provider_spec_file,
    decode_provider_spec_yaml,
)

__all__ = [
    "ProviderAuth",
    "ProviderOAuthFlow",
    "ProviderEndpoint",
    "ProviderCapabilities",
    "ProviderSpec",
    "decode_provider_spec_yaml",
    "decode_provider_spec_file",
]
