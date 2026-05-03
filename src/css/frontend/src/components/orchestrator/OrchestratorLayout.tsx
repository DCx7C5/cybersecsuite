import { useState, type ReactNode } from 'react'
import Navigation from './Navigation'
import StatusOverview from './StatusOverview'

interface OrchestratorLayoutProps {
  children?: ReactNode
  defaultView?: 'dashboard' | 'templates' | 'config' | 'notifications' | 'batch' | 'health' | 'settings'
}

export default function OrchestratorLayout({
  children,
  defaultView = 'dashboard',
}: OrchestratorLayoutProps) {
  const [currentView, setCurrentView] = useState(defaultView)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  return (
    <div className="orchestrator-layout" data-testid="orchestrator-layout">
      <Navigation 
        currentView={currentView}
        onViewChange={(view) => setCurrentView(view as typeof defaultView)}
        collapsed={sidebarCollapsed}
        onCollapsedChange={(collapsed) => setSidebarCollapsed(collapsed)}
      />
      
      <main className="orchestrator-main" data-testid="orchestrator-main">
        <div className="orchestrator-header">
          <StatusOverview isPaused={isPaused} />
          <div className="quick-actions" data-testid="quick-actions">
            <button 
              className="btn btn-secondary"
              onClick={() => setIsPaused(!isPaused)}
              aria-label={isPaused ? 'Resume orchestrator' : 'Pause orchestrator'}
              data-testid={isPaused ? 'resume-btn' : 'pause-btn'}
            >
              {isPaused ? 'Resume' : 'Pause'}
            </button>
            <button 
              className="btn btn-danger"
              aria-label="Cancel orchestrator"
              data-testid="cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>

        <div className="orchestrator-content" data-testid="orchestrator-content">
          {children}
        </div>
      </main>

      <style>{`
        .orchestrator-layout {
          display: grid;
          grid-template-columns: ${sidebarCollapsed ? '60px' : '250px'} 1fr;
          height: 100vh;
          background: var(--bg-primary);
          gap: 0;
        }

        .orchestrator-main {
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .orchestrator-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid var(--border);
          background: var(--surface-1);
          gap: 1rem;
          flex-wrap: wrap;
        }

        .quick-actions {
          display: flex;
          gap: 0.5rem;
        }

        .orchestrator-content {
          flex: 1;
          overflow: auto;
          padding: 1.5rem;
        }

        .btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border);
          background: var(--surface-2);
          color: var(--text);
          cursor: pointer;
          border-radius: 4px;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .btn:hover {
          background: var(--surface-3);
        }

        .btn-secondary {
          background: var(--accent);
          color: white;
          border-color: var(--accent);
        }

        .btn-secondary:hover {
          background: var(--accent-dark);
        }

        .btn-danger {
          background: var(--red);
          color: white;
          border-color: var(--red);
        }

        .btn-danger:hover {
          background: var(--red-dark);
        }

        @media (max-width: 768px) {
          .orchestrator-layout {
            grid-template-columns: 1fr;
          }

          .orchestrator-header {
            padding: 1rem;
            gap: 0.75rem;
          }

          .orchestrator-content {
            padding: 1rem;
          }
        }

        @media (max-width: 375px) {
          .orchestrator-header {
            padding: 0.75rem;
            flex-direction: column;
            align-items: stretch;
          }

          .quick-actions {
            width: 100%;
          }

          .quick-actions button {
            flex: 1;
          }
        }
      `}</style>
    </div>
  )
}
