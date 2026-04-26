interface ScheduledJob {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at?: string
}

interface JobListProps {
  jobs: ScheduledJob[]
  isLoading: boolean
  onSelectJob: (job: ScheduledJob) => void
}

export default function JobList({ jobs, isLoading, onSelectJob }: JobListProps) {
  if (isLoading) {
    return <div data-testid="job-list-loading">Loading jobs...</div>
  }

  return (
    <div className="job-list" data-testid="job-list">
      {jobs.length === 0 ? (
        <div className="empty-state">No scheduled jobs yet</div>
      ) : (
        <table className="jobs-table">
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} data-testid={`job-row-${job.id}`}>
                <td className="monospace">{job.id.slice(0, 8)}</td>
                <td>{job.name}</td>
                <td>
                  <span className={`status-badge status-${job.status}`}>{job.status}</span>
                </td>
                <td>{new Date(job.created_at).toLocaleDateString()}</td>
                <td>
                  <button
                    className="btn-small"
                    onClick={() => onSelectJob(job)}
                    data-testid={`view-job-${job.id}`}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <style jsx>{`
        .job-list {
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
          background: var(--surface-1);
        }

        .jobs-table {
          width: 100%;
          border-collapse: collapse;
        }

        .jobs-table thead {
          background: var(--surface-2);
          border-bottom: 1px solid var(--border);
        }

        .jobs-table th {
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          font-size: 0.875rem;
          text-transform: uppercase;
        }

        .jobs-table td {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border);
        }

        .jobs-table tbody tr:hover {
          background: var(--surface-2);
        }

        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .status-pending {
          background: var(--amber-glow);
          color: var(--amber);
        }

        .status-running {
          background: var(--accent-glow);
          color: var(--accent);
        }

        .status-completed {
          background: var(--success-glow);
          color: var(--success);
        }

        .status-failed {
          background: var(--red-glow);
          color: var(--red);
        }

        .monospace {
          font-family: 'Courier New', monospace;
        }

        .btn-small {
          padding: 0.4rem 0.8rem;
          font-size: 0.75rem;
          border: 1px solid var(--border);
          background: var(--surface-2);
          color: var(--text);
          cursor: pointer;
          border-radius: 3px;
        }

        .btn-small:hover {
          background: var(--surface-3);
        }

        .empty-state {
          padding: 2rem;
          text-align: center;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .jobs-table {
            font-size: 0.85rem;
          }

          .jobs-table th,
          .jobs-table td {
            padding: 0.5rem;
          }
        }
      `}</style>
    </div>
  )
}
