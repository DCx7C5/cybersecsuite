import { useState, useEffect, useCallback, useMemo } from 'react'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import * as RQ from '@tanstack/react-query'

const TABS = ['API', 'MCPs', 'Skills', 'Hooks'] as const
type Tab = typeof TABS[number]

interface ApiSettings { api_key?: string; model?: string; max_tokens?: number; system_prompt?: string }
interface McpSettings { mcps?: Record<string, boolean> }
interface SkillSettings { skills?: Record<string, boolean> }
interface HookSettings { hooks?: string[] }

function ApiTab() {
  const { data, isLoading } = useApiQuery<ApiSettings>(['settings-api'], '/api/settings')
  const [form, setForm] = useState<ApiSettings>(() => data ?? {})
  const [isDirty, setIsDirty] = useState(false)
  const qc = RQ.useQueryClient()
  useEffect(() => { if (data) setForm(data) }, [data])
  
  const save = useCallback(async () => {
    try {
      await fetchApi('/api/settings', { method: 'PATCH', body: JSON.stringify(form) })
      await qc.invalidateQueries({ queryKey: ['settings-api'] })
      setIsDirty(false)
    } catch (e) {
      console.error('Failed to save API settings:', e)
    }
  }, [form, qc])

  const handleChange = useCallback((key: keyof ApiSettings, value: any) => {
    setForm(f => ({ ...f, [key]: value }))
    setIsDirty(true)
  }, [])

  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Input 
        label="API Key" 
        type="password" 
        value={form.api_key ?? ''} 
        onChange={e => handleChange('api_key', e.target.value)}
        data-testid="settings-api-key"
      />
      <Input 
        label="Model" 
        value={form.model ?? ''} 
        onChange={e => handleChange('model', e.target.value)}
        data-testid="settings-model"
      />
      <Input 
        label="Max Tokens" 
        type="number" 
        value={String(form.max_tokens ?? '')} 
        onChange={e => handleChange('max_tokens', Number(e.target.value))}
        data-testid="settings-max-tokens"
      />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>System Prompt</label>
        <textarea 
          value={form.system_prompt ?? ''} 
          onChange={e => handleChange('system_prompt', e.target.value)}
          data-testid="settings-system-prompt"
          style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '80px', outline: 'none', resize: 'vertical' }} 
        />
      </div>
      <Button 
        onClick={() => { void save() }} 
        style={{ alignSelf: 'flex-start' }}
        data-testid="settings-api-save"
        disabled={!isDirty}
      >
        Save
      </Button>
    </div>
  )
}

function McpTab() {
  const { data, isLoading } = useApiQuery<McpSettings>(['settings-mcps'], '/api/settings/mcps')
  const [local, setLocal] = useState<Record<string, boolean>>(() => data?.mcps ?? {})
  const [search, setSearch] = useState('')
  const qc = RQ.useQueryClient()

  useEffect(() => { if (data?.mcps) setLocal(data.mcps) }, [data?.mcps])

  const filtered = useMemo(() => {
    if (!search) return Object.entries(local)
    return Object.entries(local).filter(([key]) => key.toLowerCase().includes(search.toLowerCase()))
  }, [local, search])

  const save = useCallback(async () => {
    try {
      await fetchApi('/api/settings/mcps', { method: 'PATCH', body: JSON.stringify({ mcps: local }) })
      await qc.invalidateQueries({ queryKey: ['settings-mcps'] })
    } catch (e) {
      console.error('Failed to save MCP settings:', e)
    }
  }, [local, qc])

  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Input 
        placeholder="Search MCPs..." 
        value={search} 
        onChange={e => setSearch(e.target.value)}
        data-testid="mcps-search"
      />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflowY: 'auto' }}>
        {filtered.map(([key, val]) => (
          <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px', background: 'var(--surface-2)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
            <span style={{ fontSize: '13px' }} data-testid={`mcp-item-${key}`}>{key}</span>
            <button 
              onClick={() => setLocal(l => ({ ...l, [key]: !val }))} 
              style={{ background: val ? 'var(--success-glow)' : 'var(--surface-2)', color: val ? 'var(--success)' : 'var(--text-muted)', border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`, borderRadius: 'var(--radius)', padding: '4px 12px', fontSize: '11px', cursor: 'pointer', transition: 'all 0.15s' }}
              data-testid={`mcp-toggle-${key}`}
            >
              {val ? 'ON' : 'OFF'}
            </button>
          </div>
        ))}
        {filtered.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '16px' }}>
          {search ? 'No MCPs match search' : 'No MCPs configured'}
        </div>}
      </div>
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }} data-testid="mcps-save">Save</Button>
    </div>
  )
}

function SkillsTab() {
  const { data, isLoading } = useApiQuery<SkillSettings>(['settings-skills'], '/api/settings/skills')
  const [local, setLocal] = useState<Record<string, boolean>>(() => data?.skills ?? {})
  const [search, setSearch] = useState('')
  const qc = RQ.useQueryClient()

  useEffect(() => { if (data?.skills) setLocal(data.skills) }, [data?.skills])

  const filtered = useMemo(() => {
    if (!search) return Object.entries(local)
    return Object.entries(local).filter(([key]) => key.toLowerCase().includes(search.toLowerCase()))
  }, [local, search])

  const save = useCallback(async () => {
    try {
      await fetchApi('/api/settings/skills', { method: 'PATCH', body: JSON.stringify({ skills: local }) })
      await qc.invalidateQueries({ queryKey: ['settings-skills'] })
    } catch (e) {
      console.error('Failed to save skill settings:', e)
    }
  }, [local, qc])

  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Input 
        placeholder="Search skills..." 
        value={search} 
        onChange={e => setSearch(e.target.value)}
        data-testid="skills-search"
      />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflowY: 'auto' }}>
        {filtered.map(([key, val]) => (
          <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px', background: 'var(--surface-2)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
            <span style={{ fontSize: '13px' }} data-testid={`skill-item-${key}`}>{key}</span>
            <button 
              onClick={() => setLocal(l => ({ ...l, [key]: !val }))} 
              style={{ background: val ? 'var(--success-glow)' : 'var(--surface-2)', color: val ? 'var(--success)' : 'var(--text-muted)', border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`, borderRadius: 'var(--radius)', padding: '4px 12px', fontSize: '11px', cursor: 'pointer', transition: 'all 0.15s' }}
              data-testid={`skill-toggle-${key}`}
            >
              {val ? 'ON' : 'OFF'}
            </button>
          </div>
        ))}
        {filtered.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '16px' }}>
          {search ? 'No skills match search' : 'No skill domains configured'}
        </div>}
      </div>
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }} data-testid="skills-save">Save</Button>
    </div>
  )
}

