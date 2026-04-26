import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import ScheduleForm from './ScheduleForm'
import JobList from './JobList'

interface ScheduledJob {
  id: string
  name: string
  template_id: string
  schedule_type: 'now' | 'once' | 'recurring'
  schedule_time?: string
  cron_expression?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at?: string
  completed_at?: string
  result?: Record<string, unknown>
}

interface JobsResponse {
  data: ScheduledJob[]
  total: number
  page: number
  limit: number
}

export default function BatchScheduler() {
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedJob, setSelectedJob] = useState<ScheduledJob | null>(null)
  const [page, setPage] = useState(1)

  const { data: jobsData, isLoading, refetch } = useQuery({
    queryKey: ['batch-jobs', page],
    queryFn: () => {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('limit', '10')
      return fetchApi<JobsResponse>(`/api/batch/jobs?${params.toString()}`)
    },
  })

  const scheduleMutation = useMutation({
    mutationFn: (data: {
      name: string
      template_id: string
      schedule_type: 'now' | 'once' | 'recurring'
      schedule_time?: string
      cron_expression?: string
    }) =>
      fetchApi('/api/batch/schedule', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      refetch()
      setShowScheduleModal(false)
    },
  })

  const cancelJobMutation = useMutation({
    mutationFn: (jobId: string) =>
      fetchApi(`/api/batch/jobs/${jobId}/cancel`, {
        method: 'POST',
      }),
    onSuccess: () => {
      refetch()
      setSelectedJob(null)
    },
  })

  return (
    <div className="batch-scheduler" data-testid="batch-scheduler">
      <div className="scheduler-header">
        <h1>Batch Job Scheduling</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowScheduleModal(true)}
          data-testid="schedule-job-btn"
        >
          + Schedule New Job
        </button>
      </div>

      <div className="scheduler-content">
        <JobList
          jobs={jobsData?.data || []}
          isLoading={isLoading}
          onSelectJob={setSelectedJob}
          onRefresh={refetch}
        />

        {jobsData && jobsData.total > 10 && (
          <div className="pagination" data-testid="pagination">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              data-testid="prev-page"
            >
              Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page >= Math.ceil(jobsData.total / 10)}
              data-testid="next-page"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {showScheduleModal && (
        <ScheduleForm
          onSchedule={(data) => {
            scheduleMutation.mutate(data)
          }}
          onClose={() => setShowScheduleModal(false)}
        />
      )}

      {selectedJob && (
        <div
          className="job-detail-modal"
          data-testid="job-detail-modal"
          onClick={() => setSelectedJob(null)}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Job Details</h2>
              <button
                className="close-btn"
                onClick={() => setSelectedJob(null)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <table className="details-table">
                <tbody>
                  <tr>
                    <td className="label">Job ID</td>
                    <td className="value">{selectedJob.id}</td>
                  </tr>
                  <tr>
                    <td className="label">Name</td>
                    <td className="value">{selectedJob.name}</td>
                  </tr>
                  <tr>
                    <td className="label">Status</td>
                    <td className="value">
                      <span className={`status-badge status-${selectedJob.status}`}>
                        {selectedJob.status}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className="label">Created</td>
                    <td className="value">{new Date(selectedJob.created_at).toLocaleString()}</td>
                  </tr>
                  {selectedJob.started_at && (
                    <tr>
                      <td className="label">Started</td>
                      <td className="value">{new Date(selectedJob.started_at).toLocaleString()}</td>
                    </tr>
                  )}
                  {selectedJob.completed_at && (
                    <tr>
                      <td className="label">Completed</td>
                      <td className="value">
                        {new Date(selectedJob.completed_at).toLocaleString()}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>

              {selectedJob.status === 'running' && (
                <div className="modal-footer">
                  <button
                    className="btn btn-danger"
                    onClick={() => cancelJobMutation.mutate(selectedJob.id)}
                    data-testid="cancel-job-btn"
                  >
                    Cancel Job
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .batch-scheduler {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .scheduler-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .scheduler-content {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 1rem;
        }

        .btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .btn-primary {
          background: var(--accent);
          color: white;
          border-color: var(--accent);
        }

        .btn-primary:hover {
          background: var(--accent-dark);
        }

        .btn-danger {
          background: var(--red);
          color: white;
          border-color: var(--red);
        }

        .btn-danger:hover {
          background: var(--red-dark);
        }

        .job-detail-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2000;
        }

        .modal-content {
          background: var(--surface-1);
          border: 1px solid var(--border);
          border-radius: 8px;
          max-width: 600px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid var(--border);
          background: var(--surface-2);
        }

        .modal-header h2 {
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          font-size: 1.5rem;
          padding: 0;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .details-table {
          width: 100%;
          border-collapse: collapse;
        }

        .details-table tr {
          border-bottom: 1px solid var(--border);
        }

        .details-table td {
          padding: 0.75rem;
        }

        .details-table .label {
          font-weight: 600;
          width: 150px;
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

        .modal-footer {
          padding: 1.5rem;
          border-top: 1px solid var(--border);
          display: flex;
          justify-content: flex-end;
        }

        @media (max-width: 768px) {
          .scheduler-header {
            flex-direction: column;
            align-items: stretch;
          }

          .scheduler-header button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
