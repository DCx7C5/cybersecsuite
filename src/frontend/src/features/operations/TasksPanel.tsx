import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface Task { task_id: string; type: string; status: string; progress?: number; created_at: string }
interface TasksData { tasks?: Task[] }

export default function TasksPanel() {
  const { data, isLoading, error } = useApiQuery<TasksData>(['tasks'], '/api/tasks-list')
  const qc = useQueryClient()

  const cancelMut = useMutation({
    mutationFn: (id: string) => fetchApi(`/api/tasks/${id}/cancel`, { method: 'POST' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['tasks'] }) }
  })

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const tasks = data?.tasks ?? []

  const columns: ColumnDef<Task>[] = [
    { accessorKey: 'task_id', header: 'Task ID' },
    { accessorKey: 'type', header: 'Type' },
    { accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const v = getValue<string>()
      return <Badge variant={v === 'done' ? 'ok' : v === 'running' ? 'info' : v === 'error' ? 'err' : 'muted'}>{v}</Badge>
    }},
    { accessorKey: 'progress', header: 'Progress', cell: ({ getValue }) => {
      const v = getValue<number | undefined>()
      return v != null ? `${v}%` : '—'
    }},
    { accessorKey: 'created_at', header: 'Created' },
    { id: 'actions', header: 'Actions', cell: ({ row }) => (
      row.original.status === 'running'
        ? <Button variant="danger" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => cancelMut.mutate(row.original.task_id)}>Cancel</Button>
        : null
    )},
  ]

  return (
    <Card title="Tasks">
      <Table data={tasks} columns={columns} />
    </Card>
  )
}
