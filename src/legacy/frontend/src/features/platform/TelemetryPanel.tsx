import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Table from '@/components/ui/Table'
import { useApiQuery } from '@/hooks/useApi'
import type { ColumnDef } from '@tanstack/react-table'

interface MetricRow { name: string; value: number; unit: string }
interface TelemetryData {
  p50_ms?: number
  p95_ms?: number
  p99_ms?: number
  total_requests?: number
  error_rate?: number
  metrics?: MetricRow[]
}

export default function TelemetryPanel() {
  const { data, isLoading, error } = useApiQuery<TelemetryData>(['telemetry'], '/api/telemetry', { refetchInterval: 3000 })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const metrics = data?.metrics ?? []

  const columns: ColumnDef<MetricRow>[] = [
    { accessorKey: 'name', header: 'Metric' },
    { accessorKey: 'value', header: 'Value' },
    { accessorKey: 'unit', header: 'Unit' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '12px' }}>
        {[
          { label: 'P50', value: data?.p50_ms != null ? `${data.p50_ms}ms` : '—' },
          { label: 'P95', value: data?.p95_ms != null ? `${data.p95_ms}ms` : '—' },
          { label: 'P99', value: data?.p99_ms != null ? `${data.p99_ms}ms` : '—' },
          { label: 'REQUESTS', value: data?.total_requests ?? '—' },
          { label: 'ERROR RATE', value: data?.error_rate != null ? `${(data.error_rate * 100).toFixed(2)}%` : '—' },
        ].map(stat => (
          <Card key={stat.label}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>{stat.label}</div>
            <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{String(stat.value)}</div>
          </Card>
        ))}
      </div>
      {metrics.length > 0 && (
        <Card title="Metrics">
          <Table data={metrics} columns={columns} />
        </Card>
      )}
    </div>
  )
}
