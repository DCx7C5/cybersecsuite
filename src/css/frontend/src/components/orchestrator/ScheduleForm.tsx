import { useState } from 'react'

interface ScheduleFormProps {
  onSchedule: (data: {
    name: string
    template_id: string
    schedule_type: 'now' | 'once' | 'recurring'
    schedule_time?: string
    cron_expression?: string
  }) => void
  onClose: () => void
}

export default function ScheduleForm({ onSchedule, onClose }: ScheduleFormProps) {
  const [jobName, setJobName] = useState('')
  const [templateId, setTemplateId] = useState('')
  const [scheduleType, setScheduleType] = useState<'now' | 'once' | 'recurring'>('now')
  const [scheduleTime, setScheduleTime] = useState('')
  const [cronExpression, setCronExpression] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = () => {
    setError('')

    if (!jobName.trim()) {
      setError('Job name is required')
      return
    }

    if (!templateId.trim()) {
      setError('Template is required')
      return
    }

    if (scheduleType === 'once' && !scheduleTime) {
      setError('Schedule time is required')
      return
    }

    if (scheduleType === 'recurring' && !cronExpression.trim()) {
      setError('Cron expression is required')
      return
    }

    onSchedule({
      name: jobName,
      template_id: templateId,
      schedule_type: scheduleType,
      schedule_time: scheduleType === 'once' ? scheduleTime : undefined,
      cron_expression: scheduleType === 'recurring' ? cronExpression : undefined,
    })
  }

  return (
    <div className="modal-overlay" data-testid="schedule-form-modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Schedule New Batch Job</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="error-message" data-testid="schedule-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="job-name">Job Name</label>
            <input
              id="job-name"
              type="text"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              placeholder="e.g., Daily Batch Processing"
              data-testid="job-name-input"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="template-select">Template</label>
            <select
              id="template-select"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              data-testid="template-select"
              className="form-select"
              required
            >
              <option value="">Select a template</option>
              <option value="template-1">Template 1</option>
              <option value="template-2">Template 2</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="schedule-type">Schedule Type</label>
            <select
              id="schedule-type"
              value={scheduleType}
              onChange={(e) => setScheduleType(e.target.value as typeof scheduleType)}
              data-testid="schedule-type-select"
              className="form-select"
            >
              <option value="now">Run Now</option>
              <option value="once">Schedule Once</option>
              <option value="recurring">Recurring (Cron)</option>
            </select>
          </div>

          {scheduleType === 'once' && (
            <div className="form-group">
              <label htmlFor="schedule-time">Date & Time</label>
              <input
                id="schedule-time"
                type="datetime-local"
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                data-testid="schedule-time-input"
                className="form-input"
                required
              />
            </div>
          )}

          {scheduleType === 'recurring' && (
            <div className="form-group">
              <label htmlFor="cron-expression">Cron Expression</label>
              <input
                id="cron-expression"
                type="text"
                value={cronExpression}
                onChange={(e) => setCronExpression(e.target.value)}
                placeholder="0 0 * * * (daily at midnight)"
                data-testid="cron-input"
                className="form-input"
                required
              />
              <small className="help-text">
                Format: minute hour day month weekday (e.g., 0 0 * * * for daily)
              </small>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            data-testid="schedule-submit-btn"
          >
            Schedule Job
          </button>
        </div>
      </div>

      <style>{`
        .modal-overlay {
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
          max-height: 90vh;
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

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }

        .form-group label {
          font-weight: 600;
          font-size: 0.875rem;
        }

        .form-input,
        .form-select {
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-2);
          color: var(--text);
        }

        .form-input:focus,
        .form-select:focus {
          outline: none;
          border-color: var(--accent);
        }

        .help-text {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-top: 0.25rem;
        }

        .error-message {
          background: var(--red-glow);
          color: var(--red);
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          font-size: 0.875rem;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          padding: 1.5rem;
          border-top: 1px solid var(--border);
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

        .btn-primary {
          background: var(--accent);
          color: white;
          border-color: var(--accent);
        }

        .btn-primary:hover {
          background: var(--accent-dark);
        }

        @media (max-width: 768px) {
          .modal-content {
            max-width: 95%;
          }

          .modal-header,
          .modal-body,
          .modal-footer {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  )
}
