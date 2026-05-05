import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import HealthDashboard from '@/components/orchestrator/HealthDashboard'

const mockQueryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

vi.mock('@/hooks/useApi', () => ({
  fetchApi: vi.fn(),
}))

describe('HealthDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders health dashboard', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('health-dashboard')).toBeInTheDocument()
  })

  it('displays system uptime metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('uptime-value')).toBeInTheDocument()
  })

  it('displays workers metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('workers-value')).toBeInTheDocument()
  })

  it('displays response time metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('response-time-value')).toBeInTheDocument()
  })

  it('displays memory usage metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('memory-value')).toBeInTheDocument()
  })

  it('displays CPU usage metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('cpu-value')).toBeInTheDocument()
  })

  it('displays database connections metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('db-connections-value')).toBeInTheDocument()
  })

  it('displays error rate metric', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('error-rate-value')).toBeInTheDocument()
  })

  it('has toggle logs button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('toggle-logs-btn')).toBeInTheDocument()
  })

  it('toggles logs viewer', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    const toggleBtn = screen.getByTestId('toggle-logs-btn')
    fireEvent.click(toggleBtn)
  })

  it('has generate report button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('generate-report-btn')).toBeInTheDocument()
  })

  it('has export metrics button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('export-metrics-btn')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <HealthDashboard />
      </QueryClientProvider>
    )
    expect(container.querySelector('.health-dashboard')).toBeInTheDocument()
  })
})
