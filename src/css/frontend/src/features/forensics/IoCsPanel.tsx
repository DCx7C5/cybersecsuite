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

interface IoC { id: string; type: string; value: string; confidence?: number; source?: string; created_at: string }
interface IoCsData { iocs?: IoC[] }

export default function IoCsPanel() {
  const { data, isLoading, error } = useApiQuery<IoCsData>(['iocs'], '/api/iocs')
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState<IoC | null>(null)
  const [form, setForm] = useState({ type: '', value: '', confidence: '80', source: '' })
  const qc = RQ.useQueryClient()

  const saveMut = RQ.useMutation({
    mutationFn: () => {
      const url = editItem ? `/api/iocs/${editItem.id}` : '/api/iocs'
      const method = editItem ? 'PATCH' : 'POST'
      return fetchApi(url, { method, body: JSON.stringify({ ...form, confidence: Number(form.confidence) }) })
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['iocs'] }); setShowModal(false); setEditItem(null) }
  })

  const deleteMut = RQ.useMutation({
    mutationFn: (id: string) => fetchApi(`/api/iocs/${id}`, { method: 'DELETE' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['iocs'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const iocs = data?.iocs ?? []

  const columns: ColumnDef<IoC>[] = [
    { accessorKey: 'type', header: 'Type' },
    { accessorKey: 'value', header: 'Value', cell: ({ getValue }) =>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{getValue<string>()}</span>
    },
    { accessorKey: 'confidence', header: 'Confidence', cell: ({ getValue }) => {
      const v = getValue<number | undefined>()
      return v != null ? `${v}%` : '—'
    }},
    { accessorKey: 'source', header: 'Source' },
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      <div style={{ display: 'flex', gap: '6px' }}>
        <Button variant="ghost" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => {
          setEditItem(row.original)
          setForm({ type: row.original.type, value: row.original.value, confidence: String(row.original.confidence ?? 80), source: row.original.source ?? '' })
          setShowModal(true)
        }}>Edit</Button>
        <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => deleteMut.mutate(row.original.id)}>Del</Button>
      </div>
    )},
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="IOCs" actions={<Button onClick={() => { setEditItem(null); setForm({ type: '', value: '', confidence: '80', source: '' }); setShowModal(true) }}>+ Add IOC</Button>}>
        <Table data={iocs} columns={columns} />
      </Card>
      <Modal open={showModal} onClose={() => setShowModal(false)} title={editItem ? 'Edit IOC' : 'New IOC'}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Type" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} placeholder="ip | domain | hash | url" />
          <Input label="Value" value={form.value} onChange={e => setForm(f => ({ ...f, value: e.target.value }))} />
          <Input label="Confidence (0-100)" type="number" value={form.confidence} onChange={e => setForm(f => ({ ...f, confidence: e.target.value }))} />
          <Input label="Source" value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))} />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <Button variant="ghost" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>Save</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
