interface Config {
  category: string
  key: string
  value: unknown
  description: string
  type: 'string' | 'number' | 'boolean' | 'array'
  required: boolean
}

interface ConfigFormProps {
  config: Config[]
  isEditMode: boolean
  changes: Record<string, unknown>
  onChange: (key: string, value: unknown) => void
}

export default function ConfigForm({
  config,
  isEditMode,
  changes,
  onChange,
}: ConfigFormProps) {
  return (
    <div className="config-form" data-testid="config-form">
      <table className="config-table">
        <tbody>
          {config.map((item) => {
            const currentValue = changes[item.key] !== undefined ? changes[item.key] : item.value
            return (
              <tr key={item.key} data-testid={`config-row-${item.key}`}>
                <td className="config-key-cell">
                  <div className="config-key">{item.key}</div>
                  <div className="config-description">{item.description}</div>
                </td>
                <td className="config-value-cell">
                  {isEditMode ? (
                    <input
                      type={item.type === 'number' ? 'number' : 'text'}
                      value={String(currentValue || '')}
                      onChange={(e) =>
                        onChange(
                          item.key,
                          item.type === 'number' ? Number(e.target.value) : e.target.value
                        )
                      }
                      data-testid={`config-input-${item.key}`}
                      className="config-input"
                      required={item.required}
                    />
                  ) : (
                    <div className="config-display" data-testid={`config-value-${item.key}`}>
                      {String(currentValue)}
                    </div>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <style jsx>{`
        .config-form {
          padding: 1.5rem;
        }

        .config-table {
          width: 100%;
          border-collapse: collapse;
        }

        .config-table tbody tr {
          border-bottom: 1px solid var(--border);
        }

        .config-table tbody tr:last-child {
          border-bottom: none;
        }

        .config-key-cell,
        .config-value-cell {
          padding: 1rem;
          text-align: left;
        }

        .config-key-cell {
          width: 40%;
          vertical-align: top;
        }

        .config-key {
          font-weight: 600;
          color: var(--text);
          font-family: 'Courier New', monospace;
          margin-bottom: 0.25rem;
        }

        .config-description {
          font-size: 0.875rem;
          color: var(--text-muted);
          margin-top: 0.25rem;
        }

        .config-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-1);
          color: var(--text);
        }

        .config-input:focus {
          outline: none;
          border-color: var(--accent);
        }

        .config-display {
          padding: 0.5rem;
          background: var(--surface-1);
          border-radius: 4px;
          font-family: 'Courier New', monospace;
          word-break: break-all;
        }

        @media (max-width: 768px) {
          .config-table tbody,
          .config-table tbody tr,
          .config-table tbody td {
            display: block;
            width: 100%;
          }

          .config-key-cell,
          .config-value-cell {
            width: 100%;
            padding: 0.75rem 0;
          }

          .config-key-cell {
            margin-bottom: 0.5rem;
          }
        }
      `}</style>
    </div>
  )
}
