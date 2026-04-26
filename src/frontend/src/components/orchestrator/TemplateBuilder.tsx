import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import TemplateEditor from './TemplateEditor'
import TemplatePreview from './TemplatePreview'

interface Template {
  id: string
  name: string
  description: string
  version: number
  created_at: string
  updated_at: string
  status: 'active' | 'inactive' | 'draft'
  content: Record<string, unknown>
}

interface TemplatesResponse {
  data: Template[]
  total: number
  page: number
  limit: number
}

export default function TemplateBuilder() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'draft'>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  const { data: templatesData, isLoading, refetch } = useQuery({
    queryKey: ['templates', page, search, filterStatus],
    queryFn: () => {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('limit', '10')
      if (search) params.append('search', search)
      if (filterStatus !== 'all') params.append('status', filterStatus)
      return fetchApi<TemplatesResponse>(`/api/templates?${params.toString()}`)
    },
  })

  const updateTemplateMutation = useMutation({
    mutationFn: (data: { id: string; template: Partial<Template> }) =>
      fetchApi(`/api/templates/${data.id}`, {
        method: 'PUT',
        body: JSON.stringify(data.template),
      }),
    onSuccess: () => refetch(),
  })

  const createTemplateMutation = useMutation({
    mutationFn: (template: Partial<Template>) =>
      fetchApi('/api/templates', {
        method: 'POST',
        body: JSON.stringify(template),
      }),
    onSuccess: () => {
      refetch()
      setShowCreate(false)
    },
  })

  return (
    <div className="template-builder" data-testid="template-builder">
      <div className="template-header">
        <h1>Template Builder</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreate(true)}
          data-testid="create-template-btn"
        >
          + New Template
        </button>
      </div>

      <div className="template-controls">
        <input
          type="text"
          placeholder="Search templates..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setPage(1)
          }}
          data-testid="search-input"
          className="search-input"
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as typeof filterStatus)}
          data-testid="filter-status"
          className="filter-select"
        >
          <option value="all">All Templates</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="draft">Draft</option>
        </select>
      </div>

      <div className="template-list" data-testid="template-list">
        {isLoading ? (
          <div className="loading">Loading templates...</div>
        ) : templatesData?.data.length === 0 ? (
          <div className="empty-state">No templates found</div>
        ) : (
          <table className="templates-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Version</th>
                <th>Status</th>
                <th>Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {templatesData?.data.map((template) => (
                <tr key={template.id} data-testid={`template-row-${template.id}`}>
                  <td>{template.name}</td>
                  <td>{template.version}</td>
                  <td>
                    <span className={`status-badge status-${template.status}`}>
                      {template.status}
                    </span>
                  </td>
                  <td>{new Date(template.updated_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button
                      className="btn-small"
                      onClick={() => setSelectedTemplate(template)}
                      data-testid={`edit-${template.id}`}
                    >
                      Edit
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => {
                        setSelectedTemplate(template)
                        setShowPreview(true)
                      }}
                      data-testid={`preview-${template.id}`}
                    >
                      Preview
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {templatesData && templatesData.total > 10 && (
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
            disabled={page >= Math.ceil(templatesData.total / 10)}
            data-testid="next-page"
          >
            Next
          </button>
        </div>
      )}

      {selectedTemplate && !showCreate && (
        <TemplateEditor
          template={selectedTemplate}
          onSave={(updated) => {
            updateTemplateMutation.mutate({ id: selectedTemplate.id, template: updated })
            setSelectedTemplate(null)
          }}
          onClose={() => setSelectedTemplate(null)}
        />
      )}

      {showPreview && selectedTemplate && (
        <TemplatePreview
          template={selectedTemplate}
          onClose={() => {
            setShowPreview(false)
            setSelectedTemplate(null)
          }}
        />
      )}

      {showCreate && (
        <TemplateEditor
          template={null}
          onSave={(template) => {
            createTemplateMutation.mutate(template)
          }}
          onClose={() => setShowCreate(false)}
        />
      )}

      <style jsx>{`
        .template-builder {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .template-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .template-controls {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .search-input,
        .filter-select {
          padding: 0.5rem;
          border: 1px solid var(--border);
          border-radius: 4px;
          background: var(--surface-1);
          color: var(--text);
        }

        .search-input {
          flex: 1;
          min-width: 200px;
        }

        .template-list {
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
        }

        .templates-table {
          width: 100%;
          border-collapse: collapse;
        }

        .templates-table thead {
          background: var(--surface-2);
          border-bottom: 1px solid var(--border);
        }

        .templates-table th,
        .templates-table td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid var(--border);
        }

        .templates-table tbody tr:hover {
          background: var(--surface-1);
        }

        .status-badge {
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

        .actions {
          display: flex;
          gap: 0.5rem;
        }

        .btn-small {
          padding: 0.4rem 0.8rem;
          font-size: 0.75rem;
          border: 1px solid var(--border);
          background: var(--surface-2);
          color: var(--text);
          cursor: pointer;
          border-radius: 3px;
        }

        .btn-small:hover {
          background: var(--surface-3);
        }

        .pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 1rem;
        }

        .loading,
        .empty-state {
          padding: 2rem;
          text-align: center;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .template-controls {
            flex-direction: column;
          }

          .search-input {
            min-width: 100%;
          }

          .templates-table {
            font-size: 0.85rem;
          }

          .templates-table th,
          .templates-table td {
            padding: 0.5rem;
          }
        }
      `}</style>
    </div>
  )
}
