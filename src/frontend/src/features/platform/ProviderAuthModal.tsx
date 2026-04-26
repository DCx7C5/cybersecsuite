import { useEffect, useState } from 'react'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Badge from '@/components/ui/Badge'
import { resolveProviderAuthConfig, normalizeAuthMethod, type ProviderAuthMethod } from '@/config/providerAuthMethods'
import { useProviderAuth } from '@/hooks/useProviderAuth'

interface ProviderAuthMethodEntry {
  auth_method: string
  config?: Record<string, unknown>
}

interface ProviderRow {
  id: string
  name: string
  auth_type: string
  auth_methods?: ProviderAuthMethodEntry[]
}

interface ProviderAuthModalProps {
  open: boolean
  provider: ProviderRow | null
  defaultMethod?: string | null
  onClose: () => void
  onSuccess: () => void
}

const METHOD_LABELS: Record<ProviderAuthMethod, string> = {
  api_key: 'API Key',
  oauth: 'OAuth',
  device_flow: 'Device Flow',
  browser: 'Browser Session',
  none: 'No Auth',
}

export default function ProviderAuthModal({
  open,
  provider,
  defaultMethod,
  onClose,
  onSuccess,
}: ProviderAuthModalProps) {
  const [selectedMethod, setSelectedMethod] = useState<ProviderAuthMethod>('api_key')
  const [label, setLabel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [oauthCode, setOauthCode] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [tenant, setTenant] = useState('')

  const {
    initiate,
    verify,
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
  } = useProviderAuth()

  const availableMethods = provider?.auth_methods?.map((m) => m.auth_method) ?? []
  const config = provider
    ? resolveProviderAuthConfig(provider.id, availableMethods, provider.auth_type)
    : resolveProviderAuthConfig('', [], 'api_key')
  const methods = config.supported.filter((method) => method !== 'none')

  useEffect(() => {
    if (!provider || !open) return
    clearError()
    setLabel('')
    setApiKey('')
    setOauthCode('')
    setDisplayName('')
    setEmail('')
    setSubject('')
    setTenant('')

    const preferred = normalizeAuthMethod(defaultMethod || undefined)
    if (preferred && preferred !== 'none' && methods.includes(preferred)) {
      setSelectedMethod(preferred)
      return
    }
    setSelectedMethod(methods[0] ?? 'api_key')
  }, [provider, open, defaultMethod, clearError, methods])

  useEffect(() => {
    if (!account || !open) return
    onSuccess()
    onClose()
  }, [account, open, onClose, onSuccess])

  if (!provider) {
    return null
  }

  const instruction = config.instructions[selectedMethod]

  const saveDirectCredentials = async () => {
    if (!provider) return
    await verify({
      providerId: provider.id,
      authMethod: selectedMethod,
      apiKey,
      label: label || undefined,
      displayName: displayName || undefined,
      email: email || undefined,
      subject: subject || undefined,
      tenant: tenant || undefined,
    })
  }

  const startOauth = async () => {
    if (!provider) return
    await initiate(provider.id, 'oauth')
  }

  const completeOauth = async () => {
    if (!provider || !authFlowId) return
    await verify({
      providerId: provider.id,
      authMethod: 'oauth',
      authFlowId,
      code: oauthCode,
      state: oauthState || undefined,
      label: label || undefined,
      displayName: displayName || undefined,
      email: email || undefined,
      subject: subject || undefined,
      tenant: tenant || undefined,
    })
  }

  const startDeviceFlow = async () => {
    if (!provider) return
    await initiate(provider.id, 'device_flow')
  }

  const verifyDeviceFlowNow = async () => {
    if (!provider || !authFlowId) return
    await verify({
      providerId: provider.id,
      authMethod: 'device_flow',
      authFlowId,
      approved: true,
      label: label || undefined,
      displayName: displayName || undefined,
      email: email || undefined,
      subject: subject || undefined,
      tenant: tenant || undefined,
    })
  }

  return (
    <Modal open={open} onClose={() => { cancelPolling(); onClose() }} title={`Connect ${provider.name}`}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minWidth: '560px', maxWidth: '92vw' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            {methods.map((method) => (
              <Button
                key={method}
                variant={selectedMethod === method ? 'primary' : 'ghost'}
                onClick={() => setSelectedMethod(method)}
                style={{ fontSize: '12px', padding: '4px 10px' }}
              >
                {METHOD_LABELS[method]}
              </Button>
            ))}
          </div>
          <Badge variant="info">{provider.id}</Badge>
        </div>

        <div style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          padding: '10px 12px',
          fontSize: '12px',
          color: 'var(--text-muted)',
          lineHeight: 1.5,
        }}>
          {instruction}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <Input label="Label (optional)" value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Main account" />
          <Input label="Display Name (optional)" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Work account" />
          <Input label="Email (optional)" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@example.com" />
          <Input label="Subject (optional)" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Provider user ID" />
          <Input label="Tenant (optional)" value={tenant} onChange={(e) => setTenant(e.target.value)} placeholder="Org or workspace" />
        </div>

        {(selectedMethod === 'api_key' || selectedMethod === 'browser') && (
          <>
            <Input
              label={selectedMethod === 'browser' ? 'Session Token / Cookie' : 'API Key'}
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={selectedMethod === 'browser' ? 'session token' : 'sk-...'}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={() => { void saveDirectCredentials() }} disabled={!apiKey.trim()}>
                Save Account
              </Button>
            </div>
          </>
        )}

        {selectedMethod === 'oauth' && (
          <>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <Button variant="secondary" onClick={() => { void startOauth() }}>
                Start OAuth
              </Button>
              {oauthUrl && (
                <a
                  href={oauthUrl}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: 'var(--accent)', fontSize: '12px', alignSelf: 'center' }}
                >
                  Open provider authorization
                </a>
              )}
            </div>
            {authFlowId && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '10px' }}>
                <Input label="OAuth Code / Access Token" value={oauthCode} onChange={(e) => setOauthCode(e.target.value)} placeholder="Paste returned code/token" />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    state: {oauthState ?? 'n/a'}
                  </span>
                  <Button onClick={() => { void completeOauth() }} disabled={!oauthCode.trim()}>
                    Verify OAuth
                  </Button>
                </div>
              </div>
            )}
          </>
        )}

        {selectedMethod === 'device_flow' && (
          <>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <Button variant="secondary" onClick={() => { void startDeviceFlow() }}>
                Start Device Flow
              </Button>
              {authFlowId && (
                <Button variant="ghost" onClick={() => { void verifyDeviceFlowNow() }}>
                  Check Now
                </Button>
              )}
              {isPolling && <Badge variant="warn">Polling...</Badge>}
            </div>
            {authFlowId && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '10px',
                background: 'var(--surface-2)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                padding: '10px',
              }}>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>USER CODE</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '15px', fontWeight: 700 }}>{userCode ?? '-'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>DEVICE CODE</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{deviceCode ?? '-'}</div>
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>VERIFICATION URL</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', wordBreak: 'break-all' }}>
                    {verificationUri ?? '-'}
                  </div>
                </div>
                <div style={{ gridColumn: '1 / -1', fontSize: '11px', color: 'var(--text-muted)' }}>
                  Expires in: {expiresIn != null ? `${expiresIn}s` : '-'}
                </div>
              </div>
            )}
          </>
        )}

        {error && (
          <div style={{
            color: 'var(--red)',
            background: 'var(--red-glow)',
            border: '1px solid var(--red)',
            borderRadius: 'var(--radius)',
            padding: '8px 10px',
            fontSize: '12px',
          }}>
            {error}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="ghost" onClick={() => { cancelPolling(); onClose() }}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  )
}
