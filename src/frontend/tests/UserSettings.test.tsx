import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import UserSettings from '@/components/orchestrator/UserSettings'

describe('UserSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders user settings', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('user-settings')).toBeInTheDocument()
  })

  it('renders account tab', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('tab-account')).toBeInTheDocument()
  })

  it('renders preferences tab', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('tab-preferences')).toBeInTheDocument()
  })

  it('renders api-keys tab', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('tab-api-keys')).toBeInTheDocument()
  })

  it('renders export tab', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('tab-export')).toBeInTheDocument()
  })

  it('displays account information by default', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('account-panel')).toBeInTheDocument()
  })

  it('shows username', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('username-value')).toBeInTheDocument()
  })

  it('shows email', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('email-value')).toBeInTheDocument()
  })

  it('shows joined date', () => {
    render(<UserSettings />)
    expect(screen.getByTestId('joined-value')).toBeInTheDocument()
  })

  it('switches to preferences tab', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-preferences'))
    expect(screen.getByTestId('preferences-panel')).toBeInTheDocument()
  })

  it('switches to api-keys tab', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-api-keys'))
    expect(screen.getByTestId('api-keys-panel')).toBeInTheDocument()
  })

  it('switches to export tab', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-export'))
    expect(screen.getByTestId('export-panel')).toBeInTheDocument()
  })

  it('has export csv button', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-export'))
    expect(screen.getByTestId('export-csv-btn')).toBeInTheDocument()
  })

  it('has export json button', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-export'))
    expect(screen.getByTestId('export-json-btn')).toBeInTheDocument()
  })

  it('has theme selector', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-preferences'))
    expect(screen.getByTestId('theme-selector')).toBeInTheDocument()
  })

  it('has notification preference toggles', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-preferences'))
    expect(screen.getByTestId('email-notif-toggle')).toBeInTheDocument()
    expect(screen.getByTestId('sms-notif-toggle')).toBeInTheDocument()
    expect(screen.getByTestId('inapp-notif-toggle')).toBeInTheDocument()
  })

  it('has api key manager', () => {
    render(<UserSettings />)
    fireEvent.click(screen.getByTestId('tab-api-keys'))
    expect(screen.getByTestId('api-key-manager')).toBeInTheDocument()
  })

  it('is responsive', () => {
    const { container } = render(<UserSettings />)
    expect(container.querySelector('.user-settings')).toBeInTheDocument()
  })
})
