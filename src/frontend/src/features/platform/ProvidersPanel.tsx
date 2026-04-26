import { useState } from 'react'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import { useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import ProviderAuthModal from '@/features/platform/ProviderAuthModal'
import { resolveProviderAuthConfig } from '@/config/providerAuthMethods'

interface ProviderAccount {
  account_id?: string
  vault_key: string
  label?: string | null
  auth_method?: string | null
  email?: string | null
  display_name?: string | null
  active?: boolean
  test_status?: string | null
}

interface ProviderAuthMethodEntry {
  auth_method: string
  config?: Record<string, unknown>
}

interface Provider {
  id: string
  name: string
  enabled?: boolean
  status: string
  auth_type: string
  models_count?: number
  auth_methods?: ProviderAuthMethodEntry[]
  accounts?: ProviderAccount[]
}

interface ProvidersData {
  providers?: Provider[]
}

type ProvidersHubResponse = ProvidersData | Provider[]

function normalizeProviders(data: ProvidersHubResponse | undefined): Provider[] {
  if (!data) return []
  if (Array.isArray(data)) return data
  return data.providers ?? []
}

function statusVariant(status: string): 'ok' | 'warn' | 'err' {
  if (status === 'available' || status === 'free_tier') return 'ok'
  if (status === 'disabled' || status === 'error') return 'err'
  return 'warn'
}

export default function ProvidersPanel() {
  const { data, isLoading, error } = useApiQuery<ProvidersHubResponse>(['providers-hub'], '/api/providers/hub')
  const qc = useQueryClient()
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null)
  const [defaultMethod, setDefaultMethod] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const [revokingAccountId, setRevokingAccountId] = useState<string | null>(null)

  const toggle = async (id: string, enabled: boolean) => {
    setLocalError(null)
    try {
      await fetchApi(`/api/providers/${id}`, { method: 'PATCH', body: JSON.stringify({ enabled: !enabled }) })
      await qc.invalidateQueries({ queryKey: ['providers-hub'] })
    } catch (err) {
      setLocalError(String(err))
    }
  }

  const openAuthModal = (provider: Provider) => {
    const resolved = resolveProviderAuthConfig(
      provider.id,
      (provider.auth_methods ?? []).map((method) => method.auth_method),
      provider.auth_type
    )
    const actionable = resolved.supported.filter((method) => method !== 'none')
    if (actionable.length === 0) {
      return
    }
    setSelectedProvider(provider)
    setDefaultMethod(actionable[0])
    setShowAuthModal(true)
    setLocalError(null)
  }

  const revokeAccount = async (providerId: string, accountId: string) => {
    setLocalError(null)
    setRevokingAccountId(accountId)
    try {
      await fetchApi(`/api/providers/${providerId}/auth/revoke`, {
        method: 'POST',
        body: JSON.stringify({ account_id: accountId }),
      })
      await qc.invalidateQueries({ queryKey: ['providers-hub'] })
    } catch (err) {
      setLocalError(String(err))
    } finally {
      setRevokingAccountId(null)
    }
  }

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const providers = normalizeProviders(data)

  const columns: ColumnDef<Provider>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={statusVariant(v)}>{v}</Badge>
    }},
    { accessorKey: 'models_count', header: 'Models' },
    { accessorKey: 'enabled', header: 'Enabled', cell: ({ row }) => (
      <button
        onClick={() => {
          const isEnabled = row.original.enabled ?? row.original.status !== 'disabled'
          void toggle(row.original.id, isEnabled)
        }}
        style={{
          background: (row.original.enabled ?? row.original.status !== 'disabled') ? 'var(--success-glow)' : 'var(--surface-2)',
          color: (row.original.enabled ?? row.original.status !== 'disabled') ? 'var(--success)' : 'var(--text-muted)',
          border: `1px solid ${(row.original.enabled ?? row.original.status !== 'disabled') ? 'var(--success)' : 'var(--border)'}`,
          borderRadius: 'var(--radius)',
          padding: '2px 10px',
          fontSize: '11px',
          cursor: 'pointer',
        }}
      >
        {(row.original.enabled ?? row.original.status !== 'disabled') ? 'ON' : 'OFF'}
      </button>
    )},
    { id: 'actions', header: 'Actions', cell: ({ row }) => {
      const provider = row.original
      const accounts = provider.accounts ?? []
      const resolved = resolveProviderAuthConfig(
        provider.id,
        (provider.auth_methods ?? []).map((method) => method.auth_method),
        provider.auth_type
      )
      const actionable = resolved.supported.filter((method) => method !== 'none')
      const canSignIn = provider.status !== 'disabled' && actionable.length > 0

      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', minWidth: '260px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => { if (canSignIn) openAuthModal(provider) }}
              disabled={!canSignIn}
              style={{
                background: canSignIn ? 'var(--accent-glow)' : 'var(--surface-2)',
                color: canSignIn ? 'var(--accent)' : 'var(--text-muted)',
                border: `1px solid ${canSignIn ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: 'var(--radius)',
                padding: '4px 10px',
                fontSize: '11px',
                cursor: canSignIn ? 'pointer' : 'not-allowed',
              }}
            >
              {accounts.length > 0 ? 'Add Account' : 'Sign In'}
            </button>
            {accounts.length > 0 && <Badge variant="info">{accounts.length} account{accounts.length > 1 ? 's' : ''}</Badge>}
            {!canSignIn && <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>No interactive auth</span>}
          </div>

          {accounts.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {accounts.map((account) => {
                const accountId = account.account_id ?? account.vault_key
                const label = account.email ?? account.display_name ?? account.label ?? account.vault_key
                const isRevoking = revokingAccountId === accountId
                return (
                  <div
                    key={accountId}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '8px',
                      fontSize: '11px',
                      padding: '4px 6px',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)',
                      background: 'var(--surface-2)',
                    }}
                    >
                    <span style={{ color: account.active ? 'var(--success)' : 'var(--text-primary)' }}>
                      {account.active ? 'active: ' : ''}{label}
                    </span>
                    <button
                      onClick={() => { void revokeAccount(provider.id, accountId) }}
                      disabled={isRevoking}
                      style={{
                        background: 'transparent',
                        border: '1px solid var(--red)',
                        color: 'var(--red)',
                        borderRadius: 'var(--radius)',
                        padding: '2px 6px',
                        fontSize: '10px',
                        cursor: isRevoking ? 'wait' : 'pointer',
                      }}
                    >
                      {isRevoking ? '...' : 'Revoke'}
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )
    }},
  ]

  return (
    <Card title="Provider Hub">
      {localError && (
        <div style={{
          color: 'var(--red)',
          background: 'var(--red-glow)',
          border: '1px solid var(--red)',
          borderRadius: 'var(--radius)',
          padding: '8px 10px',
          fontSize: '12px',
          marginBottom: '12px',
        }}>
          {localError}
        </div>
      )}
      <Table data={providers} columns={columns} />
      <ProviderAuthModal
        open={showAuthModal}
        provider={selectedProvider}
        defaultMethod={defaultMethod}
        onClose={() => {
          setShowAuthModal(false)
          setSelectedProvider(null)
        }}
        onSuccess={() => {
          void qc.invalidateQueries({ queryKey: ['providers-hub'] })
        }}
      />
    </Card>
  )
}
