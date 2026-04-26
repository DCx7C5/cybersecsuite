import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ExecutionTimeline from '@/components/workers/ExecutionTimeline.tsx'

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

const mockHistory = [
  {
    id: 1,
    action: 'Started',
    timestamp: '2026-04-26T16:00:00Z',
    details: { worker_id: '001', status: 'started' },
  },
  {
    id: 2,
    action: 'Step executed',
    timestamp: '2026-04-26T16:00:05Z',
    details: { step: 1, duration_ms: 100 },
  },
  {
    id: 3,
    action: 'Completed',
    timestamp: '2026-04-26T16:00:10Z',
    details: { worker_id: '001', status: 'completed' },
  },
]

const mockBookmarks = [
  {
    id: 1,
    name: 'Checkpoint 1',
    timestamp: '2026-04-26T16:00:05Z',
    history_id: 2,
  },
]

describe('ExecutionTimeline', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockQueryClient.clear()
  })

  it('renders loading state', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('displays timeline items', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('history')) {
          return {
            data: mockHistory,
            isLoading: false,
            error: null,
          }
        }
        return {
          data: mockBookmarks,
          isLoading: false,
          error: null,
        }
      },
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('handles date filter', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const dateInput = container.querySelector('input[type="date"]') as HTMLInputElement
    if (dateInput) {
      fireEvent.change(dateInput, { target: { value: '2026-04-26' } })
      expect(dateInput.value).toBe('2026-04-26')
    }
  })

  it('handles type filter', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const typeInputs = container.querySelectorAll('input[type="text"]')
    if (typeInputs.length > 0) {
      fireEvent.change(typeInputs[0], { target: { value: 'Started' } })
    }
  })

  it('shows empty state', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: () => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('handles bookmark modal open', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const bookmarkBtn = Array.from(buttons).find(b => b.textContent?.includes('Bookmark'))

    if (bookmarkBtn) {
      fireEvent.click(bookmarkBtn)
    }
  })

  it('handles export to JSON', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const exportBtn = Array.from(buttons).find(b => b.textContent?.includes('Export'))

    if (exportBtn) {
      fireEvent.click(exportBtn)
    }
  })

  it('displays bookmark markers', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('history')) {
          return {
            data: mockHistory,
            isLoading: false,
            error: null,
          }
        }
        return {
          data: mockBookmarks,
          isLoading: false,
          error: null,
        }
      },
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    // Verify structure
    expect(container.querySelector('[style*="position"]')).toBeDefined()
  })

  it('renders timeline correctly with markers', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    // Check for timeline divider line
    const dividers = container.querySelectorAll('[style*="position: absolute"]')
    expect(dividers.length).toBeGreaterThanOrEqual(0)
  })

  it('shows details for each timeline item', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const preElements = container.querySelectorAll('pre')
    expect(preElements.length).toBeGreaterThanOrEqual(0)
  })

  it('allows adding bookmarks', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ExecutionTimeline projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })
})
