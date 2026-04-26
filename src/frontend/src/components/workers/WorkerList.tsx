import { useState, useMemo } from 'react'
import { useWorkers, type WorkerResponse } from '@/hooks/useWorkers.ts'
import Badge from '@/components/ui/Badge.tsx'
import Button from '@/components/ui/Button.tsx'
import Input from '@/components/ui/Input.tsx'
import Select from '@/components/ui/Select.tsx'
import Spinner from '@/components/ui/Spinner.tsx'
import Card from '@/components/ui/Card.tsx'

const STATE_COLORS: Record<string, string> = {
  queued: 'var(--blue)',
  running: 'var(--green)',
  paused: 'var(--yellow)',
  completed: 'var(--green)',
  failed: 'var(--red)',
}

export default function WorkerList({ projectId }: { projectId: number }) {
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(50)
  const [search, setSearch] = useState('')
  const [stateFilter, setStateFilter] = useState('')
  const [sort, setSort] = useState('name')
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const { data, isLoading, error } = useWorkers(projectId, {
    page,
    limit,
    search,
    state: stateFilter,
    sort,
  })

  const debouncedSearch = useMemo(() => {
    const timeout = setTimeout(() => setSearch(search), 200)
    return () => clearTimeout(timeout)
  }, [search])

  const workers = data?.data || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / limit)

  const handleSelectAll = () => {
    if (selected.size === workers.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(workers.map(w => w.id)))
    }
  }

  const handleSelectWorker = (id: number) => {
    const newSelected = new Set(selected)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelected(newSelected)
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <Card>
        <div style={{ padding: '20px', color: 'var(--red)' }}>
          Error loading workers: {error.message}
        </div>
      </Card>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
        <Input
          placeholder="Search by name or ID..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          onBlur={debouncedSearch}
        />

        <Select
          value={stateFilter}
          onChange={e => setStateFilter(e.target.value)}
        >
          <option value="">All States</option>
          <option value="queued">Queued</option>
          <option value="running">Running</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </Select>

        <Select
          value={sort}
          onChange={e => setSort(e.target.value)}
        >
          <option value="name">Name</option>
          <option value="state">State</option>
          <option value="created_at">Created</option>
          <option value="last_activity">Last Activity</option>
        </Select>
      </div>

      <Card>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px', textAlign: 'left', width: '40px' }}>
                  <input
                    type="checkbox"
                    checked={selected.size === workers.length && workers.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Worker ID</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>State</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Steps</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {workers.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No workers found
                  </td>
                </tr>
              ) : (
                workers.map(worker => (
                  <tr
                    key={worker.id}
                    style={{
                      borderBottom: '1px solid var(--border)',
                      backgroundColor: selected.has(worker.id) ? 'var(--surface-2)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '12px' }}>
                      <input
                        type="checkbox"
                        checked={selected.has(worker.id)}
                        onChange={() => handleSelectWorker(worker.id)}
                      />
                    </td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '12px' }}>
                      {worker.worker_id}
                    </td>
                    <td style={{ padding: '12px' }}>{worker.name}</td>
                    <td style={{ padding: '12px' }}>
                      <Badge style={{ background: STATE_COLORS[worker.current_state] || 'var(--border)' }}>
                        {worker.current_state}
                      </Badge>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {worker.steps_executed}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {((1 - worker.steps_executed / Math.max(worker.steps_executed, 1)) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
          Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total}
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <Button
            variant="ghost"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
            Page {page} of {totalPages}
          </div>

          <Button
            variant="ghost"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      </div>

      {selected.size > 0 && (
        <div style={{ padding: '12px', background: 'var(--surface-2)', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{selected.size} worker(s) selected</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button variant="secondary" onClick={() => setSelected(new Set())}>
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
