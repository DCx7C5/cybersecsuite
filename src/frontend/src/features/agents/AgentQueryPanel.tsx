import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import { fetchApi } from '@/hooks/useApi'

export default function AgentQueryPanel() {
  const [prompt, setPrompt] = useState('')
  const [agentName, setAgentName] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<unknown>(null)
  const [err, setErr] = useState<string | null>(null)

  const run = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setErr(null)
    try {
      const res = await fetchApi<unknown>('/api/agent-query', {
        method: 'POST',
        body: JSON.stringify({ prompt, agent_name: agentName || undefined, stream: false })
      })
      setResult(res)
    } catch (e) {
      setErr(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Agent Query">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Agent Name (optional)" value={agentName} onChange={e => setAgentName(e.target.value)} placeholder="Leave blank for default" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Prompt</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              style={{
                background: 'var(--surface-2)', border: '1px solid var(--border)',
                borderRadius: 'var(--radius)', color: 'var(--text-primary)',
                fontSize: '13px', padding: '8px', resize: 'vertical', minHeight: '80px', outline: 'none',
              }}
            />
          </div>
          <Button onClick={() => { void run() }} disabled={loading || !prompt.trim()}>
            {loading ? <Spinner size={14} /> : 'Run Query'}
          </Button>
        </div>
      </Card>
      {err && <div style={{ color: 'var(--red)', padding: '12px', background: 'var(--red-glow)', borderRadius: 'var(--radius)' }}>{err}</div>}
      {result != null && (
        <Card title="Response">
          <pre style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
