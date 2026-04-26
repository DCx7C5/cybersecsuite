import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import ConfigForm from './ConfigForm'
import ConfigHistory from './ConfigHistory'

interface Config {
  category: string
  key: string
  value: unknown
  description: string
  type: 'string' | 'number' | 'boolean' | 'array'
  required: boolean
}

interface ConfigResponse {
  system: Config[]
  performance: Config[]
  security: Config[]
  logging: Config[]
  api: Config[]
}

interface ConfigHistoryEntry {
  timestamp: string
  user: string
  action: 'created' | 'updated' | 'deleted'
  config_key: string
  old_value: unknown
  new_value: unknown
}

export default function ConfigManager() {
  const [isEditMode, setIsEditMode] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [changes, setChanges] = useState<Record<string, unknown>>({})

  const { data: config, isLoading, refetch } = useQuery({
    queryKey: ['config'],
    queryFn: () => fetchApi<ConfigResponse>('/api/config'),
  })

  const { data: history } = useQuery({
    queryKey: ['config-history'],
    queryFn: () => fetchApi<ConfigHistoryEntry[]>('/api/config/history'),
  })

  const updateConfigMutation = useMutation({
    mutationFn: (updates: Record<string, unknown>) =>
      fetchApi('/api/config/update', {
        method: 'POST',
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      refetch()
      setChanges({})
      setIsEditMode(false)
    },
  })

  const handleSave = () => {
    updateConfigMutation.mutate(changes)
  }

  const handleRevert = () => {
    setChanges({})
    setIsEditMode(false)
  }

  const handleChange = (key: string, value: unknown) => {
    setChanges((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  if (isLoading) {
    return <div data-testid="config-manager-loading">Loading configuration...</div>
  }

  const categories = [
    { key: 'system', label: 'System Settings', icon: '🖥️' },
    { key: 'performance', label: 'Performance', icon: '⚡' },
    { key: 'security', label: 'Security', icon: '🔒' },
    { key: 'logging', label: 'Logging', icon: '📝' },
    { key: 'api', label: 'API Settings', icon: '🌐' },
  ] as const

  return (
    <div className="config-manager" data-testid="config-manager">
      <div className="config-header">
        <h1>Configuration Manager</h1>
        <div className="config-actions">
          {!isEditMode && (
            <button
              className="btn btn-primary"
              onClick={() => setIsEditMode(true)}
              data-testid="edit-config-btn"
            >
              Edit Configuration
            </button>
          )}
          {isEditMode && (
            <>
              <button
                className="btn btn-secondary"
                onClick={handleRevert}
                data-testid="revert-btn"
              >
                Revert
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                data-testid="save-config-btn"
                disabled={Object.keys(changes).length === 0}
              >
                Save Changes
              </button>
            </>
          )}
          <button
            className="btn btn-secondary"
            onClick={() => setShowHistory(!showHistory)}
            data-testid="history-btn"
          >
            {showHistory ? 'Hide' : 'Show'} History
          </button>
        </div>
      </div>

      {showHistory && history && (
        <ConfigHistory entries={history} />
      )}

      <div className="config-categories" data-testid="config-categories">
        {categories.map((category) => {
          const categoryConfig = config?.[category.key as keyof ConfigResponse] || []
          return (
            <div key={category.key} className="config-category">
              <div className="category-header">
                <h2>
                  <span className="category-icon">{category.icon}</span>
                  {category.label}
                </h2>
              </div>
              <ConfigForm
                config={categoryConfig}
                isEditMode={isEditMode}
                changes={changes}
                onChange={handleChange}
              />
            </div>
          )
        })}
      </div>

      <style jsx>{`
        .config-manager {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .config-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .config-actions {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .config-categories {
          display: grid;
          gap: 1.5rem;
        }

        .config-category {
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
        }

        .category-header {
          background: var(--surface-2);
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--border);
        }

        .category-header h2 {
          margin: 0;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 1.125rem;
        }

        .category-icon {
          font-size: 1.5rem;
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

        .btn-primary:hover:not(:disabled) {
          background: var(--accent-dark);
        }

        .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: var(--surface-2);
          color: var(--text);
        }

        .btn-secondary:hover {
          background: var(--surface-3);
        }

        @media (max-width: 768px) {
          .config-header {
            flex-direction: column;
            align-items: stretch;
          }

          .config-actions {
            flex-direction: column;
          }

          .config-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
