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

interface Prompt { id: string; name: string; category?: string; content?: string }
interface PromptsData { prompts?: Prompt[] }

export default function PromptsPanel() {
  const { data, isLoading, error } = useApiQuery<PromptsData>(['prompts'], '/api/prompts-list')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<Prompt | null>(null)
  const [form, setForm] = useState({ name: '', content: '', category: '' })
  const qc = useQueryClient()

  const saveMut = useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/prompts/${editItem.id}` : '/api/prompts'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify(form) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['prompts'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => fetchApi(`/api/prompts/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['prompts'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const prompts = data?.prompts ?? []

  const columns: ColumnDef<Prompt>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'category', header: 'Category' },
    { id: 'content_preview', header: 'Preview', cell: ({ row }) =>
      <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
        {(row.original.content ?? '').slice(0, 60)}{(row.original.content ?? '').length > 60 ? '…' : ''}
      </span>
    },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ name: row.original.name, content: row.original.content ?? '', category: row.original.category ?? '' })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Prompts" actions={
        <Button onClick={() => { setEditItem(null); setForm({ name: '', content: '', category: '' }); setShowModal(true) }}>+ New Prompt</Button>
      }>
        <Table data={prompts} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit Prompt' : 'New Prompt'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Category" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Content</label>
            <textarea
              value={form.content}
              onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
              style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: '13px', padding: '8px', minHeight: '120px', outline: 'none', resize: 'vertical' }}
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
