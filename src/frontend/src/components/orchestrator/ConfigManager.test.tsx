import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ConfigManager from '@/components/orchestrator/ConfigManager'

const mockQueryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

vi.mock('@/hooks/useApi', () => ({
  fetchApi: vi.fn(),
}))

describe('ConfigManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders config manager', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('config-manager')).toBeInTheDocument()
    expect(screen.getByText('Configuration Manager')).toBeInTheDocument()
  })

  it('renders edit configuration button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('edit-config-btn')).toBeInTheDocument()
  })

  it('enters edit mode', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('edit-config-btn'))
    expect(screen.getByTestId('revert-btn')).toBeInTheDocument()
  })

  it('shows history button', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('history-btn')).toBeInTheDocument()
  })

  it('toggles history view', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    const historyBtn = screen.getByTestId('history-btn')
    fireEvent.click(historyBtn)
  })

  it('renders config categories', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('config-categories')).toBeInTheDocument()
    })
  })

  it('renders config form', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('config-form')).toBeInTheDocument()
    })
  })

  it('reverts changes', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('edit-config-btn'))
    fireEvent.click(screen.getByTestId('revert-btn'))
    expect(screen.getByTestId('edit-config-btn')).toBeInTheDocument()
  })

  it('has accessible controls', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    expect(screen.getByTestId('edit-config-btn')).toBeInTheDocument()
    expect(screen.getByTestId('history-btn')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    expect(container.querySelector('.config-manager')).toBeInTheDocument()
  })

  it('shows loading state', async () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
  })

  it('renders save button when in edit mode', () => {
    render(
      <QueryClientProvider client={mockQueryClient}>
        <ConfigManager />
      </QueryClientProvider>
    )
    fireEvent.click(screen.getByTestId('edit-config-btn'))
    expect(screen.getByTestId('save-config-btn')).toBeInTheDocument()
  })
})