function HooksTab() {
  const { data, isLoading } = useApiQuery<HookSettings>(['settings-hooks'], '/api/settings/hooks')
  const [hooks, setHooks] = useState<string[]>(() => data?.hooks ?? [])
  const [newHook, setNewHook] = useState('')
  const [search, setSearch] = useState('')
  const qc = RQ.useQueryClient()

  useEffect(() => { if (data?.hooks) setHooks(data.hooks) }, [data?.hooks])

  const filtered = useMemo(() => {
    if (!search) return hooks
    return hooks.filter(h => h.toLowerCase().includes(search.toLowerCase()))
  }, [hooks, search])

  const save = useCallback(async () => {
    try {
      await fetchApi('/api/settings/hooks', { method: 'PATCH', body: JSON.stringify({ hooks }) })
      await qc.invalidateQueries({ queryKey: ['settings-hooks'] })
    } catch (e) {
      console.error('Failed to save hook settings:', e)
    }
  }, [hooks, qc])

  const addHook = useCallback(() => {
    if (newHook.trim() && !hooks.includes(newHook.trim())) {
      setHooks(hs => [...hs, newHook.trim()])
      setNewHook('')
    }
  }, [newHook, hooks])

  if (isLoading) return <Spinner />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Input 
        placeholder="Search hooks..." 
        value={search} 
        onChange={e => setSearch(e.target.value)}
        data-testid="hooks-search"
      />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '300px', overflowY: 'auto' }}>
        {filtered.map((h, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px', background: 'var(--surface-2)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
            <span style={{ flex: 1, fontFamily: 'var(--font-mono)', fontSize: '12px' }} data-testid={`hook-item-${i}`}>{h}</span>
            <Button 
              variant="danger" 
              style={{ fontSize: '11px', padding: '2px 8px' }} 
              onClick={() => setHooks(hs => hs.filter((_, j) => j !== hooks.indexOf(h)))}
              data-testid={`hook-remove-${i}`}
            >
              ✕
            </Button>
          </div>
        ))}
        {filtered.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '16px' }}>
          {search ? 'No hooks match search' : 'No hooks configured'}
        </div>}
      </div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <Input 
          value={newHook} 
          onChange={e => setNewHook(e.target.value)}
          placeholder="Hook URL or command" 
          style={{ flex: 1 }}
          data-testid="hook-input"
          onKeyPress={e => e.key === 'Enter' && addHook()}
        />
        <Button 
          variant="secondary" 
          onClick={addHook}
          data-testid="hook-add"
        >
          Add
        </Button>
      </div>
      <Button onClick={() => { void save() }} style={{ alignSelf: 'flex-start' }} data-testid="hooks-save">Save</Button>
    </div>
  )
}

export default function SettingsPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('API')

  useKeyboardShortcuts([
    {
      key: '1',
      alt: true,
      handler: () => setActiveTab('API'),
      description: 'Switch to API tab',
    },
    {
      key: '2',
      alt: true,
      handler: () => setActiveTab('MCPs'),
      description: 'Switch to MCPs tab',
    },
    {
      key: '3',
      alt: true,
      handler: () => setActiveTab('Skills'),
      description: 'Switch to Skills tab',
    },
    {
      key: '4',
      alt: true,
      handler: () => setActiveTab('Hooks'),
      description: 'Switch to Hooks tab',
    },
  ])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--border)', paddingBottom: '8px', overflow: 'auto' }}>
        {TABS.map((t, idx) => (
          <button 
            key={t} 
            onClick={() => setActiveTab(t)} 
            title={`Alt+${idx + 1}`}
            data-testid={`settings-tab-${t}`}
            style={{
              padding: '6px 14px', 
              background: activeTab === t ? 'var(--accent-glow)' : 'transparent',
              border: 'none', 
              borderBottom: activeTab === t ? '2px solid var(--accent)' : '2px solid transparent',
              color: activeTab === t ? 'var(--accent)' : 'var(--text-muted)', 
              fontSize: '13px', 
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s',
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <Card title={`Configuration — ${activeTab}`}>
        {activeTab === 'API' && <ApiTab />}
        {activeTab === 'MCPs' && <McpTab />}
        {activeTab === 'Skills' && <SkillsTab />}
        {activeTab === 'Hooks' && <HooksTab />}
      </Card>
    </div>
  )
}

