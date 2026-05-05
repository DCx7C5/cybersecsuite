import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Modal from '@/components/ui/Modal'

interface AgentTemplate { id: string; name: string; description: string }
interface TemplatesData { templates?: AgentTemplate[] }

export default function AgentFactoryPanel() {
  const { data, isLoading, error } = useApiQuery<TemplatesData>(['agent-factory'], '/api/agent-factory')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', model: '', skills: '' })
  const qc = RQ.useQueryClient()

  const createMut = RQ.useMutation({
    mutationFn: () => fetchApi('/api/agents/generate', {
      method: 'POST',
      body: JSON.stringify({ name: form.name, description: form.description, model: form.model, skills: form.skills.split(',').map(s => s.trim()).filter(Boolean) })
    }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['agent-factory'] }); setShowModal(false) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const templates = data?.templates ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Agent Factory" actions={<Button onClick={() => setShowModal(true)}>+ Generate Agent</Button>}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
          {templates.map(t => (
            <div key={t.id} style={{ padding: '12px', background: 'var(--surface-2)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '4px' }}>{t.name}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{t.description}</div>
            </div>
          ))}
          {templates.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No templates yet</div>}
        </div>
      </Card>

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Generate Agent">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <Input label="Model" value={form.model} onChange={e => setForm(f => ({ ...f, model: e.target.value }))} placeholder="claude-sonnet-4-5" />
          <Input label="Skills (comma-separated)" value={form.skills} onChange={e => setForm(f => ({ ...f, skills: e.target.value }))} />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => createMut.mutate()} disabled={createMut.isPending}>
              {createMut.isPending ? 'Generating...' : 'Generate'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
