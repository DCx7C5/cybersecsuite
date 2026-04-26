interface ConfigHistoryEntry {
  timestamp: string
  user: string
  action: 'created' | 'updated' | 'deleted'
  config_key: string
  old_value: unknown
  new_value: unknown
}

interface ConfigHistoryProps {
  entries: ConfigHistoryEntry[]
}

export default function ConfigHistory({ entries }: ConfigHistoryProps) {
  const displayEntries = entries.slice(0, 10)

  return (
    <div className="config-history" data-testid="config-history">
      <h3>Configuration History (Last 10 Changes)</h3>
      <div className="history-list">
        {displayEntries.length === 0 ? (
          <div className="empty-state">No history available</div>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Config Key</th>
                <th>Old Value</th>
                <th>New Value</th>
              </tr>
            </thead>
            <tbody>
              {displayEntries.map((entry, idx) => (
                <tr
                  key={idx}
                  data-testid={`history-entry-${idx}`}
                  className={`action-${entry.action}`}
                >
                  <td>{new Date(entry.timestamp).toLocaleString()}</td>
                  <td>{entry.user}</td>
                  <td>
                    <span className={`action-badge action-${entry.action}`}>
                      {entry.action}
                    </span>
                  </td>
                  <td className="monospace">{entry.config_key}</td>
                  <td className="monospace">{String(entry.old_value)}</td>
                  <td className="monospace">{String(entry.new_value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <style jsx>{`
        .config-history {
          background: var(--surface-1);
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .config-history h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
        }

        .history-list {
          overflow-x: auto;
        }

        .history-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .history-table thead {
          background: var(--surface-2);
          border-bottom: 1px solid var(--border);
        }

        .history-table th {
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          text-transform: uppercase;
          font-size: 0.75rem;
          letter-spacing: 0.5px;
        }

        .history-table td {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border);
        }

        .history-table tbody tr:hover {
          background: var(--surface-2);
        }

        .action-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-weight: 600;
          text-transform: uppercase;
          font-size: 0.7rem;
        }

        .action-created {
          background: var(--success-glow);
          color: var(--success);
        }

        .action-updated {
          background: var(--accent-glow);
          color: var(--accent);
        }

        .action-deleted {
          background: var(--red-glow);
          color: var(--red);
        }

        .monospace {
          font-family: 'Courier New', monospace;
          max-width: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .empty-state {
          text-align: center;
          padding: 2rem;
          color: var(--text-muted);
        }

        @media (max-width: 1024px) {
          .history-table {
            font-size: 0.8rem;
          }

          .history-table th,
          .history-table td {
            padding: 0.5rem;
          }

          .monospace {
            max-width: 100px;
          }
        }

        @media (max-width: 768px) {
          .config-history {
            padding: 1rem;
          }

          .history-table {
            font-size: 0.75rem;
          }

          .history-table th,
          .history-table td {
            padding: 0.4rem;
          }

          .monospace {
            max-width: 50px;
          }
        }
      `}</style>
    </div>
  )
}
