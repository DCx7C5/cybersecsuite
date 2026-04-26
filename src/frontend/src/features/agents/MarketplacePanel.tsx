import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'

interface MarketItem { id: string; name: string; description?: string; type?: string; installed?: boolean }
interface MarketData { items?: MarketItem[] }

export default function MarketplacePanel() {
  const [tab, setTab] = useState<'all' | 'installed'>('all')
  const { data: allData, isLoading: allLoading } = useApiQuery<MarketData>(['marketplace'], '/api/marketplace')
  const { data: instData, isLoading: instLoading } = useApiQuery<MarketData>(['marketplace-installed'], '/api/marketplace/installed', { enabled: tab === 'installed' })
  const qc = RQ.useQueryClient()

  const installMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi('/api/marketplace/install', { method: 'POST', body: JSON.stringify({ id }) }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['marketplace'] }); void qc.invalidateQueries({ queryKey: ['marketplace-installed'] }) }
  })

  const items = tab === 'all' ? (allData?.items ?? []) : (instData?.items ?? [])
  const loading = tab === 'all' ? allLoading : instLoading

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', gap: '4px' }}>
        {(['all', 'installed'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '6px 14px', background: tab === t ? 'var(--accent-glow)' : 'transparent',
            border: 'none', borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent',
            color: tab === t ? 'var(--accent)' : 'var(--text-muted)', fontSize: '13px', cursor: 'pointer', textTransform: 'capitalize',
          }}>{t}</button>
        ))}
      </div>
      <Card title="Marketplace">
        {loading ? <Spinner /> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
            {items.map(item => (
              <div key={item.id} style={{ padding: '12px', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ fontWeight: 600, fontSize: '13px' }}>{item.name}</div>
                  {item.type && <Badge variant="muted">{item.type}</Badge>}
                </div>
                {item.description && <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{item.description}</div>}
                {!item.installed && (
                  <Button variant="ghost" style={{ fontSize: '11px', padding: '3px 10px', alignSelf: 'flex-start' }}
                    onClick={() => installMut.mutate(item.id)} disabled={installMut.isPending}>
                    Install
                  </Button>
                )}
                {item.installed && <Badge variant="ok">Installed</Badge>}
              </div>
            ))}
            {items.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No items</div>}
          </div>
        )}
      </Card>
    </div>
  )
}
