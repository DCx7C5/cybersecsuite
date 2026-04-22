import { useState } from 'react'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'

interface GraphAgent { id: string; name: string; description?: string; type?: string }
interface FlowgraphData { agents?: GraphAgent[] }

export default function FlowgraphPanel() {
  const { data, isLoading, error } = useApiQuery<FlowgraphData>(['flowgraph'], '/api/flowgraph/agents')
  const [selected, setSelected] = useState<string>('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const execute = async () => {
    if (!selected) return
    setRunning(true)
    try {
      const res = await fetchApi<{ output?: string }>('/api/flowgraph/execute', {
        method: 'POST',
        body: JSON.stringify({ agent: selected })
      })
      setResult(res.output ?? JSON.stringify(res))
    } catch (e) {
      setResult(`Error: ${String(e)}`)
    } finally {
      setRunning(false)
    }
  }

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const agents = data?.agents ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Flowgraph" actions={
        <Button onClick={() => { void execute() }} disabled={!selected || running}>
          {running ? <Spinner size={14} /> : 'Execute'}
        </Button>
      }>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
          {agents.map(a => (
            <button
              key={a.id}
              onClick={() => setSelected(a.id)}
              style={{
                padding: '12px',
                background: selected === a.id ? 'var(--accent-glow)' : 'var(--surface-2)',
                border: `1px solid ${selected === a.id ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                textAlign: 'left',
                color: 'var(--text-primary)',
              }}
            >
              <div style={{ fontWeight: 600, fontSize: '13px' }}>{a.name}</div>
              {a.type && <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>{a.type}</div>}
              {a.description && <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>{a.description}</div>}
            </button>
          ))}
          {agents.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No agents available</div>}
        </div>
      </Card>
      {result && (
        <Card title="Execution Result">
          <pre style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', whiteSpace: 'pre-wrap', color: 'var(--text-primary)' }}>{result}</pre>
        </Card>
      )}
    </div>
  )
}
