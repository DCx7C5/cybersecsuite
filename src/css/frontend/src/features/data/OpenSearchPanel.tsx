import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'

interface OpenSearchData {
  status?: string
  index_count?: number
  doc_count?: number
  storage_size?: string
  cluster_name?: string
}

export default function OpenSearchPanel() {
  const { data, isLoading, error } = useApiQuery<OpenSearchData>(['opensearch'], '/api/opensearch')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="OpenObserve Status">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>STATUS</div>
            <Badge variant={data?.status === 'green' ? 'ok' : data?.status === 'yellow' ? 'warn' : 'err'}>{data?.status ?? '—'}</Badge>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>CLUSTER</div>
            <div style={{ fontSize: '13px' }}>{data?.cluster_name ?? '—'}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>INDICES</div>
            <div style={{ fontSize: '20px', fontWeight: 700 }}>{data?.index_count ?? '—'}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>DOCUMENTS</div>
            <div style={{ fontSize: '20px', fontWeight: 700 }}>{data?.doc_count?.toLocaleString() ?? '—'}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>STORAGE</div>
            <div style={{ fontSize: '16px', fontWeight: 600 }}>{data?.storage_size ?? '—'}</div>
          </div>
        </div>
      </Card>
    </div>
  )
}
