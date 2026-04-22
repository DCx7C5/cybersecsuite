import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'
import { fetchApi } from '@/hooks/useApi'

const TABS = ['Standard', 'Streaming', 'Thinking', 'Memory', 'Structured'] as const
type Tab = typeof TABS[number]

const TAB_PARAMS: Record<Tab, Record<string, boolean | string>> = {
  Standard:   { stream: false },
  Streaming:  { stream: true },
  Thinking:   { stream: false, thinking: true },
  Memory:     { stream: false, use_memory: true },
  Structured: { stream: false, structured: true },
}

export default function SdkLabPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('Standard')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<unknown>(null)
  const [err, setErr] = useState<string | null>(null)

  const run = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setErr(null)
    setResult(null)
    try {
      const res = await fetchApi<unknown>('/api/agent-query', {
        method: 'POST',
        body: JSON.stringify({ prompt, ...TAB_PARAMS[activeTab] })
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
      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            style={{
              padding: '6px 14px',
              background: activeTab === t ? 'var(--accent-glow)' : 'transparent',
              border: 'none',
              borderBottom: activeTab === t ? '2px solid var(--accent)' : '2px solid transparent',
              color: activeTab === t ? 'var(--accent)' : 'var(--text-muted)',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >{t}</button>
        ))}
      </div>
      <Card title={`SDK Lab — ${activeTab}`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Prompt</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '80px', outline: 'none', resize: 'vertical' }}
            />
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', fontFamily: 'var(--font-mono)' }}>
            Params: {JSON.stringify(TAB_PARAMS[activeTab])}
          </div>
          <Button onClick={() => { void run() }} disabled={loading || !prompt.trim()}>
            {loading ? <Spinner size={14} /> : 'Run'}
          </Button>
        </div>
      </Card>
      {err && <div style={{ color: 'var(--red)', padding: '12px', background: 'var(--red-glow)', borderRadius: 'var(--radius)' }}>{err}</div>}
      {result != null && (
        <Card title="Result">
          <pre style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
