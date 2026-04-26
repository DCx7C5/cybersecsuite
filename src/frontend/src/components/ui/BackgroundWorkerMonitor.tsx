import { useEffect, useState, useCallback } from 'react'
import Card from './Card'
import Spinner from './Spinner'
import Badge from './Badge'

interface WorkerMetrics {
  worker_id: string
  worker_type: string
  is_active: boolean
  health_status: 'healthy' | 'degraded' | 'unhealthy'
  active_task_count: number
  queue_depth: number
  total_tasks_processed: number
  avg_task_duration_ms: number
  error_count: number
  consecutive_errors: number
  last_heartbeat_seconds_ago: number
  recent_errors: Array<{ message: string; timestamp: number }>
}

interface WorkerMonitorData {
  timestamp: number
  worker_count: number
  active_workers: number
  total_queue_depth: number
  total_tasks_processed: number
  total_errors: number
  total_latency_ms: number
  avg_latency_ms: number
  vram_usage_mb?: number
  vram_available_mb?: number
  vram_percent?: number
  workers: WorkerMetrics[]
  uptime_seconds: number
  last_updated_at: string
}

interface BackgroundWorkerMonitorProps {
  pollInterval?: number
  refreshOnFocus?: boolean
}

const HEALTH_COLORS: Record<string, string> = {
  healthy: 'var(--success)',
  degraded: 'var(--warning)',
  unhealthy: 'var(--red)',
}

/**
 * BackgroundWorkerMonitor displays real-time metrics for background workers.
 * 
 * Features:
 * - Worker count and activity status
 * - Queue depth and pending tasks
 * - Performance metrics (latency, throughput)
 * - VRAM usage monitoring
 * - Error tracking and display
 * - Auto-refresh with configurable interval
 */
