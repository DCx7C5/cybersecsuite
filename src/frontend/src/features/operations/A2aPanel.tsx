import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface A2aStatus { status: string; version?: string; agents_count?: number }
interface A2aTask { task_id: string; state: string; created_at: string }
interface A2aData { tasks?: A2aTask[] }

export default function A2aPanel() {
  const { data: status } = useApiQuery<A2aStatus>(['a2a-status'], '/api/a2a')
  const { data, isLoading, error } = useApiQuery<A2aData>(['a2a-tasks'], '/api/a2a/tasks')
  const [form, setForm] = useState({ task_id: '', input: '' })
  const qc = RQ.useQueryClient()

  const createMut = RQ.useMutation({
    mutationFn: () => fetchApi('/api/a2a/tasks', { method: 'POST', body: JSON.stringify(form) }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['a2a-tasks'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const tasks = data?.tasks ?? []

  const columns: ColumnDef<A2aTask>[] = [
    { accessorKey: 'task_id', header: 'Task ID' },
    { accessorKey: 'state', header: 'State', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'completed' ? 'ok' : v === 'failed' ? 'err' : 'info'}>{v}</Badge>
    }},
    { accessorKey: 'created_at', header: 'Created' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {status && (
        <Card title="A2A Status">
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <Badge variant={status.status === 'ok' ? 'ok' : 'warn'}>{status.status}</Badge>
            {status.version && <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>v{status.version}</span>}
            {status.agents_count != null && <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{status.agents_count} agents</span>}
          </div>
        </Card>
      )}
      <Card title="Create Task">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Task ID" value={form.task_id} onChange={e => setForm(f => ({ ...f, task_id: e.target.value }))} />
          <Input label="Input" value={form.input} onChange={e => setForm(f => ({ ...f, input: e.target.value }))} />
          <Button onClick={() => createMut.mutate()} disabled={createMut.isPending}>Create Task</Button>
        </div>
      </Card>
      <Card title="Tasks">
        <Table data={tasks} columns={columns} />
      </Card>
    </div>
  )
}
