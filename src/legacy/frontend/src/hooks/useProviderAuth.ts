import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchApi } from '@/hooks/useApi'
import { normalizeAuthMethod, type ProviderAuthMethod } from '@/config/providerAuthMethods'

export interface ProviderAuthAccount {
  account_id: string
  vault_key: string
  provider_id: string
  label?: string | null
  auth_method?: string | null
  email?: string | null
  display_name?: string | null
  subject?: string | null
  tenant?: string | null
  active?: boolean
  test_status?: string | null
}

interface InitiateResponse {
  status: string
  auth_flow_id?: string
  oauth_url?: string
  state?: string
  device_code?: string
  user_code?: string
  verification_uri?: string
  interval?: number
  expires_in?: number
}

interface VerifyResponse {
  status: 'active' | 'pending' | 'expired'
  account?: ProviderAuthAccount
  auth_flow_id?: string
  user_code?: string
  verification_uri?: string
  interval?: number
  expires_in?: number
  error?: string
}

interface VerifyPayload {
  providerId: string
  authMethod: ProviderAuthMethod
  authFlowId?: string
  code?: string
  apiKey?: string
  credentials?: Record<string, unknown>
  state?: string
  codeVerifier?: string
  label?: string
  displayName?: string
  email?: string
  subject?: string
  tenant?: string
  approved?: boolean
}

function authErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  return String(error)
}

export function useProviderAuth() {
  const [isPolling, setIsPolling] = useState(false)
  const [authFlowId, setAuthFlowId] = useState<string | null>(null)
  const [oauthUrl, setOauthUrl] = useState<string | null>(null)
  const [oauthState, setOauthState] = useState<string | null>(null)
  const [deviceCode, setDeviceCode] = useState<string | null>(null)
  const [userCode, setUserCode] = useState<string | null>(null)
  const [verificationUri, setVerificationUri] = useState<string | null>(null)
  const [expiresIn, setExpiresIn] = useState<number | null>(null)
  const [account, setAccount] = useState<ProviderAuthAccount | null>(null)
  const [error, setError] = useState<string | null>(null)

  const pollingTimerRef = useRef<number | null>(null)
  const pollingStoppedRef = useRef(false)

  const stopPolling = useCallback(() => {
    pollingStoppedRef.current = true
    if (pollingTimerRef.current !== null) {
      window.clearTimeout(pollingTimerRef.current)
      pollingTimerRef.current = null
    }
    setIsPolling(false)
  }, [])

  const clearFlowState = useCallback(() => {
    stopPolling()
    setAuthFlowId(null)
    setOauthUrl(null)
    setOauthState(null)
    setDeviceCode(null)
    setUserCode(null)
    setVerificationUri(null)
    setExpiresIn(null)
  }, [stopPolling])

  const clearError = useCallback(() => setError(null), [])

  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  const pollDeviceFlow = useCallback(async (providerId: string, flowId: string, startInterval: number) => {
    pollingStoppedRef.current = false
    setIsPolling(true)

    let intervalSeconds = Math.max(3, startInterval || 8)
    let retries = 0

    const tick = async () => {
      if (pollingStoppedRef.current) {
        return
      }

      try {
        const response = await fetchApi<VerifyResponse>(`/api/providers/${providerId}/auth/verify`, {
          method: 'POST',
          body: JSON.stringify({
            auth_method: 'device_flow',
            auth_flow_id: flowId,
          }),
        })

        if (response.status === 'active' && response.account) {
          setAccount(response.account)
          clearFlowState()
          return
        }

        if (response.status === 'expired') {
          setError(response.error ?? 'Device code expired.')
          clearFlowState()
          return
        }

        retries += 1
        if (retries % 4 === 0) {
          intervalSeconds = Math.min(30, intervalSeconds * 2)
        }

        if (typeof response.expires_in === 'number') {
          setExpiresIn(response.expires_in)
        }
      } catch (err) {
        retries += 1
        intervalSeconds = Math.min(30, intervalSeconds * 2)
        setError(authErrorMessage(err))
      }

      if (!pollingStoppedRef.current) {
        pollingTimerRef.current = window.setTimeout(() => {
          void tick()
        }, intervalSeconds * 1000)
      }
    }

    await tick()
  }, [clearFlowState])

  const initiate = useCallback(async (providerId: string, authMethod: ProviderAuthMethod) => {
    setError(null)
    setAccount(null)
    clearFlowState()

    const response = await fetchApi<InitiateResponse>(`/api/providers/${providerId}/auth/initiate`, {
      method: 'POST',
      body: JSON.stringify({ auth_method: authMethod }),
    })

    if (response.auth_flow_id) setAuthFlowId(response.auth_flow_id)
    if (response.oauth_url) setOauthUrl(response.oauth_url)
    if (response.state) setOauthState(response.state)
    if (response.device_code) setDeviceCode(response.device_code)
    if (response.user_code) setUserCode(response.user_code)
    if (response.verification_uri) setVerificationUri(response.verification_uri)
    if (typeof response.expires_in === 'number') setExpiresIn(response.expires_in)

    if (authMethod === 'device_flow' && response.auth_flow_id) {
      void pollDeviceFlow(providerId, response.auth_flow_id, response.interval ?? 8)
    }

    return response
  }, [clearFlowState, pollDeviceFlow])

  const verify = useCallback(async (payload: VerifyPayload) => {
    setError(null)

    const normalizedMethod = normalizeAuthMethod(payload.authMethod)
    if (!normalizedMethod) {
      throw new Error('Unsupported authentication method.')
    }

    const body: Record<string, unknown> = {
      auth_method: normalizedMethod,
      auth_flow_id: payload.authFlowId,
      code: payload.code,
      api_key: payload.apiKey,
      credentials: payload.credentials,
      state: payload.state,
      code_verifier: payload.codeVerifier,
      label: payload.label,
      display_name: payload.displayName,
      email: payload.email,
      subject: payload.subject,
      tenant: payload.tenant,
      approved: payload.approved,
    }

    const response = await fetchApi<VerifyResponse>(`/api/providers/${payload.providerId}/auth/verify`, {
      method: 'POST',
      body: JSON.stringify(body),
    })

    if (response.status === 'active' && response.account) {
      setAccount(response.account)
      clearFlowState()
      return response
    }

    if (response.status === 'expired') {
      setError(response.error ?? 'Authentication flow expired.')
      clearFlowState()
      return response
    }

    if (typeof response.expires_in === 'number') setExpiresIn(response.expires_in)
    return response
  }, [clearFlowState])

  const revoke = useCallback(async (providerId: string, accountId: string) => {
    return await fetchApi<{ ok: boolean }>(`/api/providers/${providerId}/auth/revoke`, {
      method: 'POST',
      body: JSON.stringify({ account_id: accountId }),
    })
  }, [])

  const cancelPolling = useCallback(() => {
    stopPolling()
  }, [stopPolling])

  return {
    initiate,
    verify,
    revoke,
    cancelPolling,
    isPolling,
    authFlowId,
    oauthUrl,
    oauthState,
    deviceCode,
    userCode,
    verificationUri,
    expiresIn,
    account,
    error,
    clearError,
  }
}
