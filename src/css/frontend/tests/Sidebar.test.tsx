import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Sidebar from '../Sidebar'

// Mock the store
vi.mock('@/store/uiStore', () => ({
  useUIStore: () => ({
    activeTab: 'dashboard',
    setActiveTab: vi.fn(),
    sidebarCollapsed: false,
  }),
}))

// Mock constants
vi.mock('@/constants/nav', () => ({
  NAV_ITEMS: [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', group: 'main' },
    { id: 'forensics', label: 'Forensics', icon: '🔍', group: 'main' },
    { id: 'settings', label: 'Settings', icon: '⚙️', group: 'settings' },
  ],
  NAV_GROUPS: {
    main: 'Main',
    settings: 'Settings',
  },
}))

describe('Sidebar Component - t074: Collapse State', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should render sidebar with initial state', () => {
    render(<Sidebar />)
    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
  })

  it('should persist collapse state to localStorage', async () => {
    render(<Sidebar />)
    const button = screen.getByTestId('nav-group-toggle-main')
    
    fireEvent.click(button)
    await waitFor(() => {
      const stored = localStorage.getItem('sidebar-dropdowns')
      expect(stored).toBeTruthy()
    })
  })

  it('should restore collapse state from localStorage', () => {
    localStorage.setItem('sidebar-dropdowns', JSON.stringify({ main: false }))
    render(<Sidebar />)
    
    const items = screen.queryAllByTestId(/nav-item-/)
    expect(items).toHaveLength(0)
  })

  it('should have smooth transition when collapsing', () => {
    const { container } = render(<Sidebar />)
    const aside = container.querySelector('aside')
    expect(aside).toHaveStyle('transition: left 0.25s ease')
  })
})

describe('Sidebar Component - t092: Dropdown Functionality', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should toggle dropdown groups', async () => {
    render(<Sidebar />)
    const toggle = screen.getByTestId('nav-group-toggle-main')
    
    expect(screen.queryByTestId('nav-item-dashboard')).toBeInTheDocument()
    
    fireEvent.click(toggle)
    await waitFor(() => {
      expect(screen.queryByTestId('nav-item-dashboard')).not.toBeInTheDocument()
    })

    fireEvent.click(toggle)
    await waitFor(() => {
      expect(screen.queryByTestId('nav-item-dashboard')).toBeInTheDocument()
    })
  })

  it('should display correct dropdown indicator icon', async () => {
    render(<Sidebar />)
    const toggle = screen.getByTestId('nav-group-toggle-main')
    
    expect(toggle).toHaveTextContent('▾')
    
    fireEvent.click(toggle)
    await waitFor(() => {
      expect(toggle).toHaveTextContent('▸')
    })
  })

  it('should animate dropdown icon rotation', () => {
    render(<Sidebar />)
    const toggle = screen.getByTestId('nav-group-toggle-main')
    const icon = toggle.querySelector('span:last-child')
    
    expect(icon).toHaveStyle('transition: transform 0.2s')
  })

  it('should maintain dropdown state for multiple groups', async () => {
    render(<Sidebar />)
    const settingsToggle = screen.getByTestId('settings-toggle')
    
    fireEvent.click(settingsToggle)
    await waitFor(() => {
      expect(screen.getByTestId('settings-item-settings')).toBeInTheDocument()
    })

    const mainToggle = screen.getByTestId('nav-group-toggle-main')
    fireEvent.click(mainToggle)
    
    expect(screen.getByTestId('settings-item-settings')).toBeInTheDocument()
  })
})

describe('Sidebar Component - t094: Component Isolation', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should isolate dropdown state per group', async () => {
    render(<Sidebar />)
    
    const mainToggle = screen.getByTestId('nav-group-toggle-main')
    fireEvent.click(mainToggle)
    
    expect(screen.getByTestId('settings-item-settings')).toBeInTheDocument()
  })

  it('should not leak state between instances', async () => {
    const { unmount } = render(<Sidebar />)
    const toggle = screen.getByTestId('nav-group-toggle-main')
    fireEvent.click(toggle)
    
    unmount()
    
    const { container: container2 } = render(<Sidebar />)
    const toggle2 = container2.querySelector('[data-testid="nav-group-toggle-main"]')
    expect(toggle2).toHaveTextContent('▸')
  })

  it('should handle rapid state changes', async () => {
    render(<Sidebar />)
    const toggle = screen.getByTestId('nav-group-toggle-main')
    
    fireEvent.click(toggle)
    fireEvent.click(toggle)
    fireEvent.click(toggle)
    
    await waitFor(() => {
      expect(screen.getByTestId('nav-item-dashboard')).toBeInTheDocument()
    })
  })

  it('should manage click event isolation', async () => {
    const user = userEvent.setup()
    render(<Sidebar />)
    
    const mainItem = screen.getByTestId('nav-item-dashboard')
    const toggle = screen.getByTestId('nav-group-toggle-main')
    
    await user.click(toggle)
    await user.click(mainItem)
    
    expect(screen.getByTestId('nav-item-dashboard')).toBeInTheDocument()
  })

  it('should maintain isolation with settings dropdown', async () => {
    render(<Sidebar />)
    
    const settingsToggle = screen.getByTestId('settings-toggle')
    fireEvent.click(settingsToggle)
    
    const mainToggle = screen.getByTestId('nav-group-toggle-main')
    expect(screen.getByTestId('nav-item-dashboard')).toBeInTheDocument()
    
    fireEvent.click(mainToggle)
    expect(screen.getByTestId('settings-item-settings')).toBeInTheDocument()
  })
})
