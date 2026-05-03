import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import { useApiQuery } from '@/hooks/useApi'

interface ServiceItem { name: string; status: string; latency_ms?: number }
interface HealthData {
  status: string
  services: ServiceItem[]
  uptime_seconds?: number
}
interface OverviewData {
  providers_count?: number
  uptime?: string
  version?: string
}

function badgeVariant(status: string): 'ok' | 'err' | 'warn' {
  if (status === 'ok') return 'ok'
  if (status === 'error') return 'err'
  return 'warn'
}

export default function HealthPanel() {
  const { data, isLoading, error } = useApiQuery<HealthData>(['health'], '/api/health', { refetchInterval: 5000 })
  const { data: overview } = useApiQuery<OverviewData>(['overview'], '/api/overview')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const services = data?.services ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '12px' }}>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>SYSTEM STATUS</div>
          <Badge variant={badgeVariant(data?.status ?? 'warn')}>{data?.status ?? '—'}</Badge>
        </Card>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>UPTIME</div>
          <div style={{ fontSize: '15px', fontWeight: 600 }}>{overview?.uptime ?? data?.uptime_seconds != null ? `${Math.floor((data?.uptime_seconds ?? 0) / 60)}m` : '—'}</div>
        </Card>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>PROVIDERS</div>
          <div style={{ fontSize: '15px', fontWeight: 600 }}>{overview?.providers_count ?? '—'}</div>
        </Card>
        <Card>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>VERSION</div>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>{overview?.version ?? '—'}</div>
        </Card>
      </div>

      <Card title="Services">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {services.map((svc: any, i: any) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '8px 12px', background: 'var(--surface-2)', borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}>
              <span style={{ fontSize: '13px' }}>{svc.name}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {svc.latency_ms != null && (
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{svc.latency_ms}ms</span>
                )}
                <Badge variant={badgeVariant(svc.status)}>{svc.status}</Badge>
              </div>
            </div>
          ))}
          {services.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No services reported</div>}
        </div>
      </Card>
    </div>
  )
}
