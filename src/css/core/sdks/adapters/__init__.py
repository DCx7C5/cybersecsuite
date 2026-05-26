"""SDK adapter implementations — NativeSDK, HTTP, Ollama, Browser Relay."""

from .anthropic import AnthropicNativeAdapter, COMPUTER_USE_TOOLS
from .openai import OpenAINativeAdapter, BUILTIN_TOOLS
from .browser_relay import BrowserRelayAdapter
from .http_provider import HttpProviderAdapter
from .ollama import OllamaAdapter

__all__ = [
    "AnthropicNativeAdapter",
    "COMPUTER_USE_TOOLS",
    "OpenAINativeAdapter",
    "BUILTIN_TOOLS",
    "BrowserRelayAdapter",
    "HttpProviderAdapter",
    "OllamaAdapter",
]
