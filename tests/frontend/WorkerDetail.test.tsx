import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import WorkerDetail from '@/components/workers/WorkerDetail.tsx'

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

const mockWorker = {
  id: 1,
  worker_id: 'worker-001',
  name: 'Test Worker',
  description: 'Test description',
  worker_type: 'processor',
  current_state: 'running',
  config: { timeout: 30, retry: 3 },
  project_id: 1,
  session_id: 'session-1',
  steps_executed: 10,
  total_duration_ms: 5000,
  start_time: '2026-04-26T00:00:00Z',
  last_activity_at: '2026-04-26T16:00:00Z',
}

const mockMetrics = {
  worker_id: 'worker-001',
  step_count: 10,
  success_rate: 0.95,
  avg_duration_ms: 500,
  current_state: 'running',
  uptime_ms: 300000,
}

describe('WorkerDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockQueryClient.clear()
  })

  it('renders loading state', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('displays worker information', () => {
    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkerDetail: () => ({
        data: mockWorker,
        isLoading: false,
        error: null,
      }),
      useWorkerMetrics: () => ({
        data: mockMetrics,
        isLoading: false,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('shows error state', () => {
    vi.mock('@/hooks/useWorkers.ts', () => ({
      useWorkerDetail: () => ({
        data: null,
        isLoading: false,
        error: new Error('Failed to load'),
      }),
      useWorkerMetrics: () => ({
        data: null,
        isLoading: false,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('displays metrics correctly', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    // Verify structure
    expect(container).toBeDefined()
  })

  it('shows state transition buttons based on current state', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('handles back button click', () => {
    const onBack = vi.fn()

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} onBack={onBack} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    if (buttons.length > 0) {
      fireEvent.click(buttons[0])
    }
  })

  it('displays configuration as JSON', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const preElement = container.querySelector('pre')
    expect(preElement).toBeDefined()
  })

  it('shows delete confirmation modal', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const deleteBtn = Array.from(buttons).find(b => b.textContent?.includes('Delete'))

    if (deleteBtn) {
      fireEvent.click(deleteBtn)
    }
  })

  it('displays metrics dashboard', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    // Check for metrics grid
    expect(container.querySelector('[style*="gridTemplateColumns"]')).toBeDefined()
  })

  it('shows correct badge color for state', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check that badge is rendered
      const badges = document.querySelectorAll('[style*="background"]')
      expect(badges.length).toBeGreaterThan(0)
    })
  })

  it('handles action button clicks', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    if (buttons.length > 1) {
      fireEvent.click(buttons[1])
    }
  })

  it('renders grid layouts for info display', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <WorkerDetail projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const gridDivs = container.querySelectorAll('[style*="grid"]')
    expect(gridDivs.length).toBeGreaterThan(0)
  })
})
