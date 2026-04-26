export type ProviderAuthMethod = 'oauth' | 'device_flow' | 'api_key' | 'browser' | 'none'

export interface ProviderAuthConfig {
  supported: ProviderAuthMethod[]
  instructions: Partial<Record<ProviderAuthMethod, string>>
  oauthScopes?: string[]
}

const DEFAULT_INSTRUCTIONS: Record<ProviderAuthMethod, string> = {
  api_key: 'Paste the API key from your provider dashboard and save it to the vault-backed account store.',
  oauth: 'Start OAuth, approve access in the provider page, then paste the returned code or token.',
  device_flow: 'Open the verification URL, enter the user code, and keep this modal open while polling completes.',
  browser: 'Add browser session credentials (cookie/token) to enable browser-backed authentication.',
  none: 'This provider does not require authentication.',
}

export const providerAuthConfig: Record<string, ProviderAuthConfig> = {
  openai: {
    supported: ['api_key'],
    instructions: { api_key: 'Get your API key at https://platform.openai.com/api-keys.' },
  },
  anthropic: {
    supported: ['api_key'],
    instructions: { api_key: 'Create an API key in the Anthropic console under API Keys.' },
  },
  gemini: {
    supported: ['api_key'],
    instructions: { api_key: 'Use a Google AI Studio key or Vertex-compatible token for Gemini access.' },
  },
  deepseek: {
    supported: ['api_key'],
    instructions: { api_key: 'Use a DeepSeek API key from the DeepSeek developer console.' },
  },
  groq: {
    supported: ['api_key'],
    instructions: { api_key: 'Create a Groq API key and paste it here.' },
  },
  mistral: {
    supported: ['api_key'],
    instructions: { api_key: 'Create a Mistral API key and store it as a provider account.' },
  },
  xai: {
    supported: ['api_key', 'oauth'],
    instructions: {
      api_key: 'Use your xAI API key for direct API calls.',
      oauth: 'Use X OAuth if you prefer account-linked credentials.',
    },
  },
  together: {
    supported: ['api_key'],
    instructions: { api_key: 'Use a Together API key from your account settings.' },
  },
  replicate: {
    supported: ['api_key'],
    instructions: { api_key: 'Use your Replicate token from account API tokens.' },
  },
  cohere: {
    supported: ['api_key'],
    instructions: { api_key: 'Create a Cohere API key and add it here.' },
  },
  ollama: {
    supported: ['none'],
    instructions: { none: 'Local Ollama instances typically do not require provider authentication.' },
  },
  lmstudio: {
    supported: ['none'],
    instructions: { none: 'Local LM Studio endpoints generally do not require provider authentication.' },
  },
  'azure-openai': {
    supported: ['api_key', 'oauth'],
    instructions: {
      api_key: 'Use Azure OpenAI resource key credentials.',
      oauth: 'Use Entra ID OAuth tokens if your deployment is configured for token auth.',
    },
  },
  perplexity: {
    supported: ['api_key'],
    instructions: { api_key: 'Use your Perplexity API key from developer settings.' },
  },
  huggingface: {
    supported: ['api_key', 'oauth'],
    instructions: {
      api_key: 'Use a Hugging Face access token with the required scopes.',
      oauth: 'OAuth can be used when operating through Hugging Face account integrations.',
    },
  },
}

export function normalizeAuthMethod(method: string | null | undefined): ProviderAuthMethod | null {
  const value = String(method || '').trim().toLowerCase()
  if (!value) return null
  if (value === 'device' || value === 'device-flow') return 'device_flow'
  if (value === 'oauth') return 'oauth'
  if (value === 'api_key' || value === 'apikey') return 'api_key'
  if (value === 'browser') return 'browser'
  if (value === 'none') return 'none'
  return null
}

export function resolveProviderAuthConfig(
  providerId: string,
  availableMethods: string[],
  fallbackAuthType?: string
): ProviderAuthConfig {
  const configured = providerAuthConfig[providerId]
  const fallbackMethod = normalizeAuthMethod(fallbackAuthType)
  const normalizedAvailable = availableMethods
    .map((method) => normalizeAuthMethod(method))
    .filter((method): method is ProviderAuthMethod => method !== null)

  const supported = normalizedAvailable.length > 0
    ? Array.from(new Set(normalizedAvailable))
    : configured?.supported ?? (fallbackMethod ? [fallbackMethod] : ['api_key'])

  const instructions = {
    ...DEFAULT_INSTRUCTIONS,
    ...(configured?.instructions ?? {}),
  }

  return {
    supported,
    instructions,
    oauthScopes: configured?.oauthScopes,
  }
}
