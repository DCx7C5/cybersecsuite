import { useState } from 'react'
import ThemeSelector from './ThemeSelector'
import APIKeyManager from './APIKeyManager'

interface UserProfile {
  username: string
  email: string
  joined_date: string
}

export default function UserSettings() {
  const [profile] = useState<UserProfile>({
    username: 'admin',
    email: 'admin@orchestrator.local',
    joined_date: '2026-01-15',
  })
  const [activeTab, setActiveTab] = useState<'account' | 'preferences' | 'api-keys' | 'export'>(
    'account'
  )
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [smsNotifications, setSmsNotifications] = useState(false)
  const [inAppNotifications, setInAppNotifications] = useState(true)

  const handleExportCSV = () => {
    const data = 'User Data Export\nusername,email,joined_date\n'
    const url = URL.createObjectURL(new Blob([data], { type: 'text/csv' }))
    const a = document.createElement('a')
    a.href = url
    a.download = 'user-data.csv'
    a.click()
  }

  const handleExportJSON = () => {
    const data = {
      user: profile,
      exported_at: new Date().toISOString(),
    }
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    )
    const a = document.createElement('a')
    a.href = url
    a.download = 'user-data.json'
    a.click()
  }

  return (
    <div className="user-settings" data-testid="user-settings">
      <div className="settings-header">
        <h1>User Settings & Preferences</h1>
      </div>

      <div className="settings-tabs">
        <button
          className={`tab-btn ${activeTab === 'account' ? 'active' : ''}`}
          onClick={() => setActiveTab('account')}
          data-testid="tab-account"
        >
          Account
        </button>
        <button
          className={`tab-btn ${activeTab === 'preferences' ? 'active' : ''}`}
          onClick={() => setActiveTab('preferences')}
          data-testid="tab-preferences"
        >
          Preferences
        </button>
        <button
          className={`tab-btn ${activeTab === 'api-keys' ? 'active' : ''}`}
          onClick={() => setActiveTab('api-keys')}
          data-testid="tab-api-keys"
        >
          API Keys
        </button>
        <button
          className={`tab-btn ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
          data-testid="tab-export"
        >
          Export Data
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'account' && (
          <div className="settings-panel" data-testid="account-panel">
            <h2>Account Information</h2>
            <table className="profile-table">
              <tbody>
                <tr>
                  <td className="label">Username</td>
                  <td className="value" data-testid="username-value">
                    {profile.username}
                  </td>
                </tr>
                <tr>
                  <td className="label">Email</td>
                  <td className="value" data-testid="email-value">
                    {profile.email}
                  </td>
                </tr>
                <tr>
                  <td className="label">Joined</td>
                  <td className="value" data-testid="joined-value">
                    {new Date(profile.joined_date).toLocaleDateString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'preferences' && (
          <div className="settings-panel" data-testid="preferences-panel">
            <h2>Notification Preferences</h2>
            <ThemeSelector />
            <div className="preference-group">
              <div className="preference-item">
                <input
                  type="checkbox"
                  id="email-notif"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  data-testid="email-notif-toggle"
                />
                <label htmlFor="email-notif">Email Notifications</label>
              </div>
              <div className="preference-item">
                <input
                  type="checkbox"
                  id="sms-notif"
                  checked={smsNotifications}
                  onChange={(e) => setSmsNotifications(e.target.checked)}
                  data-testid="sms-notif-toggle"
                />
                <label htmlFor="sms-notif">SMS Notifications</label>
              </div>
              <div className="preference-item">
                <input
                  type="checkbox"
                  id="inapp-notif"
                  checked={inAppNotifications}
                  onChange={(e) => setInAppNotifications(e.target.checked)}
                  data-testid="inapp-notif-toggle"
                />
                <label htmlFor="inapp-notif">In-App Notifications</label>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'api-keys' && (
          <div className="settings-panel" data-testid="api-keys-panel">
            <h2>API Key Management</h2>
            <APIKeyManager />
          </div>
        )}

        {activeTab === 'export' && (
          <div className="settings-panel" data-testid="export-panel">
            <h2>Export Data</h2>
            <div className="export-options">
              <button
                className="btn btn-secondary"
                onClick={handleExportCSV}
                data-testid="export-csv-btn"
              >
                📥 Export as CSV
              </button>
              <button
                className="btn btn-secondary"
                onClick={handleExportJSON}
                data-testid="export-json-btn"
              >
                📥 Export as JSON
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .user-settings {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .settings-header h1 {
          margin: 0;
        }

        .settings-tabs {
          display: flex;
          gap: 0.5rem;
          border-bottom: 1px solid var(--border);
          flex-wrap: wrap;
        }

        .tab-btn {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-muted);
          transition: all 0.2s;
        }

        .tab-btn:hover {
          color: var(--text);
        }

        .tab-btn.active {
          color: var(--accent);
          border-bottom-color: var(--accent);
        }

        .settings-content {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .settings-panel {
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 1.5rem;
          background: var(--surface-1);
        }

        .settings-panel h2 {
          margin: 0 0 1.5rem 0;
          font-size: 1.125rem;
        }

        .profile-table {
          width: 100%;
          border-collapse: collapse;
        }

        .profile-table tr {
          border-bottom: 1px solid var(--border);
        }

        .profile-table td {
          padding: 1rem;
        }

        .profile-table .label {
          font-weight: 600;
          width: 150px;
          background: var(--surface-2);
        }

        .preference-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .preference-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .preference-item input[type='checkbox'] {
          cursor: pointer;
          width: 18px;
          height: 18px;
        }

        .preference-item label {
          cursor: pointer;
          font-size: 0.875rem;
        }

        .export-options {
          display: flex;
          gap: 1rem;
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
          .settings-tabs {
            overflow-x: auto;
          }

          .tab-btn {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
          }

          .profile-table td {
            padding: 0.75rem;
          }

          .export-options {
            flex-direction: column;
          }

          .export-options button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
