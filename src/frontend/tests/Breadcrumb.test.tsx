import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Breadcrumb from '../Breadcrumb'

describe('Breadcrumb Component - t113: Navigation Breadcrumb', () => {
  it('should render breadcrumb items', () => {
    const items = [
      { label: 'Home', href: '/' },
      { label: 'Cases', href: '/cases' },
      { label: 'Case 123' },
    ]
    render(<Breadcrumb items={items} />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Cases')).toBeInTheDocument()
    expect(screen.getByText('Case 123')).toBeInTheDocument()
  })

  it('should render separator between items', () => {
    const items = [
      { label: 'Home' },
      { label: 'Dashboard' },
    ]
    const { container } = render(<Breadcrumb items={items} />)

    const separators = container.querySelectorAll('[style*="var(--text-faint)"]')
    expect(separators.length).toBeGreaterThan(0)
  })

  it('should support custom separator', () => {
    const items = [
      { label: 'Home' },
      { label: 'Dashboard' },
    ]
    const { container } = render(<Breadcrumb items={items} separator="→" />)

    expect(container.textContent).toContain('→')
  })

  it('should render clickable items with href', () => {
    const items = [
      { label: 'Home', href: '/' },
      { label: 'Dashboard', href: '/dashboard' },
    ]
    render(<Breadcrumb items={items} />)

    const homeLink = screen.getByText('Home') as HTMLAnchorElement
    expect(homeLink.href).toContain('/')
  })

  it('should call onClick handler for clickable items', () => {
    const handleClick = vi.fn()
    const items = [
      { label: 'Home', onClick: handleClick },
      { label: 'Dashboard' },
    ]
    render(<Breadcrumb items={items} />)

    const homeButton = screen.getByText('Home')
    fireEvent.click(homeButton)

    expect(handleClick).toHaveBeenCalled()
  })

  it('should render icons', () => {
    const items = [
      { label: 'Home', icon: '🏠' },
      { label: 'Dashboard', icon: '📊' },
    ]
    const { container } = render(<Breadcrumb items={items} />)

    expect(container.textContent).toContain('🏠')
    expect(container.textContent).toContain('📊')
  })

  it('should handle long breadcrumb trails with maxItems', () => {
    const items = [
      { label: 'Home' },
      { label: 'Cases' },
      { label: 'Case 123' },
      { label: 'Evidence' },
      { label: 'File' },
      { label: 'Deep Item' },
    ]
    render(<Breadcrumb items={items} maxItems={4} />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('...')).toBeInTheDocument()
    expect(screen.getByText('Deep Item')).toBeInTheDocument()
  })

  it('should not collapse when items less than maxItems', () => {
    const items = [
      { label: 'Home' },
      { label: 'Dashboard' },
    ]
    render(<Breadcrumb items={items} maxItems={5} />)

    expect(screen.queryByText('...')).not.toBeInTheDocument()
  })

  it('should apply accessibility attributes', () => {
    const items = [
      { label: 'Home', href: '/' },
      { label: 'Dashboard' },
    ]
    const { container } = render(<Breadcrumb items={items} />)

    const nav = container.querySelector('[aria-label="Breadcrumb"]')
    expect(nav).toBeInTheDocument()
  })

  it('should handle items without onClick gracefully', () => {
    const items = [
      { label: 'Home' },
      { label: 'Dashboard' },
    ]
    render(<Breadcrumb items={items} />)

    const dashboard = screen.getByText('Dashboard')
    expect(() => fireEvent.click(dashboard)).not.toThrow()
  })

  it('should render last item as non-clickable by default', () => {
    const items = [
      { label: 'Home', href: '/' },
      { label: 'Dashboard', href: '/dashboard' },
      { label: 'Current Page' },
    ]
    render(<Breadcrumb items={items} />)

    const currentPage = screen.getByText('Current Page')
    expect(currentPage.tagName).not.toBe('A')
  })
})
