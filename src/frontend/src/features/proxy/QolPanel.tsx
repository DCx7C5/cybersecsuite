import { useState, useEffect } from 'react'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Button from '@/components/ui/Button'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import { useQueryClient } from '@tanstack/react-query'

interface QolData {
  settings?: Record<string, boolean | string | number>
}

export default function QolPanel() {
  const { data, isLoading, error } = useApiQuery<QolData>(['qol'], '/api/qol')
  const [local, setLocal] = useState<Record<string, boolean | string | number>>({})
  const [saving, setSaving] = useState(false)
  const qc = useQueryClient()

  useEffect(() => {
    if (data?.settings) setLocal(data.settings)
  }, [data])

  const save = async () => {
    setSaving(true)
    try {
      await fetchApi('/api/qol', { method: 'POST', body: JSON.stringify(local) })
      await qc.invalidateQueries({ queryKey: ['qol'] })
    } finally {
      setSaving(false)
    }
  }

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  return (
    <Card title="QoL Controls" actions={<Button onClick={() => { void save() }} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {Object.entries(local).map(([key, val]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <label style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{key}</label>
            {typeof val === 'boolean' ? (
              <button
                onClick={() => setLocal(l => ({ ...l, [key]: !val }))}
                style={{
                  background: val ? 'var(--success-glow)' : 'var(--surface-2)',
                  color: val ? 'var(--success)' : 'var(--text-muted)',
                  border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius)',
                  padding: '2px 12px',
                  fontSize: '11px',
                  cursor: 'pointer',
                }}
              >
                {val ? 'ON' : 'OFF'}
              </button>
            ) : (
              <input
                value={String(val)}
                onChange={e => setLocal(l => ({ ...l, [key]: e.target.value }))}
                style={{
                  background: 'var(--surface-2)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  padding: '4px 8px',
                  outline: 'none',
                  width: '200px',
                }}
              />
            )}
          </div>
        ))}
        {Object.keys(local).length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No settings available</div>}
      </div>
    </Card>
  )
}
