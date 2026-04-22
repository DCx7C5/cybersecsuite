import { useState, useEffect } from 'react'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import { useQueryClient } from '@tanstack/react-query'

const TABS = ['API', 'MCPs', 'Skills', 'Hooks'] as const
type Tab = typeof TABS[number]

interface ApiSettings { api_key?: string; model?: string; max_tokens?: number; system_prompt?: string }
interface McpSettings { mcps?: Record<string, boolean> }
interface SkillSettings { skills?: Record<string, boolean> }
interface HookSettings { hooks?: string[] }

function ApiTab() {
  const { data, isLoading } = useApiQuery<ApiSettings>(['settings-api'], '/api/settings')
  const [form, setForm] = useState<ApiSettings>({})
  const qc = useQueryClient()
  useEffect(() => { if (data) setForm(data) }, [data])
  const save = async () => {
    await fetchApi('/api/settings', { method: 'PATCH', body: JSON.stringify(form) })
    await qc.invalidateQueries({ queryKey: ['settings-api'] })
  }
  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Input label="API Key" type="password" value={form.api_key ?? ''} onChange={e => setForm(f => ({ ...f, api_key: e.target.value }))} />
      <Input label="Model" value={form.model ?? ''} onChange={e => setForm(f => ({ ...f, model: e.target.value }))} />
      <Input label="Max Tokens" type="number" value={String(form.max_tokens ?? '')} onChange={e => setForm(f => ({ ...f, max_tokens: Number(e.target.value) }))} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>System Prompt</label>
        <textarea value={form.system_prompt ?? ''} onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))}
          style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '80px', outline: 'none', resize: 'vertical' }} />
      </div>
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }}>Save</Button>
    </div>
  )
}

function McpTab() {
  const { data, isLoading } = useApiQuery<McpSettings>(['settings-mcps'], '/api/settings/mcps')
  const [local, setLocal] = useState<Record<string, boolean>>({})
  const qc = useQueryClient()
  useEffect(() => { if (data?.mcps) setLocal(data.mcps) }, [data])
  const save = async () => {
    await fetchApi('/api/settings/mcps', { method: 'PATCH', body: JSON.stringify({ mcps: local }) })
    await qc.invalidateQueries({ queryKey: ['settings-mcps'] })
  }
  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {Object.entries(local).map(([key, val]) => (
        <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: '13px' }}>{key}</span>
          <button onClick={() => setLocal(l => ({ ...l, [key]: !val }))} style={{ background: val ? 'var(--success-glow)' : 'var(--surface-2)', color: val ? 'var(--success)' : 'var(--text-muted)', border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`, borderRadius: 'var(--radius)', padding: '2px 12px', fontSize: '11px', cursor: 'pointer' }}>
            {val ? 'ON' : 'OFF'}
          </button>
        </div>
      ))}
      {Object.keys(local).length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No MCPs configured</div>}
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }}>Save</Button>
    </div>
  )
}

function SkillsTab() {
  const { data, isLoading } = useApiQuery<SkillSettings>(['settings-skills'], '/api/settings/skills')
  const [local, setLocal] = useState<Record<string, boolean>>({})
  const qc = useQueryClient()
  useEffect(() => { if (data?.skills) setLocal(data.skills) }, [data])
  const save = async () => {
    await fetchApi('/api/settings/skills', { method: 'PATCH', body: JSON.stringify({ skills: local }) })
    await qc.invalidateQueries({ queryKey: ['settings-skills'] })
  }
  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {Object.entries(local).map(([key, val]) => (
        <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: '13px' }}>{key}</span>
          <button onClick={() => setLocal(l => ({ ...l, [key]: !val }))} style={{ background: val ? 'var(--success-glow)' : 'var(--surface-2)', color: val ? 'var(--success)' : 'var(--text-muted)', border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`, borderRadius: 'var(--radius)', padding: '2px 12px', fontSize: '11px', cursor: 'pointer' }}>
            {val ? 'ON' : 'OFF'}
          </button>
        </div>
      ))}
      {Object.keys(local).length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No skill domains configured</div>}
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }}>Save</Button>
    </div>
  )
}

function HooksTab() {
  const { data, isLoading } = useApiQuery<HookSettings>(['settings-hooks'], '/api/settings/hooks')
  const [hooks, setHooks] = useState<string[]>([])
  const [newHook, setNewHook] = useState('')
  const qc = useQueryClient()
  useEffect(() => { if (data?.hooks) setHooks(data.hooks) }, [data])
  const save = async () => {
    await fetchApi('/api/settings/hooks', { method: 'PATCH', body: JSON.stringify({ hooks }) })
    await qc.invalidateQueries({ queryKey: ['settings-hooks'] })
  }
  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {hooks.map((h, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 10px', background: 'var(--surface-2)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
          <span style={{ flex: 1, fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{h}</span>
          <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => setHooks(hs => hs.filter((_, j) => j !== i))}>✕</Button>
        </div>
      ))}
      {hooks.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No hooks configured</div>}
      <div style={{ display: 'flex', gap: '8px' }}>
        <Input value={newHook} onChange={e => setNewHook(e.target.value)} placeholder="Hook URL or command" style={{ flex: 1 }} />
        <Button variant="secondary" onClick={() => { if (newHook.trim()) { setHooks(hs => [...hs, newHook.trim()]); setNewHook('') } }}>Add</Button>
      </div>
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }}>Save</Button>
    </div>
  )
}

export default function SettingsPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('API')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setActiveTab(t)} style={{
            padding: '6px 14px', background: activeTab === t ? 'var(--accent-glow)' : 'transparent',
            border: 'none', borderBottom: activeTab === t ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === t ? 'var(--accent)' : 'var(--text-muted)', fontSize: '13px', cursor: 'pointer',
          }}>{t}</button>
        ))}
      </div>
      <Card title={`Claude Settings — ${activeTab}`}>
        {activeTab === 'API' && <ApiTab />}
        {activeTab === 'MCPs' && <McpTab />}
        {activeTab === 'Skills' && <SkillsTab />}
        {activeTab === 'Hooks' && <HooksTab />}
      </Card>
    </div>
  )
}
