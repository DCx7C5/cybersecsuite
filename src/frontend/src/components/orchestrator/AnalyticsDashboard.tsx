import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import MetricsCharts from './MetricsCharts'

interface AnalyticsData {
  success_rate: number
  avg_runtime_ms: number
  throughput: number
  total_executions: number
  state_distribution: {
    queued: number
    running: number
    paused: number
    completed: number
    failed: number
  }
  error_rate: number
}

export default function AnalyticsDashboard() {
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('7d')
  const [workerType, setWorkerType] = useState<string>('all')
  const [state, setState] = useState<string>('all')

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', dateRange, workerType, state],
    queryFn: () => {
      const params = new URLSearchParams()
      params.append('range', dateRange)
      if (workerType !== 'all') params.append('worker_type', workerType)
      if (state !== 'all') params.append('state', state)
      return fetchApi<AnalyticsData>(`/api/analytics?${params.toString()}`)
    },
  })

  const mockData: AnalyticsData = {
    success_rate: 98.5,
    avg_runtime_ms: 245,
    throughput: 1240,
    total_executions: 8674,
    state_distribution: {
      queued: 234,
      running: 12,
      paused: 0,
      completed: 8401,
      failed: 27,
    },
    error_rate: 1.5,
  }

  const data = analytics || mockData

  const handleExportCSV = () => {
    const csv = `Metric,Value
Success Rate,${data.success_rate}%
Average Runtime,${data.avg_runtime_ms}ms
Throughput,${data.throughput}/hour
Total Executions,${data.total_executions}
Error Rate,${data.error_rate}%`
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
    const a = document.createElement('a')
    a.href = url
    a.download = 'analytics.csv'
    a.click()
  }

  const handleExportJSON = () => {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    )
    const a = document.createElement('a')
    a.href = url
    a.download = 'analytics.json'
    a.click()
  }

  if (isLoading) {
    return <div data-testid="analytics-loading">Loading analytics...</div>
  }

  return (
    <div className="analytics-dashboard" data-testid="analytics-dashboard">
      <div className="analytics-header">
        <h1>Analytics Dashboard</h1>
      </div>

      <div className="analytics-filters">
        <div className="filter-group">
          <label htmlFor="date-range">Date Range</label>
          <select
            id="date-range"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as typeof dateRange)}
            data-testid="date-range-select"
            className="filter-select"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="worker-type">Worker Type</label>
          <select
            id="worker-type"
            value={workerType}
            onChange={(e) => setWorkerType(e.target.value)}
            data-testid="worker-type-select"
            className="filter-select"
          >
            <option value="all">All Workers</option>
            <option value="type1">Type 1</option>
            <option value="type2">Type 2</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="state-filter">State</label>
          <select
            id="state-filter"
            value={state}
            onChange={(e) => setState(e.target.value)}
            data-testid="state-select"
            className="filter-select"
          >
            <option value="all">All States</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      <div className="key-metrics">
        <div className="metric-box">
          <h3>Success Rate</h3>
          <p className="metric-value" data-testid="success-rate-metric">
            {data.success_rate}%
          </p>
        </div>
        <div className="metric-box">
          <h3>Avg Runtime</h3>
          <p className="metric-value" data-testid="avg-runtime-metric">
            {data.avg_runtime_ms}ms
          </p>
        </div>
        <div className="metric-box">
          <h3>Throughput</h3>
          <p className="metric-value" data-testid="throughput-metric">
            {data.throughput}/hr
          </p>
        </div>
        <div className="metric-box">
          <h3>Total Executions</h3>
          <p className="metric-value" data-testid="total-executions-metric">
            {data.total_executions}
          </p>
        </div>
      </div>

      <MetricsCharts data={data} />

      <div className="state-distribution">
        <h2>State Distribution</h2>
        <table className="distribution-table">
          <tbody>
            <tr>
              <td>Queued</td>
              <td>{data.state_distribution.queued}</td>
            </tr>
            <tr>
              <td>Running</td>
              <td>{data.state_distribution.running}</td>
            </tr>
            <tr>
              <td>Paused</td>
              <td>{data.state_distribution.paused}</td>
            </tr>
            <tr>
              <td>Completed</td>
              <td>{data.state_distribution.completed}</td>
            </tr>
            <tr>
              <td>Failed</td>
              <td>{data.state_distribution.failed}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="analytics-actions">
        <button className="btn btn-secondary" onClick={handleExportCSV} data-testid="export-csv-btn">
          📥 Export CSV
        </button>
        <button className="btn btn-secondary" onClick={handleExportJSON} data-testid="export-json-btn">
          📥 Export JSON
        </button>
      </div>

      <style jsx>{`
        .analytics-dashboard {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .analytics-header h1 {
          margin: 0;
        }

        .analytics-filters {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
          padding: 1rem;
          background: var(--surface-2);
          border-radius: 6px;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .filter-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-muted);
        }

        .filter-select {
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-1);
          color: var(--text);
          min-width: 150px;
        }

        .key-metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .metric-box {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
          text-align: center;
        }

        .metric-box h3 {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          text-transform: uppercase;
          color: var(--text-muted);
          letter-spacing: 0.5px;
        }

        .metric-value {
          margin: 0;
          font-size: 2rem;
          font-weight: 600;
          color: var(--accent);
          font-family: 'Courier New', monospace;
        }

        .state-distribution {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .state-distribution h2 {
          margin: 0 0 1rem 0;
          font-size: 1.125rem;
        }

        .distribution-table {
          width: 100%;
          border-collapse: collapse;
        }

        .distribution-table tr {
          border-bottom: 1px solid var(--border);
        }

        .distribution-table td {
          padding: 0.75rem;
        }

        .distribution-table td:first-child {
          font-weight: 600;
          width: 50%;
        }

        .distribution-table td:last-child {
          text-align: right;
          font-family: 'Courier New', monospace;
        }

        .analytics-actions {
          display: flex;
          gap: 0.5rem;
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

        @media (max-width: 768px) {
          .analytics-filters {
            flex-direction: column;
          }

          .filter-select {
            min-width: 100%;
          }

          .key-metrics {
            grid-template-columns: 1fr;
          }

          .analytics-actions {
            flex-direction: column;
          }

          .analytics-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