export function BackgroundWorkerMonitor({
  pollInterval = 5000,
  refreshOnFocus = true,
}: BackgroundWorkerMonitorProps) {
  const [data, setData] = useState<WorkerMonitorData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const fetchMetrics = useCallback(async () => {
    try {
      setError(null)
      const response = await fetch('/api/v1/metrics/workers')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const newData = await response.json()
      setData(newData)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics')
      setLoading(false)
    }
  }, [])

  // Initial fetch and polling
  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, pollInterval)
    return () => clearInterval(interval)
  }, [fetchMetrics, pollInterval])

  // Refresh on window focus
  useEffect(() => {
    if (!refreshOnFocus) return

    const handleFocus = () => {
      fetchMetrics()
    }

    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [refreshOnFocus, fetchMetrics])

  if (loading && !data) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spinner />
          <p>Loading worker metrics...</p>
        </div>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card style={{ borderColor: 'var(--red)' }}>
        <div style={{ color: 'var(--red)' }}>
          <strong>Error</strong>: {error || 'No data available'}
        </div>
      </Card>
    )
  }

  const toggleWorker = (workerId: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(workerId)) {
      newExpanded.delete(workerId)
    } else {
      newExpanded.add(workerId)
    }
    setExpanded(newExpanded)
  }

  const uptimeStr = formatUptime(data.uptime_seconds)

  return (
    <Card>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 'bold' }}>
          Background Workers
        </h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '12px',
            fontSize: '13px',
          }}
        >
          <div>
            <span style={{ opacity: 0.7 }}>Workers:</span>{' '}
            <strong>{data.active_workers}</strong>/{data.worker_count}
          </div>
          <div>
            <span style={{ opacity: 0.7 }}>Queue Depth:</span> <strong>{data.total_queue_depth}</strong>
          </div>
          <div>
            <span style={{ opacity: 0.7 }}>Errors:</span>{' '}
            <strong style={{ color: data.total_errors > 0 ? 'var(--red)' : 'inherit' }}>
              {data.total_errors}
            </strong>
          </div>
          <div>
            <span style={{ opacity: 0.7 }}>Uptime:</span> <strong>{uptimeStr}</strong>
          </div>
        </div>
      </div>

      {/* VRAM Monitoring */}
      {data.vram_percent !== null && (
        <div style={{ marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ marginBottom: '6px', fontSize: '13px', fontWeight: 'bold' }}>
            VRAM Usage
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <div
              style={{
                flex: 1,
                height: '6px',
                backgroundColor: 'var(--border)',
                borderRadius: '3px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${data.vram_percent ?? 0}%`,
                  height: '100%',
                  backgroundColor:
                    (data.vram_percent ?? 0) > 80
                      ? 'var(--red)'
                      : (data.vram_percent ?? 0) > 50
                        ? 'var(--warning)'
                        : 'var(--success)',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <span style={{ minWidth: '40px', textAlign: 'right' }}>
              {(data.vram_percent ?? 0).toFixed(1)}%
            </span>
          </div>
          <div style={{ fontSize: '11px', opacity: 0.7, marginTop: '4px' }}>
            {data.vram_usage_mb?.toFixed(0)} MB / {data.vram_available_mb?.toFixed(0)} MB available
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      <div style={{ marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13px' }}>
          <div>
            <span style={{ opacity: 0.7 }}>Avg Latency:</span>{' '}
            <strong>{data.avg_latency_ms.toFixed(2)}ms</strong>
          </div>
          <div>
            <span style={{ opacity: 0.7 }}>Tasks Processed:</span>{' '}
            <strong>{data.total_tasks_processed}</strong>
          </div>
        </div>
      </div>

      {/* Worker List */}
      <div>
        <div style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '8px' }}>
          Workers ({data.workers.length})
        </div>
        {data.workers.length === 0 ? (
          <div style={{ fontSize: '13px', opacity: 0.7 }}>No active workers</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {data.workers.map((worker) => (
              <div key={worker.worker_id}>
                <div
                  onClick={() => toggleWorker(worker.worker_id)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: 'var(--surface-alt)',
                    borderRadius: 'var(--radius)',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '12px',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--surface-alt-hover)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'var(--surface-alt)')}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: HEALTH_COLORS[worker.health_status] || 'var(--border)',
                      }}
                    />
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{worker.worker_id}</div>
                      <div style={{ opacity: 0.7, fontSize: '11px' }}>{worker.worker_type}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Badge variant="info">{`${worker.active_task_count} active`}</Badge>
                    <Badge variant="info">{`Q:${worker.queue_depth}`}</Badge>
                    <span style={{ opacity: 0.7 }}>
                      {expanded.has(worker.worker_id) ? '▼' : '▶'}
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {expanded.has(worker.worker_id) && (
                  <div
                    style={{
                      padding: '8px 12px',
                      backgroundColor: 'var(--surface)',
                      borderRadius: '0 0 var(--radius) var(--radius)',
                      fontSize: '12px',
                      borderLeft: `2px solid ${HEALTH_COLORS[worker.health_status]}`,
                    }}
                  >
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '8px' }}>
                      <div>
                        <span style={{ opacity: 0.7 }}>Total Tasks:</span>{' '}
                        <strong>{worker.total_tasks_processed}</strong>
                      </div>
                      <div>
                        <span style={{ opacity: 0.7 }}>Avg Duration:</span>{' '}
                        <strong>{worker.avg_task_duration_ms}ms</strong>
                      </div>
                      <div>
                        <span style={{ opacity: 0.7 }}>Errors:</span>{' '}
                        <strong style={{ color: worker.error_count > 0 ? 'var(--red)' : 'inherit' }}>
                          {worker.error_count}
                        </strong>
                      </div>
                      <div>
                        <span style={{ opacity: 0.7 }}>Last Heartbeat:</span>{' '}
                        <strong>{formatSeconds(worker.last_heartbeat_seconds_ago)} ago</strong>
                      </div>
                    </div>

                    {worker.recent_errors.length > 0 && (
                      <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid var(--border)' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '4px', color: 'var(--red)' }}>
                          Recent Errors:
                        </div>
                        <div style={{ fontSize: '11px' }}>
                          {worker.recent_errors.slice(0, 3).map((err, idx) => (
                            <div key={idx} style={{ marginBottom: '4px', opacity: 0.8 }}>
                              • {err.message}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Last Updated */}
      <div
        style={{
          marginTop: '12px',
          paddingTop: '8px',
          borderTop: '1px solid var(--border)',
          fontSize: '11px',
          opacity: 0.6,
        }}
      >
        Last updated: {new Date(data.last_updated_at).toLocaleTimeString()}
      </div>
    </Card>
  )
}

function formatUptime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

function formatSeconds(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s`
  }
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    return `${minutes}m`
  }
  const hours = Math.floor(minutes / 60)
  return `${hours}h`
}
