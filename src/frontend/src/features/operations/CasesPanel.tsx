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

interface Case { id: string; title: string; status: string; severity: string; created_at: string; description?: string }
interface CasesData { cases?: Case[] }

function statusVariant(s: string): 'ok' | 'err' | 'warn' | 'info' | 'muted' {
  if (s === 'closed') return 'ok'
  if (s === 'open') return 'info'
  if (s === 'escalated') return 'err'
  return 'muted'
}
function sevVariant(s: string): 'err' | 'warn' | 'info' | 'muted' {
  if (s === 'critical') return 'err'
  if (s === 'high') return 'warn'
  if (s === 'medium') return 'info'
  return 'muted'
}

export default function CasesPanel() {
  const { data, isLoading, error } = useApiQuery<CasesData>(['cases'], '/api/cases')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Case | null>(null)
  const [form, setForm] = useState({ title: '', description: '', status: 'open', severity: 'medium' })
  const qc = useQueryClient()

  const saveMut = useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/cases/${editItem.id}` : '/api/cases'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['cases'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => fetchApi(`/api/cases/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['cases'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const cases = data?.cases ?? []

  const columns: ColumnDef<Case>[] = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'title', header: 'Title' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => <Badge variant={statusVariant(getValue<string>())}>{getValue<string>()}</Badge> },
    { accessorKey: 'severity', header: 'Severity', cell: ({ getValue }) => <Badge variant={sevVariant(getValue<string>())}>{getValue<string>()}</Badge> },
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ title: row.original.title, description: row.original.description ?? '', status: row.original.status, severity: row.original.severity })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Cases" actions={<Button onClick={() => { setEditItem(null); setForm({ title: '', description: '', status: 'open', severity: 'medium' }); setShowModal(true) }}>+ New Case</Button>}>
        <Table data={cases} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit Case' : 'New Case'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Status</label>
              <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '7px 10px', fontSize: '13px' }}>
                <option>open</option><option>closed</option><option>escalated</option><option>pending</option>
              </select>
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Severity</label>
              <select value={form.severity} onChange={e => setForm(f => ({ ...f, severity: e.target.value }))} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '7px 10px', fontSize: '13px' }}>
                <option>critical</option><option>high</option><option>medium</option><option>low</option>
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
