import { useApiQuery } from '@/hooks/useApi.ts'
import Card from '@/components/ui/Card.tsx'
import Spinner from '@/components/ui/Spinner.tsx'

interface WorkerMetrics {
  worker_id: string
  step_count: number
  success_rate: number
  avg_duration_ms: number
  current_state: string
  uptime_ms: number
}

interface WorkerSummary {
  project_id: number
  total_workers: number
  running: number
  paused: number
  completed: number
  failed: number
  queued: number
  avg_step_count: number
  avg_success_rate: number
}

interface HealthStatus {
  status: 'healthy' | 'warning' | 'critical'
  message: string
}

interface MetricsCardProps {
  projectId: number
  workerId?: number
  showSummary?: boolean
}

export default function MetricsCard({ projectId, workerId, showSummary = false }: MetricsCardProps) {
  const { data: workerMetrics, isLoading: metricsLoading } = useApiQuery<WorkerMetrics>(
    ['metrics', projectId, workerId],
    workerId ? `/api/projects/${projectId}/workers/${workerId}/metrics` : null,
    { enabled: !!workerId }
  )

  const { data: summary, isLoading: summaryLoading } = useApiQuery<WorkerSummary>(
    ['summary', projectId],
    showSummary ? `/api/projects/${projectId}/workers/summary` : null,
    { enabled: showSummary }
  )

  const { data: health } = useApiQuery<HealthStatus>(
    ['health', projectId],
    `/api/projects/${projectId}/health/workers`
  )

  if ((workerId && metricsLoading) || (showSummary && summaryLoading)) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
        <Spinner />
      </div>
    )
  }

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'var(--green)'
      case 'warning':
        return 'var(--yellow)'
      case 'critical':
        return 'var(--red)'
      default:
        return 'var(--border)'
    }
  }

  const getStateColor = (state: string) => {
    const colors: Record<string, string> = {
      queued: 'var(--blue)',
      running: 'var(--green)',
      paused: 'var(--yellow)',
      completed: 'var(--green)',
      failed: 'var(--red)',
    }
    return colors[state] || 'var(--border)'
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Health Status Indicator */}
      {health && (
        <Card>
          <div style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: getHealthColor(health.status),
              }}
            />
            <div>
              <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                {health.status}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {health.message}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Worker Metrics */}
      {workerId && workerMetrics && (
        <Card>
          <div style={{ padding: '20px' }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Worker Metrics</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Steps
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {workerMetrics.step_count}
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Success Rate
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {(workerMetrics.success_rate * 100).toFixed(1)}%
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Avg Duration
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {workerMetrics.avg_duration_ms}ms
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Uptime
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {Math.floor(workerMetrics.uptime_ms / 1000 / 60)}m
                </div>
              </div>
            </div>

            <div style={{ marginTop: '12px', padding: '8px', background: 'var(--surface-2)', borderRadius: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: getStateColor(workerMetrics.current_state),
                  }}
                />
                <span style={{ textTransform: 'capitalize', fontSize: '14px' }}>
                  {workerMetrics.current_state}
                </span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Project Summary */}
      {showSummary && summary && (
        <Card>
          <div style={{ padding: '20px' }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Project Summary</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div style={{ background: 'var(--surface-2)', padding: '12px', borderRadius: '4px' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Total Workers
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.total_workers}
                </div>
              </div>

              <div style={{ background: 'var(--blue-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--blue)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Queued
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.queued}
                </div>
              </div>

              <div style={{ background: 'var(--green-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--green)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Running
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.running}
                </div>
              </div>

              <div style={{ background: 'var(--yellow-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--yellow)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Paused
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.paused}
                </div>
              </div>

              <div style={{ background: 'var(--surface-2)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--green)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Completed
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.completed}
                </div>
              </div>

              <div style={{ background: 'var(--red-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--red)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Failed
                </div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>
                  {summary.failed}
                </div>
              </div>
            </div>

            {/* State Distribution Pie Chart (Simple Bar) */}
            <div style={{ marginTop: '16px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
                State Distribution
              </div>
              <div style={{ height: '8px', background: 'var(--surface-2)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                {summary.total_workers > 0 && (
                  <>
                    <div
                      style={{
                        background: 'var(--blue)',
                        width: `${(summary.queued / summary.total_workers) * 100}%`,
                        height: '100%',
                      }}
                      title={`Queued: ${summary.queued}`}
                    />
                    <div
                      style={{
                        background: 'var(--green)',
                        width: `${(summary.running / summary.total_workers) * 100}%`,
                        height: '100%',
                      }}
                      title={`Running: ${summary.running}`}
                    />
                    <div
                      style={{
                        background: 'var(--yellow)',
                        width: `${(summary.paused / summary.total_workers) * 100}%`,
                        height: '100%',
                      }}
                      title={`Paused: ${summary.paused}`}
                    />
                    <div
                      style={{
                        background: 'var(--red)',
                        width: `${(summary.failed / summary.total_workers) * 100}%`,
                        height: '100%',
                      }}
                      title={`Failed: ${summary.failed}`}
                    />
                  </>
                )}
              </div>
            </div>

            {/* Averages */}
            <div style={{ marginTop: '16px', padding: '12px', background: 'var(--surface-2)', borderRadius: '4px', fontSize: '12px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Avg Steps: </span>
                  <strong>{summary.avg_step_count.toFixed(1)}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Avg Success Rate: </span>
                  <strong>{(summary.avg_success_rate * 100).toFixed(1)}%</strong>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
