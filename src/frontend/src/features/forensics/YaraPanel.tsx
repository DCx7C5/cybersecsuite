import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'

interface YaraRule { id: string; name: string; content?: string; description?: string }
interface YaraData { rules?: YaraRule[] }

export default function YaraPanel() {
  const { data, isLoading, error } = useApiQuery<YaraData>(['yara'], '/api/yara')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const rules = data?.rules ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title={`YARA Rules (${rules.length})`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {rules.map((rule: any) => (
            <div key={rule.id} style={{ border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
              <div style={{ background: 'var(--surface-2)', padding: '8px 12px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600, fontSize: '13px', fontFamily: 'var(--font-mono)' }}>{rule.name}</span>
                {rule.description && <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{rule.description}</span>}
              </div>
              {rule.content && (
                <pre style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--cyan)', background: 'var(--bg-deep)', margin: 0, overflowX: 'auto', maxHeight: '200px' }}>
                  {rule.content}
                </pre>
              )}
            </div>
          ))}
          {rules.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No YARA rules found</div>}
        </div>
      </Card>
    </div>
  )
}
