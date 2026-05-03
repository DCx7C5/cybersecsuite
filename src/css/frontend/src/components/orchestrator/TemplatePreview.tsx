interface Template {
  id?: string
  name: string
  description: string
  version?: number
  status?: string
  content: Record<string, unknown>
}

interface TemplatePreviewProps {
  template: Template
  onClose: () => void
}

export default function TemplatePreview({ template, onClose }: TemplatePreviewProps) {
  return (
    <div className="modal-overlay" data-testid="template-preview-modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Template Preview</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="preview-section">
            <h3>Name</h3>
            <p data-testid="preview-name">{template.name}</p>
          </div>

          <div className="preview-section">
            <h3>Description</h3>
            <p data-testid="preview-description">{template.description}</p>
          </div>

          {template.version && (
            <div className="preview-section">
              <h3>Version</h3>
              <p data-testid="preview-version">{template.version}</p>
            </div>
          )}

          {template.status && (
            <div className="preview-section">
              <h3>Status</h3>
              <span
                className={`status-badge status-${template.status}`}
                data-testid="preview-status"
              >
                {template.status}
              </span>
            </div>
          )}

          <div className="preview-section">
            <h3>Content</h3>
            <pre className="json-content" data-testid="preview-content">
              {JSON.stringify(template.content, null, 2)}
            </pre>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
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

        .preview-section {
          margin-bottom: 1.5rem;
        }

        .preview-section h3 {
          font-size: 0.875rem;
          text-transform: uppercase;
          color: var(--text-muted);
          margin: 0 0 0.5rem 0;
          letter-spacing: 0.5px;
        }

        .preview-section p {
          margin: 0;
          font-size: 1rem;
          color: var(--text);
        }

        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .status-active {
          background: var(--success-glow);
          color: var(--success);
        }

        .status-inactive {
          background: var(--amber-glow);
          color: var(--amber);
        }

        .status-draft {
          background: var(--accent-glow);
          color: var(--accent);
        }

        .json-content {
          background: var(--surface-2);
          border: 1px solid var(--border);
          border-radius: 4px;
          padding: 1rem;
          overflow-x: auto;
          font-family: 'Courier New', monospace;
          font-size: 0.85rem;
          margin: 0;
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
