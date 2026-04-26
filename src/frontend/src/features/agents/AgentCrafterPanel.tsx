import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Modal from '@/components/ui/Modal'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface Agent { id: string; name: string; description: string; model: string; status?: string }
interface AgentsData { agents?: Agent[] }

export default function AgentCrafterPanel() {
  const { data, isLoading, error } = useApiQuery<AgentsData>(['agents'], '/api/agents')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Agent | null>(null)
  const [form, setForm] = useState({ name: '', description: '', model: '' })
  const qc = RQ.useQueryClient()

  const saveMut = RQ.useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/agents/crud/${editItem.id}` : '/api/agents/crud'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['agents'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi(`/api/agents/crud/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['agents'] }) }
  })

  const openEdit = (agent: Agent) => {
    setEditItem(agent)
    setForm({ name: agent.name, description: agent.description, model: agent.model })
    setShowModal(true)
  }

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const agents = data?.agents ?? []

  const columns: ColumnDef<Agent>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'description', header: 'Description' },
    { accessorKey: 'model', header: 'Model' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string | undefined>()
      return v ? <Badge variant={v === 'active' ? 'ok' : 'muted'}>{v}</Badge> : null
    }},
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => openEdit(row.original)}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Agent Crafter" actions={
        <Button onClick={() => { setEditItem(null); setForm({ name: '', description: '', model: '' }); setShowModal(true) }}>
          + New Agent
        </Button>
      }>
        <Table data={agents} columns={columns} />
      </Card>

      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit Agent' : 'New Agent'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <Input label="Model" value={form.model} onChange={e => setForm(f => ({ ...f, model: e.target.value }))} />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>Save</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
