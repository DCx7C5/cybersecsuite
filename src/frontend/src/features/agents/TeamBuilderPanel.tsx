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

interface Team { id: string; name: string; description: string; agent_count?: number; status?: string }
interface TeamsData { teams?: Team[] }

export default function TeamBuilderPanel() {
  const { data, isLoading, error } = useApiQuery<TeamsData>(['teams'], '/api/teams')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Team | null>(null)
  const [form, setForm] = useState({ name: '', description: '' })
  const qc = RQ.useQueryClient()

  const saveMut = RQ.useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/teams/${editItem.id}` : '/api/teams'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['teams'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi(`/api/teams/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['teams'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const teams = data?.teams ?? []

  const columns: ColumnDef<Team>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'description', header: 'Description' },
    { accessorKey: 'agent_count', header: 'Agents' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string | undefined>()
      return v ? <Badge variant={v === 'active' ? 'ok' : 'muted'}>{v}</Badge> : null
    }},
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ name: row.original.name, description: row.original.description })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Team Builder" actions={
        <Button onClick={() => { setEditItem(null); setForm({ name: '', description: '' }); setShowModal(true) }}>+ New Team</Button>
      }>
        <Table data={teams} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit Team' : 'New Team'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>Save</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
