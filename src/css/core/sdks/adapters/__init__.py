"""SDK adapter implementations — NativeSDK, HTTP, Ollama, Browser Relay."""

from .anthropic import AnthropicNativeAdapter, COMPUTER_USE_TOOLS
from .openai import OpenAINativeAdapter, BUILTIN_TOOLS
from .browser_relay import BrowserRelayAdapter
from .deepseek import DeepSeekAdapter
from .http_provider import HttpProviderAdapter
from .ollama import OllamaAdapter
