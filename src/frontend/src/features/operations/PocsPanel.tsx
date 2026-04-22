import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Modal from '@/components/ui/Modal'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface Poc { id: string; title: string; description?: string; type?: string; created_at: string }
interface PocsData { pocs?: Poc[] }

export default function PocsPanel() {
  const { data, isLoading, error } = useApiQuery<PocsData>(['pocs'], '/api/pocs')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Poc | null>(null)
  const [form, setForm] = useState({ title: '', description: '', type: '', content: '' })
  const qc = useQueryClient()

  const saveMut = useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/pocs/${editItem.id}` : '/api/pocs'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['pocs'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => fetchApi(`/api/pocs/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['pocs'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const pocs = data?.pocs ?? []

  const columns: ColumnDef<Poc>[] = [
    { accessorKey: 'title', header: 'Title' },
    { accessorKey: 'description', header: 'Description' },
    { accessorKey: 'type', header: 'Type' },
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ title: row.original.title, description: row.original.description ?? '', type: row.original.type ?? '', content: '' })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="PoCs" actions={<Button onClick={() => { setEditItem(null); setForm({ title: '', description: '', type: '', content: '' }); setShowModal(true) }}>+ New PoC</Button>}>
        <Table data={pocs} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit PoC' : 'New PoC'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <Input label="Type" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Content</label>
            <textarea
              value={form.content}
              onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
              style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '80px', outline: 'none', resize: 'vertical' }}
            />
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
