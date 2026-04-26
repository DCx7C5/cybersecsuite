import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { NotificationProvider } from '@/context/NotificationContext'
import NotificationCenter from '@/components/orchestrator/NotificationCenter'

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <NotificationProvider>{children}</NotificationProvider>
)

describe('NotificationCenter', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders notification center', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('notification-center')).toBeInTheDocument()
  })

  it('renders preferences button', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('preferences-btn')).toBeInTheDocument()
  })

  it('renders history button', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('history-btn')).toBeInTheDocument()
  })

  it('renders clear all button', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('clear-all-btn')).toBeInTheDocument()
  })

  it('shows active notifications section', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('active-notifications')).toBeInTheDocument()
  })

  it('toggles preferences panel', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    fireEvent.click(screen.getByTestId('preferences-btn'))
    expect(screen.getByTestId('alert-preferences')).toBeInTheDocument()
  })

  it('toggles history view', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    fireEvent.click(screen.getByTestId('history-btn'))
    expect(screen.getByTestId('notification-history')).toBeInTheDocument()
  })

  it('has accessible controls', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByTestId('preferences-btn')).toBeInTheDocument()
    expect(screen.getByTestId('history-btn')).toBeInTheDocument()
    expect(screen.getByTestId('clear-all-btn')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(container.querySelector('.notification-center')).toBeInTheDocument()
  })

  it('shows empty state when no notifications', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByText('No active notifications')).toBeInTheDocument()
  })

  it('shows notification count', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    expect(screen.getByText(/Active Notifications \(0\)/)).toBeInTheDocument()
  })

  it('renders alert preferences panel', () => {
    render(
      <TestWrapper>
        <NotificationCenter />
      </TestWrapper>
    )
    fireEvent.click(screen.getByTestId('preferences-btn'))
    expect(screen.getByText('Alert Preferences')).toBeInTheDocument()
  })
})

import { vi } from 'vitest'
