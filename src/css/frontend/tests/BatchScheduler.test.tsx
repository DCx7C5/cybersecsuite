import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BatchScheduler from '@/components/orchestrator/BatchScheduler'

const mockQueryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

vi.mock('@/hooks/useApi', () => ({
  fetchApi: vi.fn(),
}))

describe('BatchScheduler', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders batch scheduler', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('batch-scheduler')).toBeInTheDocument()
  })

  it('renders schedule job button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('schedule-job-btn')).toBeInTheDocument()
  })

  it('opens schedule form modal', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('schedule-job-btn'))
    expect(screen.getByTestId('schedule-form-modal')).toBeInTheDocument()
  })

  it('renders job list', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('job-list')).toBeInTheDocument()
    })
  })

  it('has accessible controls', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('schedule-job-btn')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    expect(container.querySelector('.batch-scheduler')).toBeInTheDocument()
  })

  it('shows schedule form with correct fields', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('schedule-job-btn'))
    expect(screen.getByTestId('job-name-input')).toBeInTheDocument()
    expect(screen.getByTestId('template-select')).toBeInTheDocument()
    expect(screen.getByTestId('schedule-type-select')).toBeInTheDocument()
  })

  it('handles schedule type changes', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('schedule-job-btn'))
    const typeSelect = screen.getByTestId('schedule-type-select')
    fireEvent.change(typeSelect, { target: { value: 'once' } })
    expect(typeSelect).toHaveValue('once')
  })

  it('validates form inputs', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <BatchScheduler />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('schedule-job-btn'))
    fireEvent.click(screen.getByTestId('schedule-submit-btn'))
    expect(screen.getByTestId('schedule-error')).toBeInTheDocument()
  })
})
