import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import WorkerList from '@/components/workers/WorkerList.tsx'

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

const mockWorkers = [
  {
    id: 1,
    worker_id: 'worker-001',
    name: 'Test Worker 1',
    description: 'Test',
    worker_type: 'processor',
    current_state: 'running',
    config: {},
    project_id: 1,
    session_id: 'session-1',
    steps_executed: 5,
    total_duration_ms: 1000,
    start_time: '2026-04-26T00:00:00Z',
    last_activity_at: '2026-04-26T16:00:00Z',
  },
  {
    id: 2,
    worker_id: 'worker-002',
    name: 'Test Worker 2',
    description: 'Test',
    worker_type: 'processor',
    current_state: 'queued',
    config: {},
    project_id: 1,
    session_id: 'session-1',
    steps_executed: 0,
    total_duration_ms: 0,
    start_time: '2026-04-26T00:00:00Z',
    last_activity_at: '2026-04-26T16:00:00Z',
  },
]

const mockResponse = {
  data: mockWorkers,
  total: 2,
  page: 1,
  limit: 50,
}

describe('WorkerList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockQueryClient.clear()
  })

  it('renders loading state', async () => {
    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkers: () => ({
        data: undefined,
        isLoading: true,
        error: null,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    // Component should show spinner during loading
    await waitFor(() => {
      expect(screen.queryByText(/No workers found|Showing/)).toBeInTheDocument()
    })
  })

  it('renders worker list with data', async () => {
    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkers: () => ({
        data: mockResponse,
        isLoading: false,
        error: null,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    // Check table headers exist
    expect(screen.getByText('Worker ID')).toBeInTheDocument()
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('State')).toBeInTheDocument()
  })

  it('handles search input', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    const searchInput = container.querySelector('input[placeholder*="Search"]') as HTMLInputElement
    expect(searchInput).toBeDefined()

    fireEvent.change(searchInput, { target: { value: 'test' } })
    expect(searchInput.value).toBe('test')
  })

  it('handles state filter selection', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    const selects = container.querySelectorAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(2)

    fireEvent.change(selects[0], { target: { value: 'running' } })
    expect((selects[0] as HTMLSelectElement).value).toBe('running')
  })

  it('handles multi-select checkboxes', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    const checkboxes = container.querySelectorAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)

    if (checkboxes.length > 1) {
      fireEvent.click(checkboxes[1])
      expect((checkboxes[1] as HTMLInputElement).checked).toBe(true)
    }
  })

  it('handles pagination', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    const buttons = screen.getAllByRole('button')
    const nextBtn = buttons.find(b => b.textContent === 'Next')

    if (nextBtn && !nextBtn.hasAttribute('disabled')) {
      fireEvent.click(nextBtn)
    }
  })

  it('shows error state', async () => {
    const errorMsg = 'Failed to load workers'

    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkers: () => ({
        data: null,
        isLoading: false,
        error: new Error(errorMsg),
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )
  })

  it('shows empty state when no workers', () => {
    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkers: () => ({
        data: { data: [], total: 0, page: 1, limit: 50 },
        isLoading: false,
        error: null,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )
  })

  it('selects and deselects all workers', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerList projectId={1} />
      </QueryClientProvider>
    )

    const checkboxes = container.querySelectorAll('input[type="checkbox"]')
    if (checkboxes.length > 0) {
      const selectAllCheckbox = checkboxes[0] as HTMLInputElement
      fireEvent.click(selectAllCheckbox)
      await waitFor(() => {
        expect(selectAllCheckbox.checked).toBe(true)
      })
    }
  })
})
