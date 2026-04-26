import { ReactNode } from 'react'

interface NavSection {
  label: string
  icon: string
  view: string
  items?: NavItem[]
}

interface NavItem {
  label: string
  view: string
  icon: string
}

interface NavigationProps {
  currentView: string
  onViewChange: (view: string) => void
  collapsed: boolean
  onCollapsedChange: (collapsed: boolean) => void
}

const sections: NavSection[] = [
  {
    label: 'Dashboard',
    icon: '📊',
    view: 'dashboard',
  },
  {
    label: 'Templates',
    icon: '📋',
    view: 'templates',
  },
  {
    label: 'Configuration',
    icon: '⚙️',
    view: 'config',
  },
  {
    label: 'Notifications',
    icon: '🔔',
    view: 'notifications',
  },
  {
    label: 'Batch Jobs',
    icon: '⚡',
    view: 'batch',
  },
  {
    label: 'Health',
    icon: '❤️',
    view: 'health',
  },
  {
    label: 'Settings',
    icon: '🔧',
    view: 'settings',
  },
]

export default function Navigation({
  currentView,
  onViewChange,
  collapsed,
  onCollapsedChange,
}: NavigationProps) {
  return (
    <nav className="nav-sidebar" data-testid="nav-sidebar" aria-label="Main navigation">
      <button
        className="nav-toggle"
        onClick={() => onCollapsedChange(!collapsed)}
        aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}
        data-testid="nav-toggle"
      >
        ☰
      </button>

      <ul className="nav-list">
        {sections.map((section) => (
          <li key={section.view}>
            <button
              className={`nav-item ${currentView === section.view ? 'active' : ''}`}
              onClick={() => onViewChange(section.view)}
              data-testid={`nav-${section.view}`}
              title={collapsed ? section.label : undefined}
              aria-current={currentView === section.view ? 'page' : undefined}
            >
              <span className="nav-icon">{section.icon}</span>
              {!collapsed && <span className="nav-label">{section.label}</span>}
            </button>
          </li>
        ))}
      </ul>

      <style jsx>{`
        .nav-sidebar {
          display: flex;
          flex-direction: column;
          background: var(--surface-2);
          border-right: 1px solid var(--border);
          height: 100vh;
          overflow-y: auto;
          transition: width 0.3s ease;
          width: ${collapsed ? '60px' : '250px'};
          padding: 0;
          margin: 0;
        }

        .nav-toggle {
          padding: 1rem;
          background: var(--surface-3);
          border: none;
          border-bottom: 1px solid var(--border);
          cursor: pointer;
          color: var(--text);
          font-size: 1.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }

        .nav-toggle:hover {
          background: var(--surface-4);
        }

        .nav-list {
          list-style: none;
          padding: 0.5rem;
          margin: 0;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          width: 100%;
          padding: 0.75rem 1rem;
          background: transparent;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          color: var(--text-muted);
          font-size: 0.875rem;
          transition: all 0.2s;
          text-align: left;
        }

        .nav-item:hover {
          background: var(--surface-3);
          color: var(--text);
        }

        .nav-item.active {
          background: var(--accent);
          color: white;
        }

        .nav-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 1.5rem;
          font-size: 1.25rem;
        }

        .nav-label {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        @media (max-width: 768px) {
          .nav-sidebar {
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            z-index: 1000;
            box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
          }

          .nav-sidebar:not([data-collapsed='true']) {
            width: 200px;
          }
        }

        @media (max-width: 375px) {
          .nav-sidebar {
            width: 60px;
          }

          .nav-item {
            padding: 0.5rem;
            justify-content: center;
          }

          .nav-icon {
            font-size: 1rem;
          }
        }
      `}</style>
    </nav>
  )
}
