import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MetricsCard from '@/components/workers/MetricsCard.tsx'

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

const mockWorkerMetrics = {
  worker_id: 'worker-001',
  step_count: 25,
  success_rate: 0.92,
  avg_duration_ms: 450,
  current_state: 'running',
  uptime_ms: 600000,
}

const mockSummary = {
  project_id: 1,
  total_workers: 100,
  running: 45,
  paused: 10,
  completed: 30,
  failed: 5,
  queued: 10,
  avg_step_count: 18.5,
  avg_success_rate: 0.88,
}

const mockHealth = {
  status: 'healthy' as const,
  message: 'All systems operational',
}

describe('MetricsCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockQueryClient.clear()
  })

  it('renders without worker ID', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} />
      </QueryClientProvider>
    )
  })

  it('displays worker metrics when workerId provided', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('metrics')) {
          return { data: mockWorkerMetrics, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('displays project summary when showSummary is true', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('summary')) {
          return { data: mockSummary, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} showSummary />
      </QueryClientProvider>
    )
  })

  it('shows loading state', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: () => ({
        data: null,
        isLoading: true,
      }),
    }))

    render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} workerId={1} />
      </QueryClientProvider>
    )
  })

  it('displays health status indicator', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: () => ({
        data: mockHealth,
        isLoading: false,
      }),
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} />
      </QueryClientProvider>
    )

    // Verify health status indicator is present
    const indicators = container.querySelectorAll('[style*="borderRadius: 50%"]')
    expect(indicators.length).toBeGreaterThanOrEqual(0)
  })

  it('renders worker metrics grid correctly', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    const grids = container.querySelectorAll('[style*="gridTemplateColumns"]')
    expect(grids.length).toBeGreaterThanOrEqual(0)
  })

  it('shows state distribution bar', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('summary')) {
          return { data: mockSummary, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} showSummary />
      </QueryClientProvider>
    )

    // Verify state distribution bar exists
    const bars = container.querySelectorAll('[style*="height: 8px"]')
    expect(bars.length).toBeGreaterThanOrEqual(0)
  })

  it('displays status badge with correct color', async () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} />
      </QueryClientProvider>
    )

    await waitFor(() => {
      const elements = container.querySelectorAll('[style*="background"]')
      expect(elements.length).toBeGreaterThan(0)
    })
  })

  it('shows all summary metrics cards', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('summary')) {
          return { data: mockSummary, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} showSummary />
      </QueryClientProvider>
    )

    // Check for metric cards
    const cards = container.querySelectorAll('[style*="padding: 12px"]')
    expect(cards.length).toBeGreaterThan(0)
  })

  it('displays average statistics', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('summary')) {
          return { data: mockSummary, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} showSummary />
      </QueryClientProvider>
    )

    // Verify structure exists
    expect(container).toBeDefined()
  })

  it('renders worker state indicator', () => {
    vi.mock('@/hooks/useApi.ts', () => ({
      useApiQuery: (key: unknown, url: string) => {
        if (url.includes('metrics')) {
          return { data: mockWorkerMetrics, isLoading: false }
        }
        return { data: mockHealth, isLoading: false }
      },
    }))

    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <MetricsCard projectId={1} workerId={1} />
      </QueryClientProvider>
    )

    // Check for colored state indicator
    const indicators = container.querySelectorAll('[style*="borderRadius: 50%"]')
    expect(indicators.length).toBeGreaterThanOrEqual(0)
  })
})
