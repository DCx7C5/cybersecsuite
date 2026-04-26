import { NAV_ITEMS, NAV_GROUPS } from '@/constants/nav'
import { useUIStore } from '@/store/uiStore'
import { useState, useEffect } from 'react'

export default function Sidebar() {
  const { activeTab, setActiveTab, sidebarCollapsed } = useUIStore()
  const [settingsOpen, setSettingsOpen] = useState<boolean>(() => {
    const saved = localStorage.getItem('sidebar-settings-open')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    localStorage.setItem('sidebar-settings-open', JSON.stringify(settingsOpen))
  }, [settingsOpen])

  const groups = Object.entries(NAV_GROUPS)
  const settingsItems = NAV_ITEMS.filter(i => i.group === 'settings')

  return (
    <aside
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
        {groups.map(([groupId, groupLabel]) => {
          if (groupId === 'settings') return null
          const items = NAV_ITEMS.filter((i) => i.group === groupId)
          return (
            <div key={groupId} data-testid={`nav-group-${groupId}`}>
              {groupLabel && (
                <div
                  style={{
                    padding: '8px 12px 4px',
                    fontSize: '10px',
                    fontWeight: 700,
                    color: 'var(--text-faint)',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                  }}
                >
                  {groupLabel}
                </div>
              )}
              {items.map((item) => (
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
            }}
          >
            <span>SETTINGS</span>
            <span style={{ fontSize: '10px' }}>{settingsOpen ? '▾' : '▸'}</span>
          </button>
          {settingsOpen &&
            settingsItems.map((item) => (
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
