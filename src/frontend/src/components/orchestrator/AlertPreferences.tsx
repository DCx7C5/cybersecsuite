import { useState } from 'react'
import { useNotifications } from '@/hooks/useNotifications'

interface AlertPreference {
  enabled: boolean
  sound: boolean
  email: boolean
}

interface NotificationPreferences {
  success: AlertPreference
  error: AlertPreference
  warning: AlertPreference
  info: AlertPreference
}

interface AlertPreferencesProps {
  onClose: () => void
}

const defaultPreferences: NotificationPreferences = {
  success: { enabled: true, sound: false, email: false },
  error: { enabled: true, sound: true, email: true },
  warning: { enabled: true, sound: false, email: false },
  info: { enabled: true, sound: false, email: false },
}

export default function AlertPreferences({ onClose }: AlertPreferencesProps) {
  useNotifications()
  const [preferences, setPreferences] = useState<NotificationPreferences>(defaultPreferences)

  const handleToggle = (type: keyof NotificationPreferences, key: keyof AlertPreference) => {
    setPreferences((prev) => ({
      ...prev,
      [type]: {
        ...prev[type],
        [key]: !prev[type][key],
      },
    }))
  }

  const handleSave = () => {
    localStorage.setItem('notification-preferences', JSON.stringify(preferences))
    success('Preferences saved successfully')
    onClose()
  }

  const types: Array<keyof NotificationPreferences> = ['success', 'error', 'warning', 'info']

  return (
    <div className="alert-preferences" data-testid="alert-preferences">
      <div className="preferences-header">
        <h3>Alert Preferences</h3>
        <button className="close-btn" onClick={onClose} aria-label="Close">
          ✕
        </button>
      </div>

      <div className="preferences-body">
        <table className="preferences-table">
          <thead>
            <tr>
              <th>Alert Type</th>
              <th>Enabled</th>
              <th>Sound</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {types.map((type) => (
              <tr key={type} data-testid={`preference-row-${type}`}>
                <td className="type-cell">
                  <span className={`type-badge type-${type}`}>{type}</span>
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={preferences[type].enabled}
                    onChange={() => handleToggle(type, 'enabled')}
                    data-testid={`toggle-enabled-${type}`}
                    aria-label={`Enable ${type} notifications`}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={preferences[type].sound}
                    onChange={() => handleToggle(type, 'sound')}
                    data-testid={`toggle-sound-${type}`}
                    aria-label={`Enable sound for ${type} notifications`}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={preferences[type].email}
                    onChange={() => handleToggle(type, 'email')}
                    data-testid={`toggle-email-${type}`}
                    aria-label={`Enable email for ${type} notifications`}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="preferences-footer">
        <button className="btn btn-secondary" onClick={onClose}>
          Cancel
        </button>
        <button className="btn btn-primary" onClick={handleSave} data-testid="save-preferences-btn">
          Save Preferences
        </button>
      </div>

      <style jsx>{`
        .alert-preferences {
          background: var(--surface-1);
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .preferences-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--border);
          background: var(--surface-2);
        }

        .preferences-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          font-size: 1.5rem;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .close-btn:hover {
          color: var(--text);
        }

        .preferences-body {
          padding: 1.5rem;
        }

        .preferences-table {
          width: 100%;
          border-collapse: collapse;
        }

        .preferences-table thead {
          background: var(--surface-2);
          border-bottom: 1px solid var(--border);
        }

        .preferences-table th {
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          font-size: 0.875rem;
          text-transform: uppercase;
        }

        .preferences-table td {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border);
          text-align: center;
        }

        .type-cell {
          text-align: left;
        }

        .type-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .type-success {
          background: var(--success-glow);
          color: var(--success);
        }

        .type-error {
          background: var(--red-glow);
          color: var(--red);
        }

        .type-warning {
          background: var(--amber-glow);
          color: var(--amber);
        }

        .type-info {
          background: var(--accent-glow);
          color: var(--accent);
        }

        .preferences-table input[type='checkbox'] {
          cursor: pointer;
          width: 18px;
          height: 18px;
        }

        .preferences-footer {
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
          .preferences-header,
          .preferences-body,
          .preferences-footer {
            padding: 1rem;
          }

          .preferences-table {
            font-size: 0.85rem;
          }

          .preferences-table th,
          .preferences-table td {
            padding: 0.5rem;
          }
        }
      `}</style>
    </div>
  )
}
