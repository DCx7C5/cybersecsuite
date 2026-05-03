from enum import Enum


class SDKType(str, Enum):
    SDKLIBRARY = "sdklibrary"
    CUSTOMSDK = "customsdk"
    LOCALSDK = "localsdk"


class APIEndpointType(str, Enum):
    OPENAPI = "openapi"
    WEBLLM = "webllm"
    LOCAL = "local"
    SPECIFIC = "specific"


class ProviderType(str, Enum):
    """Supported API service providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    MISTRAL = "mistral"
    XAI = "xai"
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"
    CEREBRAS = "cerebras"
    TOGETHER = "together"
    GITHUB = "github"
    CLOUDFLARE = "cloudflare"
    FIREWORKS = "fireworks"
    OPENCODE = "opencode"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"
    SAMBANOVA = "sambanova"
    DEEPINFRA = "deepinfra"
    AI21 = "ai21"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    NSCALE = "nscale"
    LAMBDA = "lambda"
