import { useState, useEffect } from 'react'
import { useNotifications, type Notification } from '@/hooks/useNotifications'
import AlertPreferences from './AlertPreferences'

export default function NotificationCenter() {
  const { notifications, clearAll, remove } = useNotifications()
  const [showHistory, setShowHistory] = useState(false)
  const [showPreferences, setShowPreferences] = useState(false)
  const [history, setHistory] = useState<Notification[]>([])

  useEffect(() => {
    setHistory((prev) => {
      const newNotifications = notifications.filter((n) => !prev.find((h) => h.id === n.id))
      if (newNotifications.length === 0) return prev
      const updated = [...prev, ...newNotifications]
      return updated.slice(-50)
    })
  }, [notifications])

  const getIcon = (type: string) => {
    const icons: Record<string, string> = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ⓘ',
    }
    return icons[type] || '•'
  }

  const getColor = (type: string) => {
    const colors: Record<string, string> = {
      success: 'var(--success)',
      error: 'var(--red)',
      warning: 'var(--amber)',
      info: 'var(--accent)',
    }
    return colors[type] || 'var(--text)'
  }

  return (
    <div className="notification-center" data-testid="notification-center">
      <div className="notification-header">
        <h2>Notifications & Alerts</h2>
        <div className="notification-actions">
          <button
            className="btn btn-small"
            onClick={() => setShowPreferences(!showPreferences)}
            data-testid="preferences-btn"
          >
            ⚙️ Preferences
          </button>
          <button
            className="btn btn-small"
            onClick={() => setShowHistory(!showHistory)}
            data-testid="history-btn"
          >
            📋 History
          </button>
          <button
            className="btn btn-small"
            onClick={clearAll}
            data-testid="clear-all-btn"
            disabled={notifications.length === 0}
          >
            Clear All
          </button>
        </div>
      </div>

      {showPreferences && (
        <AlertPreferences onClose={() => setShowPreferences(false)} />
      )}

      <div className="active-notifications" data-testid="active-notifications">
        <h3>Active Notifications ({notifications.length})</h3>
        {notifications.length === 0 ? (
          <div className="empty-state">No active notifications</div>
        ) : (
          <div className="notification-list">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                className={`notification notification-${notif.type}`}
                data-testid={`notification-${notif.id}`}
                style={{ borderLeftColor: getColor(notif.type) }}
              >
                <span className="notification-icon">{getIcon(notif.type)}</span>
                <div className="notification-content">
                  <p className="notification-message">{notif.message}</p>
                  <span className="notification-time">
                    {new Date(notif.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <button
                  className="notification-close"
                  onClick={() => remove(notif.id)}
                  aria-label="Dismiss notification"
                  data-testid={`close-notification-${notif.id}`}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showHistory && (
        <div className="notification-history" data-testid="notification-history">
          <h3>History (Last 50)</h3>
          {history.length === 0 ? (
            <div className="empty-state">No notification history</div>
          ) : (
            <div className="history-list">
              {history
                .slice()
                .reverse()
                .map((notif) => (
                  <div
                    key={notif.id}
                    className={`history-item history-${notif.type}`}
                    data-testid={`history-item-${notif.id}`}
                  >
                    <span className="history-icon">{getIcon(notif.type)}</span>
                    <div className="history-content">
                      <p>{notif.message}</p>
                      <span className="history-time">
                        {new Date(notif.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <span className={`history-type history-type-${notif.type}`}>
                      {notif.type}
                    </span>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      <style>{`
        .notification-center {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .notification-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .notification-actions {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .btn-small {
          padding: 0.4rem 0.8rem;
          font-size: 0.875rem;
          border: 1px solid var(--border);
          background: var(--surface-2);
          color: var(--text);
          cursor: pointer;
          border-radius: 4px;
          transition: all 0.2s;
        }

        .btn-small:hover:not(:disabled) {
          background: var(--surface-3);
        }

        .btn-small:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .active-notifications,
        .notification-history {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .active-notifications h3,
        .notification-history h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
        }

        .notification-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .notification {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          border-left: 4px solid var(--border);
          background: var(--surface-2);
          border-radius: 4px;
          animation: slideIn 0.3s ease;
        }

        .notification-icon {
          font-size: 1.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 1.5rem;
        }

        .notification-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .notification-message {
          margin: 0;
          font-weight: 500;
        }

        .notification-time {
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .notification-close {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          font-size: 1rem;
          padding: 0.25rem;
          min-width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .notification-close:hover {
          color: var(--text);
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          max-height: 400px;
          overflow-y: auto;
        }

        .history-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 0.75rem;
          background: var(--surface-2);
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .history-icon {
          font-size: 1rem;
          min-width: 1.25rem;
          text-align: center;
        }

        .history-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.2rem;
        }

        .history-content p {
          margin: 0;
        }

        .history-time {
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .history-type {
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .history-type-success {
          background: var(--success-glow);
          color: var(--success);
        }

        .history-type-error {
          background: var(--red-glow);
          color: var(--red);
        }

        .history-type-warning {
          background: var(--amber-glow);
          color: var(--amber);
        }

        .history-type-info {
          background: var(--accent-glow);
          color: var(--accent);
        }

        .empty-state {
          text-align: center;
          padding: 2rem;
          color: var(--text-muted);
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .notification-header {
            flex-direction: column;
            align-items: stretch;
          }

          .notification-actions {
            flex-direction: column;
          }

          .notification-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
