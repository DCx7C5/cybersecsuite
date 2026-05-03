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

interface Workflow { id: string; name: string; status: string; steps_count?: number; created_at: string }
interface WorkflowsData { workflows?: Workflow[] }

export default function WorkflowsPanel() {
  const { data, isLoading, error } = useApiQuery<WorkflowsData>(['workflows'], '/api/workflows')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', steps: '' })
  const qc = RQ.useQueryClient()

  const createMut = RQ.useMutation({
    mutationFn: () => fetchApi('/api/workflows', { method: 'POST', body: JSON.stringify({ name: form.name, steps: form.steps }) }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['workflows'] }); setShowModal(false) }
  })

  const cancelMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi(`/api/workflows/${id}/cancel`, { method: 'POST' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['workflows'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const workflows = data?.workflows ?? []

  const columns: ColumnDef<Workflow>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'done' ? 'ok' : v === 'running' ? 'info' : v === 'error' ? 'err' : 'muted'}>{v}</Badge>
    }},
    { accessorKey: 'steps_count', header: 'Steps' },
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      row.original.status === 'running'
        ? <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => cancelMut.mutate(row.original.id)}>Cancel</Button>
        : null
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Workflows" actions={<Button onClick={() => setShowModal(true)}>+ New Workflow</Button>}>
        <Table data={workflows} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title="New Workflow">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Steps (JSON)</label>
            <textarea
              value={form.steps}
              onChange={e => setForm(f => ({ ...f, steps: e.target.value }))}
              style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '80px', outline: 'none', resize: 'vertical' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => createMut.mutate()} disabled={createMut.isPending}>Create</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
