import { useState } from 'react'

interface APIKey {
  id: string
  name: string
  key: string
  created_at: string
  last_used?: string
  permissions: string[]
}

export default function APIKeyManager() {
  const [keys, setKeys] = useState<APIKey[]>([
    {
      id: '1',
      name: 'Production Key',
      key: 'sk_live_••••••••••••••••••••••••',
      created_at: '2026-01-15',
      permissions: ['read', 'write'],
    },
  ])
  const [showGenerate, setShowGenerate] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')

  const handleGenerateKey = () => {
    if (!newKeyName.trim()) return
    const newKey: APIKey = {
      id: Date.now().toString(),
      name: newKeyName,
      key: `sk_live_${Math.random().toString(36).slice(2)}`,
      created_at: new Date().toISOString(),
      permissions: ['read', 'write'],
    }
    setKeys([...keys, newKey])
    setNewKeyName('')
    setShowGenerate(false)
  }

  const handleRevokeKey = (id: string) => {
    setKeys((prev) => prev.filter((k) => k.id !== id))
  }

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
  }

  return (
    <div className="api-key-manager" data-testid="api-key-manager">
      <div className="api-header">
        <button
          className="btn btn-primary"
          onClick={() => setShowGenerate(!showGenerate)}
          data-testid="generate-key-btn"
        >
          + Generate New Key
        </button>
      </div>

      {showGenerate && (
        <div className="generate-form" data-testid="generate-form">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Key name"
            data-testid="key-name-input"
            className="form-input"
          />
          <button
            className="btn btn-secondary"
            onClick={handleGenerateKey}
            data-testid="confirm-generate-btn"
          >
            Generate
          </button>
        </div>
      )}

      <div className="keys-list">
        <table className="keys-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Key</th>
              <th>Created</th>
              <th>Permissions</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.id} data-testid={`key-row-${key.id}`}>
                <td>{key.name}</td>
                <td>
                  <code>{key.key}</code>
                </td>
                <td>{new Date(key.created_at).toLocaleDateString()}</td>
                <td>
                  <span className="permissions">
                    {key.permissions.join(', ')}
                  </span>
                </td>
                <td className="actions">
                  <button
                    className="btn-icon"
                    onClick={() => handleCopyKey(key.key)}
                    data-testid={`copy-key-${key.id}`}
                    title="Copy key"
                  >
                    📋
                  </button>
                  <button
                    className="btn-icon btn-danger"
                    onClick={() => handleRevokeKey(key.id)}
                    data-testid={`revoke-key-${key.id}`}
                    title="Revoke key"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style jsx>{`
        .api-key-manager {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .api-header {
          display: flex;
          justify-content: flex-start;
        }

        .generate-form {
          display: flex;
          gap: 0.75rem;
          padding: 1rem;
          background: var(--surface-2);
          border-radius: 4px;
        }

        .form-input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-1);
          color: var(--text);
        }

        .keys-list {
          border: 1px solid var(--border);
          border-radius: 4px;
          overflow: hidden;
        }

        .keys-table {
          width: 100%;
          border-collapse: collapse;
        }

        .keys-table thead {
          background: var(--surface-2);
          border-bottom: 1px solid var(--border);
        }

        .keys-table th {
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          font-size: 0.875rem;
          text-transform: uppercase;
        }

        .keys-table td {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border);
        }

        .keys-table tbody tr:hover {
          background: var(--surface-2);
        }

        .keys-table code {
          background: var(--surface-2);
          padding: 0.25rem 0.5rem;
          border-radius: 3px;
          font-size: 0.85rem;
          font-family: 'Courier New', monospace;
        }

        .permissions {
          font-size: 0.875rem;
          color: var(--text-muted);
        }

        .actions {
          display: flex;
          gap: 0.5rem;
        }

        .btn-icon {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1rem;
          padding: 0.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          border-radius: 3px;
          transition: background 0.2s;
        }

        .btn-icon:hover {
          background: var(--surface-2);
        }

        .btn-icon.btn-danger:hover {
          background: var(--red-glow);
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

        .btn-secondary {
          background: var(--surface-2);
          color: var(--text);
        }

        .btn-secondary:hover {
          background: var(--surface-3);
        }

        @media (max-width: 768px) {
          .generate-form {
            flex-direction: column;
          }

          .keys-table {
            font-size: 0.85rem;
          }

          .keys-table th,
          .keys-table td {
            padding: 0.5rem;
          }
        }
      `}</style>
    </div>
  )
}
