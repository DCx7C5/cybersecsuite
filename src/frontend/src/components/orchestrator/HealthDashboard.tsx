import { useEffect, useState } from 'react'
import * as RQ from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import LogsViewer from './LogsViewer'

interface HealthMetrics {
  uptime_hours: number
  active_workers: number
  idle_workers: number
  failed_workers: number
  api_response_time_ms: number
  database_connections_used: number
  database_connections_available: number
  memory_usage_percent: number
  cpu_usage_percent: number
  error_rate_24h: number
}

interface SystemLog {
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
  source: string
}

export default function HealthDashboard() {
  const [metrics, setMetrics] = useState<HealthMetrics>({
    uptime_hours: 240,
    active_workers: 5,
    idle_workers: 2,
    failed_workers: 0,
    api_response_time_ms: 125,
    database_connections_used: 3,
    database_connections_available: 7,
    memory_usage_percent: 62,
    cpu_usage_percent: 35,
    error_rate_24h: 0.2,
  })
  const [showLogs, setShowLogs] = useState(false)

  const { data: logs } = RQ.useQuery({
    queryKey: ['system-logs'],
    queryFn: () => fetchApi<SystemLog[]>('/api/system/logs'),
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

  const getHealthStatus = () => {
    if (metrics.error_rate_24h > 5) return 'critical'
    if (metrics.error_rate_24h > 1) return 'warning'
    if (metrics.cpu_usage_percent > 80) return 'warning'
    return 'healthy'
  }

  const healthStatus = getHealthStatus()

  return (
    <div className="health-dashboard" data-testid="health-dashboard">
      <div className="dashboard-header">
        <h1>System Health & Diagnostics</h1>
        <div className="health-status">
          <span className={`status-indicator status-${healthStatus}`} />
          <span className="status-text">{healthStatus.toUpperCase()}</span>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>📊 System Uptime</h3>
          <p className="metric-value" data-testid="uptime-value">
            {metrics.uptime_hours} hours
          </p>
          <p className="metric-info">
            {(metrics.uptime_hours / 24).toFixed(1)} days
          </p>
        </div>

        <div className="metric-card">
          <h3>👷 Workers</h3>
          <p className="metric-value" data-testid="workers-value">
            {metrics.active_workers} Active
          </p>
          <p className="metric-info">
            {metrics.idle_workers} Idle, {metrics.failed_workers} Failed
          </p>
        </div>

        <div className="metric-card">
          <h3>⏱️ API Response Time</h3>
          <p className="metric-value" data-testid="response-time-value">
            {metrics.api_response_time_ms}ms
          </p>
          <p className="metric-info">Average (P50)</p>
        </div>

        <div className="metric-card">
          <h3>💾 Memory Usage</h3>
          <p className="metric-value" data-testid="memory-value">
            {metrics.memory_usage_percent}%
          </p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${metrics.memory_usage_percent}%` }}
            />
          </div>
        </div>

        <div className="metric-card">
          <h3>🔧 CPU Usage</h3>
          <p className="metric-value" data-testid="cpu-value">
            {metrics.cpu_usage_percent}%
          </p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${metrics.cpu_usage_percent}%` }}
            />
          </div>
        </div>

        <div className="metric-card">
          <h3>🗄️ Database Connections</h3>
          <p className="metric-value" data-testid="db-connections-value">
            {metrics.database_connections_used}/{metrics.database_connections_available}
          </p>
          <p className="metric-info">Used/Available</p>
        </div>

        <div className="metric-card">
          <h3>📈 Error Rate (24h)</h3>
          <p className="metric-value" data-testid="error-rate-value">
            {metrics.error_rate_24h}%
          </p>
          <div className="progress-bar">
            <div
              className={`progress-fill ${metrics.error_rate_24h > 1 ? 'error' : ''}`}
              style={{ width: `${Math.min(metrics.error_rate_24h, 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="diagnostics-section">
        <div className="section-header">
          <h2>Diagnostics</h2>
          <button
            className="btn btn-small"
            onClick={() => setShowLogs(!showLogs)}
            data-testid="toggle-logs-btn"
          >
            {showLogs ? 'Hide' : 'Show'} Logs
          </button>
        </div>

        {showLogs && logs && (
          <LogsViewer logs={logs} />
        )}

        <div className="diagnostic-actions">
          <button
            className="btn btn-secondary"
            data-testid="generate-report-btn"
          >
            Generate Diagnostic Report
          </button>
          <button
            className="btn btn-secondary"
            data-testid="export-metrics-btn"
          >
            Export Metrics
          </button>
        </div>
      </div>

      <style>{`
        .health-dashboard {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .health-status {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background: var(--surface-2);
          border-radius: 4px;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        .status-healthy {
          background: var(--success);
        }

        .status-warning {
          background: var(--amber);
        }

        .status-critical {
          background: var(--red);
        }

        .status-text {
          font-weight: 600;
          font-size: 0.875rem;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
        }

        .metric-card {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .metric-card h3 {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          text-transform: uppercase;
          color: var(--text-muted);
          letter-spacing: 0.5px;
        }

        .metric-value {
          margin: 0;
          font-size: 1.75rem;
          font-weight: 600;
          color: var(--text);
          font-family: 'Courier New', monospace;
        }

        .metric-info {
          margin: 0.5rem 0 0 0;
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .progress-bar {
          width: 100%;
          height: 6px;
          background: var(--surface-2);
          border-radius: 3px;
          overflow: hidden;
          margin-top: 0.5rem;
        }

        .progress-fill {
          height: 100%;
          background: var(--accent);
          transition: width 0.3s ease;
        }

        .progress-fill.error {
          background: var(--red);
        }

        .diagnostics-section {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .section-header h2 {
          margin: 0;
          font-size: 1.125rem;
        }

        .diagnostic-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
          flex-wrap: wrap;
        }

        .btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .btn-secondary {
          background: var(--surface-2);
          color: var(--text);
        }

        .btn-secondary:hover {
          background: var(--surface-3);
        }

        .btn-small {
          padding: 0.4rem 0.8rem;
          font-size: 0.75rem;
          background: var(--accent);
          color: white;
          border-color: var(--accent);
        }

        .btn-small:hover {
          background: var(--accent-dark);
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        @media (max-width: 768px) {
          .metrics-grid {
            grid-template-columns: 1fr;
          }

          .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .diagnostic-actions {
            flex-direction: column;
          }

          .diagnostic-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
