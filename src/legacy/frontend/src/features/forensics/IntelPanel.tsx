import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Modal from '@/components/ui/Modal'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface IntelItem { id: string; title?: string; type?: string; source?: string; created_at?: string }
interface IntelData { items?: IntelItem[] }
interface IntelSource { id: string; name: string; url?: string; type?: string }
interface SourcesData { sources?: IntelSource[] }

export default function IntelPanel() {
  const { data: intelData, isLoading } = useApiQuery<IntelData>(['intelligence'], '/api/intelligence')
  const { data: sourcesData } = useApiQuery<SourcesData>(['intel-sources'], '/api/intel-sources')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', url: '', type: '' })
  const qc = RQ.useQueryClient()

  const addSourceMut = RQ.useMutation({
    mutationFn: () => fetchApi('/api/intel-sources', { method: 'POST', body: JSON.stringify(form) }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['intel-sources'] }); setShowModal(false) }
  })

  const deleteSourceMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi(`/api/intel-sources/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['intel-sources'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>

  const items = intelData?.items ?? []
  const sources = sourcesData?.sources ?? []

  const intelColumns: ColumnDef<IntelItem>[] = [
    { accessorKey: 'title', header: 'Title' },
    { accessorKey: 'type', header: 'Type' },
    { accessorKey: 'source', header: 'Source' },
    { accessorKey: 'created_at', header: 'Date' },
  ]

  const sourceColumns: ColumnDef<IntelSource>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'url', header: 'URL' },
    { accessorKey: 'type', header: 'Type' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteSourceMut.mutate(row.original.id)}>Del</Button>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Intel Feed">
        <Table data={items} columns={intelColumns} />
      </Card>
      <Card title="Sources" actions={<Button onClick={() => { setForm({ name: '', url: '', type: '' }); setShowModal(true) }}>+ Add Source</Button>}>
        <Table data={sources} columns={sourceColumns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add Intel Source">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="URL" value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} />
          <Input label="Type" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => addSourceMut.mutate()} disabled={addSourceMut.isPending}>Add</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
