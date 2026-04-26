import { useState } from 'react'

interface Template {
  id?: string
  name: string
  description: string
  version?: number
  status?: 'active' | 'inactive' | 'draft'
  content: Record<string, unknown>
}

interface TemplateEditorProps {
  template: Template | null
  onSave: (template: Partial<Template>) => void
  onClose: () => void
}

export default function TemplateEditor({ template, onSave, onClose }: TemplateEditorProps) {
  const [name, setName] = useState(template?.name || '')
  const [description, setDescription] = useState(template?.description || '')
  const [status, setStatus] = useState(template?.status || 'draft')
  const [jsonContent, setJsonContent] = useState(
    JSON.stringify(template?.content || {}, null, 2)
  )
  const [error, setError] = useState('')

  const handleSave = () => {
    setError('')

    if (!name.trim()) {
      setError('Template name is required')
      return
    }

    try {
      const content = JSON.parse(jsonContent)
      onSave({
        name,
        description,
        status: status as 'active' | 'inactive' | 'draft',
        content,
      })
    } catch {
      setError('Invalid JSON content')
    }
  }

  return (
    <div className="modal-overlay" data-testid="template-editor-modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{template?.id ? 'Edit Template' : 'Create Template'}</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="error-message" data-testid="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="template-name">Template Name</label>
            <input
              id="template-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Worker Template v1"
              data-testid="template-name-input"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="template-description">Description</label>
            <textarea
              id="template-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Template description"
              data-testid="template-description-input"
              className="form-textarea"
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="template-status">Status</label>
            <select
              id="template-status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              data-testid="template-status-select"
              className="form-select"
            >
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="template-json">Template Content (JSON)</label>
            <textarea
              id="template-json"
              value={jsonContent}
              onChange={(e) => setJsonContent(e.target.value)}
              placeholder="{}"
              data-testid="template-json-input"
              className="form-textarea json-editor"
              rows={10}
              spellCheck="false"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            data-testid="save-template-btn"
          >
            Save Template
          </button>
        </div>
      </div>

      <style jsx>{`
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
          max-width: 800px;
          width: 90%;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid var(--border);
        }

        .modal-header h2 {
          margin: 0;
          font-size: 1.25rem;
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

        .modal-body {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          padding: 1.5rem;
          border-top: 1px solid var(--border);
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .form-group label {
          font-weight: 600;
          font-size: 0.875rem;
          color: var(--text);
        }

        .form-input,
        .form-textarea,
        .form-select {
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-2);
          color: var(--text);
          font-family: inherit;
        }

        .form-input:focus,
        .form-textarea:focus,
        .form-select:focus {
          outline: none;
          border-color: var(--accent);
        }

        .json-editor {
          font-family: 'Courier New', monospace;
          font-size: 0.875rem;
        }

        .error-message {
          background: var(--red-glow);
          color: var(--red);
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          font-size: 0.875rem;
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
