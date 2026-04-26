import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AnalyticsDashboard from '@/components/orchestrator/AnalyticsDashboard'

const mockQueryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

vi.mock('@/hooks/useApi', () => ({
  fetchApi: vi.fn(),
}))

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders analytics dashboard', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('analytics-dashboard')).toBeInTheDocument()
  })

  it('renders date range filter', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('date-range-select')).toBeInTheDocument()
  })

  it('renders worker type filter', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('worker-type-select')).toBeInTheDocument()
  })

  it('renders state filter', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('state-select')).toBeInTheDocument()
  })

  it('displays success rate metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('success-rate-metric')).toBeInTheDocument()
  })

  it('displays average runtime metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('avg-runtime-metric')).toBeInTheDocument()
  })

  it('displays throughput metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('throughput-metric')).toBeInTheDocument()
  })

  it('displays total executions metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('total-executions-metric')).toBeInTheDocument()
  })

  it('renders metrics charts', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('metrics-charts')).toBeInTheDocument()
  })

  it('has export csv button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('export-csv-btn')).toBeInTheDocument()
  })

  it('has export json button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('export-json-btn')).toBeInTheDocument()
  })

  it('handles date range change', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    const select = screen.getByTestId('date-range-select')
    fireEvent.change(select, { target: { value: '30d' } })
    expect(select).toHaveValue('30d')
  })

  it('is responsive', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )
    expect(container.querySelector('.analytics-dashboard')).toBeInTheDocument()
  })
})
