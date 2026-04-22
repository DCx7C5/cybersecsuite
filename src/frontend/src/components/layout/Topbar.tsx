import { useUIStore } from '@/store/uiStore'
import { NAV_ITEMS } from '@/constants/nav'
import Button from '@/components/ui/Button'

export default function Topbar() {
  const { activeTab, toggleSidebar, theme, setTheme } = useUIStore()
  const current = NAV_ITEMS.find(i => i.id === activeTab)

  return (
    <header style={{
      height: 'var(--header-h)',
      background: 'var(--bg-deep)',
      borderBottom: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      position: 'sticky',
      top: 0,
      zIndex: 40,
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={toggleSidebar}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: '18px',
            cursor: 'pointer',
            padding: '4px',
          }}
        >
          ☰
        </button>
        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
          {current?.group?.toUpperCase() ?? ''} /
        </span>
        <span style={{ color: 'var(--text-primary)', fontSize: '13px', fontWeight: 500 }}>
          {current?.label ?? activeTab}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {(['blue', 'purple', 'red'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTheme(t)}
            title={`Theme: ${t}`}
            style={{
              width: '16px', height: '16px',
              borderRadius: '50%',
              border: theme === t ? '2px solid var(--text-primary)' : '2px solid transparent',
              background: t === 'blue' ? '#3574f0' : t === 'purple' ? '#a855f7' : '#ef4444',
              cursor: 'pointer',
              padding: 0,
            }}
          />
        ))}
        <Button
          variant="ghost"
          style={{ padding: '4px 8px', fontSize: '12px' }}
          onClick={() => window.location.reload()}
        >
          ↻
        </Button>
      </div>
    </header>
  )
}
