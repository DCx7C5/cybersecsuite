interface SystemLog {
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
  source: string
}

interface LogsViewerProps {
  logs: SystemLog[]
}

export default function LogsViewer({ logs }: LogsViewerProps) {
  const displayLogs = logs.slice(0, 100)

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      info: 'var(--accent)',
      warning: 'var(--amber)',
      error: 'var(--red)',
    }
    return colors[level] || 'var(--text)'
  }

  return (
    <div className="logs-viewer" data-testid="logs-viewer">
      <div className="logs-container">
        {displayLogs.length === 0 ? (
          <div className="empty-state">No logs available</div>
        ) : (
          <table className="logs-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Source</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {displayLogs
                .slice()
                .reverse()
                .map((log, idx) => (
                  <tr
                    key={idx}
                    data-testid={`log-row-${idx}`}
                    className={`log-${log.level}`}
                  >
                    <td className="timestamp">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td>
                      <span
                        className="level-badge"
                        style={{ color: getLevelColor(log.level) }}
                      >
                        {log.level.toUpperCase()}
                      </span>
                    </td>
                    <td className="source">{log.source}</td>
                    <td className="message">{log.message}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        )}
      </div>

      <style>{`
        .logs-viewer {
          margin-top: 1rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          overflow: hidden;
        }

        .logs-container {
          max-height: 400px;
          overflow-y: auto;
          background: var(--surface-2);
        }

        .logs-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.85rem;
          font-family: 'Courier New', monospace;
        }

        .logs-table thead {
          background: var(--surface-3);
          border-bottom: 1px solid var(--border);
          position: sticky;
          top: 0;
        }

        .logs-table th {
          padding: 0.5rem;
          text-align: left;
          font-weight: 600;
          font-size: 0.75rem;
          text-transform: uppercase;
          color: var(--text-muted);
        }

        .logs-table td {
          padding: 0.5rem;
          border-bottom: 1px solid var(--border);
        }

        .logs-table tbody tr:hover {
          background: var(--surface-1);
        }

        .timestamp {
          color: var(--text-muted);
          width: 120px;
          white-space: nowrap;
        }

        .level-badge {
          font-weight: 600;
          font-size: 0.7rem;
        }

        .source {
          color: var(--text-muted);
          width: 100px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .message {
          max-width: 400px;
          word-break: break-word;
        }

        .log-error {
          background: rgba(255, 0, 0, 0.05);
        }

        .log-warning {
          background: rgba(255, 193, 7, 0.05);
        }

        .empty-state {
          padding: 1.5rem;
          text-align: center;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .logs-table {
            font-size: 0.8rem;
          }

          .logs-table th,
          .logs-table td {
            padding: 0.35rem;
          }

          .source {
            width: 80px;
          }

          .message {
            max-width: 200px;
          }
        }
      `}</style>
    </div>
  )
}
