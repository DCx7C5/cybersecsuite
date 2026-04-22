import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Modal from '@/components/ui/Modal'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface Finding { id: string; title: string; severity: string; status: string; created_at: string; description?: string }
interface FindingsData { findings?: Finding[] }

function sevBadge(s: string): 'err' | 'warn' | 'info' | 'muted' {
  if (s === 'critical') return 'err'
  if (s === 'high') return 'warn'
  if (s === 'medium') return 'info'
  return 'muted'
}

export default function FindingsPanel() {
  const { data, isLoading, error } = useApiQuery<FindingsData>(['findings'], '/api/findings')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Finding | null>(null)
  const [form, setForm] = useState({ title: '', description: '', severity: 'medium', status: 'open' })
  const qc = useQueryClient()

  const saveMut = useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/findings/${editItem.id}` : '/api/findings'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['findings'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => fetchApi(`/api/findings/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['findings'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const findings = data?.findings ?? []

  const columns: ColumnDef<Finding>[] = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'title', header: 'Title' },
    { accessorKey: 'severity', header: 'Severity', cell: ({ getValue }) => <Badge variant={sevBadge(getValue<string>())}>{getValue<string>()}</Badge> },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => <Badge variant="muted">{getValue<string>()}</Badge> },
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ title: row.original.title, description: row.original.description ?? '', severity: row.original.severity, status: row.original.status })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Findings" actions={<Button onClick={() => { setEditItem(null); setForm({ title: '', description: '', severity: 'medium', status: 'open' }); setShowModal(true) }}>+ New Finding</Button>}>
        <Table data={findings} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit Finding' : 'New Finding'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Severity</label>
              <select value={form.severity} onChange={e => setForm(f => ({ ...f, severity: e.target.value }))} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '7px 10px', fontSize: '13px' }}>
                <option>critical</option><option>high</option><option>medium</option><option>low</option>
              </select>
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Status</label>
              <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '7px 10px', fontSize: '13px' }}>
                <option>open</option><option>closed</option><option>false_positive</option><option>accepted</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>Save</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
