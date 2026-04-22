import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import { useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'

interface Provider { id: string; name: string; enabled: boolean; status: string; models_count?: number }
interface ProvidersData { providers?: Provider[] }

export default function ProvidersPanel() {
  const { data, isLoading, error } = useApiQuery<ProvidersData>(['providers-hub'], '/api/providers/hub')
  const qc = useQueryClient()

  const toggle = async (id: string, enabled: boolean) => {
    await fetchApi(`/api/providers/${id}`, { method: 'PATCH', body: JSON.stringify({ enabled: !enabled }) })
    await qc.invalidateQueries({ queryKey: ['providers-hub'] })
  }

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const providers = data?.providers ?? []

  const columns: ColumnDef<Provider>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'ok' ? 'ok' : v === 'error' ? 'err' : 'warn'}>{v}</Badge>
    }},
    { accessorKey: 'models_count', header: 'Models' },
    { accessorKey: 'enabled', header: 'Enabled', cell: ({ row }) => (
      <button
        onClick={() => { void toggle(row.original.id, row.original.enabled) }}
        style={{
          background: row.original.enabled ? 'var(--success-glow)' : 'var(--surface-2)',
          color: row.original.enabled ? 'var(--success)' : 'var(--text-muted)',
          border: `1px solid ${row.original.enabled ? 'var(--success)' : 'var(--border)'}`,
          borderRadius: 'var(--radius)',
          padding: '2px 10px',
          fontSize: '11px',
          cursor: 'pointer',
        }}
      >
        {row.original.enabled ? 'ON' : 'OFF'}
      </button>
    )},
  ]

  return (
    <Card title="Provider Hub">
      <Table data={providers} columns={columns} />
    </Card>
  )
}
