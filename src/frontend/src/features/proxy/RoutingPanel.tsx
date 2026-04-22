import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import { useApiQuery } from '@/hooks/useApi'
import type { ColumnDef } from '@tanstack/react-table'

interface CircuitBreaker { provider: string; state: string; failure_count: number }
interface RoutingData {
  strategy?: string
  fallback_chain?: string[]
  circuit_breakers?: CircuitBreaker[]
}

export default function RoutingPanel() {
  const { data, isLoading, error } = useApiQuery<RoutingData>(['routing'], '/api/routing')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const cbs = data?.circuit_breakers ?? []
  const chain = data?.fallback_chain ?? []

  const columns: ColumnDef<CircuitBreaker>[] = [
    { accessorKey: 'provider', header: 'Provider' },
    { accessorKey: 'state', header: 'State', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'closed' ? 'ok' : v === 'open' ? 'err' : 'warn'}>{v}</Badge>
    }},
    { accessorKey: 'failure_count', header: 'Failures' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Current Strategy">
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', color: 'var(--accent)' }}>
          {data?.strategy ?? '—'}
        </div>
      </Card>

      <Card title="Fallback Chain">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {chain.map((p, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Badge variant="info">{p}</Badge>
              {i < chain.length - 1 && <span style={{ color: 'var(--text-faint)' }}>→</span>}
            </div>
          ))}
          {chain.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No fallback chain configured</span>}
        </div>
      </Card>

      <Card title="Circuit Breakers">
        <Table data={cbs} columns={columns} />
      </Card>
    </div>
  )
}
