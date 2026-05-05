import { NAV_ITEMS, NAV_GROUPS } from '@/constants/nav'
import { useUIStore } from '@/store/uiStore'
import { useState, useEffect, useRef, useCallback } from 'react'

interface DropdownState {
  [key: string]: boolean
}

export default function Sidebar() {
  const { activeTab, setActiveTab, sidebarCollapsed } = useUIStore()
  const [settingsOpen, setSettingsOpen] = useState<boolean>(() => {
    const saved = localStorage.getItem('sidebar-settings-open')
    return saved ? JSON.parse(saved) : false
  })
  const [dropdowns, setDropdowns] = useState<DropdownState>(() => {
    const saved = localStorage.getItem('sidebar-dropdowns')
    return saved ? JSON.parse(saved) : {}
  })
  const sidebarRef = useRef<HTMLElement>(null)

  useEffect(() => {
    localStorage.setItem('sidebar-settings-open', JSON.stringify(settingsOpen))
  }, [settingsOpen])

  useEffect(() => {
    localStorage.setItem('sidebar-dropdowns', JSON.stringify(dropdowns))
  }, [dropdowns])

  const toggleDropdown = useCallback((groupId: string) => {
    setDropdowns(prev => ({ ...prev, [groupId]: !prev[groupId] }))
  }, [])

  return (
    <aside
      ref={sidebarRef}
      data-testid="sidebar"
      style={{
        position: 'fixed',
        left: sidebarCollapsed ? 'calc(-1 * var(--sidebar-w))' : '0',
        top: 0,
        width: 'var(--sidebar-w)',
        height: '100vh',
        background: 'var(--bg-deep)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'left 0.25s ease',
        zIndex: 50,
        overflowY: 'auto',
        overflowX: 'hidden',
      }}
    >
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border)' }}>
        <div
          style={{
            fontWeight: 700,
            fontSize: '14px',
            color: 'var(--text-primary)',
            letterSpacing: '0.05em',
          }}
        >
          CyberSecSuite
        </div>
        <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '2px' }}>
          forensic intelligence platform
        </div>
      </div>

      <nav style={{ flex: 1, padding: '8px 0' }}>
        {Object.entries(NAV_GROUPS).map(([groupId, groupLabel]) => {
          if (groupId === 'settings') return null
          const items = NAV_ITEMS.filter((i) => i.group === groupId)
          const isOpen = dropdowns[groupId]
          return (
            <div key={groupId} data-testid={`nav-group-${groupId}`}>
              {groupLabel && (
                <button
                  data-testid={`nav-group-toggle-${groupId}`}
                  onClick={() => toggleDropdown(groupId)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px 4px',
                    fontSize: '10px',
                    fontWeight: 700,
                    color: 'var(--text-faint)',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'color 0.15s',
                  }}
                >
                  <span>{groupLabel}</span>
                  <span style={{ fontSize: '10px', transform: isOpen ? 'rotate(0deg)' : 'rotate(-90deg)', transition: 'transform 0.2s' }}>▾</span>
                </button>
              )}
              {isOpen && items.map((item) => (
                <button
                  key={item.id}
                  data-testid={`nav-item-${item.id}`}
                  onClick={() => setActiveTab(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '7px 12px',
                    background: activeTab === item.id ? 'var(--accent-glow)' : 'transparent',
                    border: 'none',
                    borderLeft:
                      activeTab === item.id ? '2px solid var(--accent)' : '2px solid transparent',
                    color: activeTab === item.id ? 'var(--accent)' : 'var(--text-muted)',
                    fontSize: '13px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                  }}
                >
                  <span style={{ fontSize: '14px', minWidth: '18px' }}>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          )
        })}

        <div>
          <button
            data-testid="settings-toggle"
            onClick={() => setSettingsOpen((o) => !o)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px 4px',
              background: 'transparent',
              border: 'none',
              fontSize: '10px',
              fontWeight: 700,
              color: 'var(--text-faint)',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              transition: 'color 0.15s',
            }}
          >
            <span>SETTINGS</span>
            <span style={{ fontSize: '10px', transform: settingsOpen ? 'rotate(0deg)' : 'rotate(-90deg)', transition: 'transform 0.2s' }}>▾</span>
          </button>
          {settingsOpen &&
            NAV_ITEMS.filter(i => i.group === 'settings').map((item) => (
              <button
                key={item.id}
                data-testid={`settings-item-${item.id}`}
                onClick={() => setActiveTab(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '7px 12px',
                  background: activeTab === item.id ? 'var(--accent-glow)' : 'transparent',
                  border: 'none',
                  borderLeft:
                    activeTab === item.id ? '2px solid var(--accent)' : '2px solid transparent',
                  color: activeTab === item.id ? 'var(--accent)' : 'var(--text-muted)',
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s',
                }}
              >
                <span style={{ fontSize: '14px', minWidth: '18px' }}>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
        </div>
      </nav>
    </aside>
  )
}
