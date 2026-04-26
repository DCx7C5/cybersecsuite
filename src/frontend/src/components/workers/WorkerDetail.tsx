import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useWorkerDetail, useWorkerMetrics, type WorkerResponse } from '@/hooks/useWorkers.ts'
import Button from '@/components/ui/Button.tsx'
import Badge from '@/components/ui/Badge.tsx'
import Card from '@/components/ui/Card.tsx'
import Modal from '@/components/ui/Modal.tsx'
import Spinner from '@/components/ui/Spinner.tsx'

const STATE_COLORS: Record<string, string> = {
  queued: 'var(--blue)',
  running: 'var(--green)',
  paused: 'var(--yellow)',
  completed: 'var(--green)',
  failed: 'var(--red)',
}

interface WorkerDetailProps {
  projectId: number
  workerId: number
  onBack?: () => void
}

async function performAction(projectId: number, workerId: number, action: string) {
  const response = await fetch(`/api/projects/${projectId}/workers/${workerId}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  return response.json()
}

export default function WorkerDetail({ projectId, workerId, onBack }: WorkerDetailProps) {
  const { data: worker, isLoading: workerLoading, error: workerError } = useWorkerDetail(projectId, workerId)
  const { data: metrics, isLoading: metricsLoading } = useWorkerMetrics(projectId, workerId)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)

  const startMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'start'),
  })

  const pauseMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'pause'),
  })

  const resumeMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'resume'),
  })

  const stopMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'stop'),
  })

  const retryMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'retry'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => performAction(projectId, workerId, 'delete'),
    onSuccess: onBack,
  })

  if (workerLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
        <Spinner />
      </div>
    )
  }

  if (workerError || !worker) {
    return (
      <Card>
        <div style={{ padding: '20px', color: 'var(--red)' }}>
          Error loading worker: {workerError?.message}
        </div>
      </Card>
    )
  }

  const uptime = metrics?.uptime_ms ? Math.floor(metrics.uptime_ms / 1000 / 60) : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {onBack && (
        <Button variant="ghost" onClick={onBack}>
          ← Back to List
        </Button>
      )}

      <Card>
        <div style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div>
              <h1 style={{ margin: '0 0 8px 0', fontSize: '24px' }}>{worker.name}</h1>
              <p style={{ margin: '0', color: 'var(--text-muted)', fontSize: '14px' }}>
                ID: {worker.worker_id}
              </p>
            </div>
            <Badge style={{ background: STATE_COLORS[worker.current_state] || 'var(--border)' }}>
              {worker.current_state}
            </Badge>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                Type
              </div>
              <div>{worker.worker_type}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                Description
              </div>
              <div>{worker.description}</div>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px', marginBottom: '20px' }}>
            <h2 style={{ margin: '0 0 12px 0', fontSize: '16px' }}>State Transitions</h2>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {worker.current_state === 'queued' && (
                <Button
                  variant="primary"
                  onClick={() => startMutation.mutate()}
                  disabled={startMutation.isPending}
                >
                  Start
                </Button>
              )}
              {['running', 'paused'].includes(worker.current_state) && (
                <Button
                  variant="secondary"
                  onClick={() => pauseMutation.mutate()}
                  disabled={pauseMutation.isPending}
                >
                  Pause
                </Button>
              )}
              {worker.current_state === 'paused' && (
                <Button
                  variant="primary"
                  onClick={() => resumeMutation.mutate()}
                  disabled={resumeMutation.isPending}
                >
                  Resume
                </Button>
              )}
              {['running', 'paused'].includes(worker.current_state) && (
                <Button
                  variant="danger"
                  onClick={() => stopMutation.mutate()}
                  disabled={stopMutation.isPending}
                >
                  Stop
                </Button>
              )}
              {worker.current_state === 'failed' && (
                <Button
                  variant="primary"
                  onClick={() => retryMutation.mutate()}
                  disabled={retryMutation.isPending}
                >
                  Retry
                </Button>
              )}
              <Button
                variant="danger"
                onClick={() => setShowDeleteModal(true)}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {metrics && (
        <Card>
          <div style={{ padding: '24px' }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Metrics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Steps Executed
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {metrics.step_count}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Success Rate
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {(metrics.success_rate * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Avg Duration
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {metrics.avg_duration_ms}ms
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Uptime
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {uptime}m
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      <Card>
        <div style={{ padding: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Configuration</h2>
          <pre
            style={{
              background: 'var(--surface-2)',
              padding: '12px',
              borderRadius: '4px',
              fontSize: '12px',
              overflow: 'auto',
              maxHeight: '300px',
            }}
          >
            {JSON.stringify(worker.config, null, 2)}
          </pre>
        </div>
      </Card>

      {showDeleteModal && (
        <Modal
          title="Delete Worker"
          onClose={() => setShowDeleteModal(false)}
        >
          <div style={{ padding: '20px' }}>
            <p>Are you sure you want to delete this worker? This action cannot be undone.</p>
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <Button
                variant="ghost"
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
              >
                Delete
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
