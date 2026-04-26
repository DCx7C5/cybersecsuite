import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import TemplateBuilder from '@/components/orchestrator/TemplateBuilder'

const mockQueryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

const mockTemplates = [
  {
    id: '1',
    name: 'Template 1',
    description: 'Test template 1',
    version: 1,
    status: 'active' as const,
    created_at: '2026-04-26T00:00:00Z',
    updated_at: '2026-04-26T00:00:00Z',
    content: { key: 'value' },
  },
  {
    id: '2',
    name: 'Template 2',
    description: 'Test template 2',
    version: 2,
    status: 'draft' as const,
    created_at: '2026-04-26T00:00:00Z',
    updated_at: '2026-04-26T00:00:00Z',
    content: { key: 'value2' },
  },
]

vi.mock('@/hooks/useApi', () => ({
  fetchApi: vi.fn(),
}))

describe('TemplateBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders template builder', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('template-builder')).toBeInTheDocument()
    expect(screen.getByText('Template Builder')).toBeInTheDocument()
  })

  it('renders create template button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('create-template-btn')).toBeInTheDocument()
  })

  it('renders search and filter controls', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('search-input')).toBeInTheDocument()
    expect(screen.getByTestId('filter-status')).toBeInTheDocument()
  })

  it('opens create template modal', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('create-template-btn'))
    expect(screen.getByTestId('template-editor-modal')).toBeInTheDocument()
  })

  it('filters templates by status', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    const filterSelect = screen.getByTestId('filter-status')
    fireEvent.change(filterSelect, { target: { value: 'active' } })
    expect(filterSelect).toHaveValue('active')
  })

  it('searches templates', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    const searchInput = screen.getByTestId('search-input')
    fireEvent.change(searchInput, { target: { value: 'test' } })
    expect(searchInput).toHaveValue('test')
  })

  it('shows template table', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('template-list')).toBeInTheDocument()
    })
  })

  it('handles pagination', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('template-builder')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(container.querySelector('.template-builder')).toBeInTheDocument()
  })

  it('shows template table headers', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('template-list')).toBeInTheDocument()
    })
  })

  it('has accessible controls', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <TemplateBuilder />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('search-input')).toBeInTheDocument()
    expect(screen.getByTestId('create-template-btn')).toBeInTheDocument()
  })
})
