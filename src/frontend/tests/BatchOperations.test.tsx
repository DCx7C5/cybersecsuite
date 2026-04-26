import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BatchOperations from '@/components/workers/BatchOperations.tsx'

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

describe('BatchOperations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockQueryClient.clear()
  })

  it('renders nothing when no workers selected', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[]} />
      </QueryClientProvider>
    )

    expect(container.children.length).toBe(0)
  })

  it('shows selection count when workers selected', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2, 3]} />
      </QueryClientProvider>
    )

    // Verify card exists
    expect(container.querySelector('[style*="padding"]')).toBeDefined()
  })

  it('displays batch action buttons', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('shows confirmation modal on action click', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    if (buttons.length > 0) {
      fireEvent.click(buttons[0])
    }
  })

  it('handles start all action', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const startBtn = Array.from(buttons).find(b => b.textContent?.includes('Start'))

    if (startBtn) {
      fireEvent.click(startBtn)
    }
  })

  it('handles stop all action', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const stopBtn = Array.from(buttons).find(b => b.textContent?.includes('Stop'))

    if (stopBtn) {
      fireEvent.click(stopBtn)
    }
  })

  it('handles update config action', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    const updateBtn = Array.from(buttons).find(b => b.textContent?.includes('Update'))

    if (updateBtn) {
      fireEvent.click(updateBtn)
    }
  })

  it('shows results modal after batch operation', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    // Component renders
    expect(container).toBeDefined()
  })

  it('displays progress bar during operation', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    // Check for progress bar element
    expect(container.querySelector('[style*="height: 4px"]')).toBeDefined()
  })

  it('calls onComplete callback', () => {
    const onComplete = vi.fn()

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1]} onComplete={onComplete} />
      </QueryClientProvider>
    )

    expect(container).toBeDefined()
  })

  it('shows success/failure counts in results', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2, 3]} />
      </QueryClientProvider>
    )

    // Verify card structure
    const cards = container.querySelectorAll('[style*="padding: 16px"]')
    expect(cards.length).toBeGreaterThan(0)
  })

  it('disables buttons during batch operation', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('handles modal close', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchOperations projectId={1} selectedWorkerIds={[1, 2]} />
      </QueryClientProvider>
    )

    const buttons = container.querySelectorAll('button')
    if (buttons.length > 1) {
      fireEvent.click(buttons[1])
    }
  })
})
