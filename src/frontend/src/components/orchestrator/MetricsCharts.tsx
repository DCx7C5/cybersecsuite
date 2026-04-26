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

interface MetricsChartsProps {
  data: AnalyticsData
}

export default function MetricsCharts({ data }: MetricsChartsProps) {
  const totalStates =
    data.state_distribution.queued +
    data.state_distribution.running +
    data.state_distribution.paused +
    data.state_distribution.completed +
    data.state_distribution.failed

  const getStatePercentage = (count: number) => {
    return totalStates > 0 ? ((count / totalStates) * 100).toFixed(1) : '0'
  }

  return (
    <div className="metrics-charts" data-testid="metrics-charts">
      <div className="chart-container">
        <h2>Performance Metrics</h2>
        <div className="metrics-summary">
          <div className="metric-row">
            <span className="label">Success Rate:</span>
            <div className="progress-bar">
              <div
                className="progress-fill success"
                style={{ width: `${data.success_rate}%` }}
              />
            </div>
            <span className="value">{data.success_rate}%</span>
          </div>
          <div className="metric-row">
            <span className="label">Error Rate:</span>
            <div className="progress-bar">
              <div
                className="progress-fill error"
                style={{ width: `${Math.min(data.error_rate, 100)}%` }}
              />
            </div>
            <span className="value">{data.error_rate}%</span>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <h2>State Distribution</h2>
        <div className="distribution-chart">
          <div className="state-bar queued">
            <span>{getStatePercentage(data.state_distribution.queued)}%</span>
            <small>Queued: {data.state_distribution.queued}</small>
          </div>
          <div className="state-bar running">
            <span>{getStatePercentage(data.state_distribution.running)}%</span>
            <small>Running: {data.state_distribution.running}</small>
          </div>
          <div className="state-bar completed">
            <span>{getStatePercentage(data.state_distribution.completed)}%</span>
            <small>Completed: {data.state_distribution.completed}</small>
          </div>
          <div className="state-bar failed">
            <span>{getStatePercentage(data.state_distribution.failed)}%</span>
            <small>Failed: {data.state_distribution.failed}</small>
          </div>
          <div className="state-bar paused">
            <span>{getStatePercentage(data.state_distribution.paused)}%</span>
            <small>Paused: {data.state_distribution.paused}</small>
          </div>
        </div>
      </div>

      <style jsx>{`
        .metrics-charts {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1.5rem;
        }

        .chart-container {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .chart-container h2 {
          margin: 0 0 1.5rem 0;
          font-size: 1rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .metrics-summary {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .metric-row {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .label {
          font-weight: 600;
          min-width: 100px;
          font-size: 0.875rem;
        }

        .progress-bar {
          flex: 1;
          height: 24px;
          background: var(--surface-2);
          border-radius: 12px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 0.75rem;
          font-weight: 600;
          transition: width 0.3s ease;
        }

        .progress-fill.success {
          background: var(--success);
        }

        .progress-fill.error {
          background: var(--red);
        }

        .value {
          font-weight: 600;
          min-width: 60px;
          text-align: right;
          font-family: 'Courier New', monospace;
        }

        .distribution-chart {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .state-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.75rem;
          border-radius: 4px;
          color: white;
          font-weight: 600;
          min-height: 40px;
        }

        .state-bar.queued {
          background: var(--amber);
        }

        .state-bar.running {
          background: var(--accent);
        }

        .state-bar.completed {
          background: var(--success);
        }

        .state-bar.failed {
          background: var(--red);
        }

        .state-bar.paused {
          background: var(--text-muted);
        }

        .state-bar small {
          font-size: 0.75rem;
          opacity: 0.9;
        }

        @media (max-width: 1024px) {
          .metrics-charts {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 768px) {
          .chart-container {
            padding: 1rem;
          }

          .metric-row {
            flex-wrap: wrap;
          }

          .label {
            width: 100%;
          }

          .progress-bar {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
