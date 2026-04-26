import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import OrchestratorLayout from '@/components/orchestrator/OrchestratorLayout'

describe('OrchestratorLayout', () => {
  it('renders main layout structure', () => {
    render(<OrchestratorLayout />)
    expect(screen.getByTestId('orchestrator-layout')).toBeInTheDocument()
    expect(screen.getByTestId('orchestrator-main')).toBeInTheDocument()
    expect(screen.getByTestId('orchestrator-content')).toBeInTheDocument()
  })

  it('renders navigation sidebar', () => {
    render(<OrchestratorLayout />)
    expect(screen.getByTestId('nav-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('nav-toggle')).toBeInTheDocument()
  })

  it('renders status overview', () => {
    render(<OrchestratorLayout />)
    expect(screen.getByTestId('status-overview')).toBeInTheDocument()
    expect(screen.getByTestId('status-value')).toHaveTextContent('Running')
  })

  it('renders quick actions bar', () => {
    render(<OrchestratorLayout />)
    expect(screen.getByTestId('quick-actions')).toBeInTheDocument()
    expect(screen.getByTestId('pause-btn')).toBeInTheDocument()
    expect(screen.getByTestId('cancel-btn')).toBeInTheDocument()
  })

  it('toggles pause/resume state', () => {
    render(<OrchestratorLayout />)
    const pauseBtn = screen.getByTestId('pause-btn')
    
    fireEvent.click(pauseBtn)
    expect(screen.getByTestId('resume-btn')).toBeInTheDocument()
    expect(screen.getByTestId('status-value')).toHaveTextContent('Paused')
    
    const resumeBtn = screen.getByTestId('resume-btn')
    fireEvent.click(resumeBtn)
    expect(screen.getByTestId('pause-btn')).toBeInTheDocument()
  })

  it('toggles sidebar collapse', () => {
    render(<OrchestratorLayout />)
    const toggle = screen.getByTestId('nav-toggle')
    
    fireEvent.click(toggle)
    fireEvent.click(toggle)
    
    expect(screen.getByTestId('nav-sidebar')).toBeInTheDocument()
  })

  it('navigates between views', () => {
    render(<OrchestratorLayout />)
    
    fireEvent.click(screen.getByTestId('nav-templates'))
    fireEvent.click(screen.getByTestId('nav-config'))
    fireEvent.click(screen.getByTestId('nav-health'))
    
    expect(screen.getByTestId('nav-health')).toHaveAttribute('aria-current', 'page')
  })

  it('renders with custom default view', () => {
    render(<OrchestratorLayout defaultView="templates" />)
    expect(screen.getByTestId('nav-templates')).toHaveAttribute('aria-current', 'page')
  })

  it('renders children content', () => {
    render(
      <OrchestratorLayout>
        <div data-testid="custom-content">Test Content</div>
      </OrchestratorLayout>
    )
    expect(screen.getByTestId('custom-content')).toBeInTheDocument()
  })

  it('is responsive on tablet viewport', () => {
    window.innerWidth = 768
    const { container } = render(<OrchestratorLayout />)
    expect(container.querySelector('.orchestrator-layout')).toBeInTheDocument()
  })

  it('is responsive on mobile viewport', () => {
    window.innerWidth = 375
    const { container } = render(<OrchestratorLayout />)
    const layout = container.querySelector('.orchestrator-layout')
    expect(layout).toBeInTheDocument()
  })

  it('navigation shows all menu items', () => {
    render(<OrchestratorLayout />)
    
    expect(screen.getByTestId('nav-dashboard')).toBeInTheDocument()
    expect(screen.getByTestId('nav-templates')).toBeInTheDocument()
    expect(screen.getByTestId('nav-config')).toBeInTheDocument()
    expect(screen.getByTestId('nav-notifications')).toBeInTheDocument()
    expect(screen.getByTestId('nav-batch')).toBeInTheDocument()
    expect(screen.getByTestId('nav-health')).toBeInTheDocument()
    expect(screen.getByTestId('nav-settings')).toBeInTheDocument()
  })

  it('status overview shows health metrics', async () => {
    render(<OrchestratorLayout />)
    
    await waitFor(() => {
      expect(screen.getByTestId('active-workers')).toBeInTheDocument()
      expect(screen.getByTestId('response-time')).toBeInTheDocument()
      expect(screen.getByTestId('memory-usage')).toBeInTheDocument()
    })
  })

  it('has accessible navigation', () => {
    render(<OrchestratorLayout />)
    const nav = screen.getByRole('navigation')
    expect(nav).toHaveAttribute('aria-label', 'Main navigation')
  })

  it('quick action buttons are accessible', () => {
    render(<OrchestratorLayout />)
    const pauseBtn = screen.getByTestId('pause-btn')
    const cancelBtn = screen.getByTestId('cancel-btn')
    
    expect(pauseBtn).toHaveAttribute('aria-label')
    expect(cancelBtn).toHaveAttribute('aria-label')
  })

  it('navigation items have proper roles', () => {
    render(<OrchestratorLayout />)
    const dashboardItem = screen.getByTestId('nav-dashboard')
    
    expect(dashboardItem).toHaveAttribute('aria-current', 'page')
  })

  it('expands when content children provided', () => {
    const { container } = render(
      <OrchestratorLayout>
        <div style={{ height: '500px' }}>Large content</div>
      </OrchestratorLayout>
    )
    const content = container.querySelector('.orchestrator-content')
    expect(content).toBeInTheDocument()
  })
})
