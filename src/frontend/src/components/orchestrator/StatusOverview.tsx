import { useEffect, useState } from 'react'

interface HealthMetrics {
  uptime_hours: number
  active_workers: number
  idle_workers: number
  failed_workers: number
  cpu_usage_percent: number
  memory_usage_percent: number
  api_response_time_ms: number
  total_jobs_processed: number
}

interface StatusOverviewProps {
  isPaused?: boolean
}

export default function StatusOverview({ isPaused = false }: StatusOverviewProps) {
  const [metrics, setMetrics] = useState<HealthMetrics>({
    uptime_hours: 24,
    active_workers: 5,
    idle_workers: 2,
    failed_workers: 0,
    cpu_usage_percent: 35,
    memory_usage_percent: 62,
    api_response_time_ms: 125,
    total_jobs_processed: 1542,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        api_response_time_ms: Math.floor(Math.random() * 200) + 50,
        cpu_usage_percent: Math.floor(Math.random() * 80) + 10,
        memory_usage_percent: Math.floor(Math.random() * 70) + 30,
      }))
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const statusColor = isPaused
    ? 'var(--amber)'
    : metrics.failed_workers > 0
      ? 'var(--red)'
      : 'var(--success)'

  return (
    <div className="status-overview" data-testid="status-overview">
      <div className="status-card">
        <div className="status-indicator" style={{ backgroundColor: statusColor }} />
        <div className="status-info">
          <span className="status-label">System Status</span>
          <span className="status-value" data-testid="status-value">
            {isPaused ? 'Paused' : 'Running'}
          </span>
        </div>
      </div>

      <div className="status-card">
        <div className="metric-icon">👷</div>
        <div className="metric-content">
          <span className="metric-label">Workers</span>
          <span className="metric-value" data-testid="active-workers">
            {metrics.active_workers}/{metrics.active_workers + metrics.idle_workers + metrics.failed_workers}
          </span>
        </div>
      </div>

      <div className="status-card">
        <div className="metric-icon">⏱️</div>
        <div className="metric-content">
          <span className="metric-label">Response Time</span>
          <span className="metric-value" data-testid="response-time">
            {metrics.api_response_time_ms}ms
          </span>
        </div>
      </div>

      <div className="status-card">
        <div className="metric-icon">💾</div>
        <div className="metric-content">
          <span className="metric-label">Memory</span>
          <span className="metric-value" data-testid="memory-usage">
            {metrics.memory_usage_percent}%
          </span>
        </div>
      </div>

      <style jsx>{`
        .status-overview {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
          align-items: center;
        }

        .status-card {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: var(--surface-1);
          border: 1px solid var(--border);
          border-radius: 6px;
          min-width: 200px;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          flex-shrink: 0;
          animation: pulse 2s infinite;
        }

        .status-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .status-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .status-value {
          font-size: 1rem;
          font-weight: 600;
          color: var(--text);
        }

        .metric-icon {
          font-size: 1.5rem;
        }

        .metric-content {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .metric-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .metric-value {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text);
          font-family: 'Courier New', monospace;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        @media (max-width: 1024px) {
          .status-card {
            min-width: 150px;
            padding: 0.75rem;
          }
        }

        @media (max-width: 768px) {
          .status-overview {
            gap: 0.75rem;
          }

          .status-card {
            min-width: 130px;
            padding: 0.5rem;
            font-size: 0.85rem;
          }
        }

        @media (max-width: 375px) {
          .status-overview {
            gap: 0.5rem;
          }

          .status-card {
            min-width: 100%;
            padding: 0.75rem;
          }
        }
      `}</style>
    </div>
  )
}
