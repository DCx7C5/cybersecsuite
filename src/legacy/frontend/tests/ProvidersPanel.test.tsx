import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ProvidersPanel from '@/features/platform/ProvidersPanel'

const useApiQueryMock = vi.fn()
const fetchApiMock = vi.fn()

vi.mock('@/hooks/useApi', () => ({
  useApiQuery: (...args: unknown[]) => useApiQueryMock(...args),
  fetchApi: (...args: unknown[]) => fetchApiMock(...args),
}))

vi.mock('@/features/platform/ProviderAuthModal', () => ({
  default: ({ open, provider }: { open: boolean; provider: { name?: string } | null }) => (
    open ? <div data-testid="provider-auth-modal">{provider?.name ?? 'Unknown Provider'}</div> : null
  ),
}))

function renderPanel() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <ProvidersPanel />
    </QueryClientProvider>
  )
}

describe('ProvidersPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetchApiMock.mockResolvedValue({ ok: true })
    useApiQueryMock.mockReturnValue({
      data: {
        providers: [
          {
            id: 'openai',
            name: 'OpenAI',
            status: 'available',
            auth_type: 'api_key',
            enabled: true,
            models_count: 10,
            auth_methods: [{ auth_method: 'api_key', config: {} }],
            accounts: [],
          },
          {
            id: 'anthropic',
            name: 'Anthropic',
            status: 'available',
            auth_type: 'api_key',
            enabled: true,
            models_count: 6,
            auth_methods: [{ auth_method: 'api_key', config: {} }],
            accounts: [
              {
                account_id: 'anthropic-1',
                vault_key: 'anthropic-1',
                label: 'Work account',
                auth_method: 'api_key',
                active: true,
                test_status: 'untested',
              },
            ],
          },
        ],
      },
      isLoading: false,
      error: null,
    })
  })

  it('renders providers and actions', () => {
    renderPanel()
    expect(screen.getByText('OpenAI')).toBeInTheDocument()
    expect(screen.getByText('Anthropic')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Add Account' })).toBeInTheDocument()
  })

  it('opens auth modal when sign in is clicked', () => {
    renderPanel()
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))
    expect(screen.getByTestId('provider-auth-modal')).toHaveTextContent('OpenAI')
  })

  it('toggles provider enabled state', async () => {
    renderPanel()
    const toggleButtons = screen.getAllByRole('button', { name: /ON|OFF/ })
    fireEvent.click(toggleButtons[0])

    await waitFor(() => {
      expect(fetchApiMock).toHaveBeenCalledWith(
        '/api/providers/openai',
        expect.objectContaining({ method: 'PATCH' })
      )
    })
  })

  it('revokes an account from actions column', async () => {
    renderPanel()
    fireEvent.click(screen.getByRole('button', { name: 'Revoke' }))

    await waitFor(() => {
      expect(fetchApiMock).toHaveBeenCalledWith(
        '/api/providers/anthropic/auth/revoke',
        expect.objectContaining({ method: 'POST' })
      )
    })
  })
})
