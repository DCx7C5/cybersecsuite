import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import { useApiQuery } from '@/hooks/useApi'
import type { ColumnDef } from '@tanstack/react-table'

interface UsageRow { provider: string; model: string; tokens: number; cost_usd: number; latency_ms: number; status: string; created_at: string }
interface UsageData {
  total_requests?: number
  total_tokens?: number
  total_cost_usd?: number
  recent?: UsageRow[]
}

export default function UsagePanel() {
  const { data, isLoading, error } = useApiQuery<UsageData>(['usage'], '/api/usage')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const recent = data?.recent ?? []

  const columns: ColumnDef<UsageRow>[] = [
    { accessorKey: 'provider', header: 'Provider' },
    { accessorKey: 'model', header: 'Model' },
    { accessorKey: 'tokens', header: 'Tokens' },
    { accessorKey: 'cost_usd', header: 'Cost ($)', cell: ({ getValue }) => `$${(getValue<number>()).toFixed(4)}` },
    { accessorKey: 'latency_ms', header: 'Latency', cell: ({ getValue }) => `${getValue<number>()}ms` },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'ok' ? 'ok' : 'err'}>{v}</Badge>
    }},
    { accessorKey: 'created_at', header: 'Time' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>TOTAL REQUESTS</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data?.total_requests ?? '—'}</div>
        </Card>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>TOTAL TOKENS</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data?.total_tokens?.toLocaleString() ?? '—'}</div>
        </Card>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>TOTAL COST</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>${(data?.total_cost_usd ?? 0).toFixed(4)}</div>
        </Card>
      </div>
      <Card title="Recent Usage">
        <Table data={recent} columns={columns} />
      </Card>
    </div>
  )
}
