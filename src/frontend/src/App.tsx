import React, { Suspense, useEffect } from 'react'
import * as RQ from '@tanstack/react-query'
import { queryClient } from './libs/queryClient'
import { useUIStore } from './store/uiStore'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'
import StatusBar from './components/layout/StatusBar'
import Spinner from './components/ui/Spinner'
import { ErrorBoundary } from './components/shared/ErrorBoundary'

const panels: Record<string, React.LazyExoticComponent<() => React.ReactElement>> = {
  'chat':                   React.lazy(() => import('./features/agents/ChatPanel')),
  'health':                 React.lazy(() => import('./features/platform/HealthPanel')),
  'usage':                  React.lazy(() => import('./features/platform/UsagePanel')),
  'telemetry':              React.lazy(() => import('./features/platform/TelemetryPanel')),
  'providers-hub':          React.lazy(() => import('./features/platform/ProvidersPanel')),
  'routing':                React.lazy(() => import('./features/proxy/RoutingPanel')),
  'qol-controls':           React.lazy(() => import('./features/proxy/QolPanel')),
  'agent-factory':          React.lazy(() => import('./features/agents/AgentFactoryPanel')),
  'agent-crafter':          React.lazy(() => import('./features/agents/AgentCrafterPanel')),
  'team-builder':           React.lazy(() => import('./features/agents/TeamBuilderPanel')),
  'agent-query':            React.lazy(() => import('./features/agents/AgentQueryPanel')),
  'workflows':              React.lazy(() => import('./features/agents/WorkflowsPanel')),
  'flowgraph':              React.lazy(() => import('./features/agents/FlowgraphPanel')),
  'prompts':                React.lazy(() => import('./features/agents/PromptsPanel')),
  'sdk-lab':                React.lazy(() => import('./features/agents/SdkLabPanel')),
  'marketplace':            React.lazy(() => import('./features/agents/MarketplacePanel')),
  'marketplace-factory':    React.lazy(() => import('./features/agents/MarketplaceFactoryPanel')),
  'cases':                  React.lazy(() => import('./features/operations/CasesPanel')),
  'tasks':                  React.lazy(() => import('./features/operations/TasksPanel')),
  'pocs':                   React.lazy(() => import('./features/operations/PocsPanel')),
  'a2a':                    React.lazy(() => import('./features/operations/A2aPanel')),
  'investigations':         React.lazy(() => import('./features/forensics/InvestigationsPanel')),
  'findings':               React.lazy(() => import('./features/forensics/FindingsPanel')),
  'iocs':                   React.lazy(() => import('./features/forensics/IoCsPanel')),
  'yara':                   React.lazy(() => import('./features/forensics/YaraPanel')),
  'intel':                  React.lazy(() => import('./features/forensics/IntelPanel')),
  'audit':                  React.lazy(() => import('./features/forensics/AuditPanel')),
  'compliance':             React.lazy(() => import('./features/forensics/CompliancePanel')),
  'opensearch':             React.lazy(() => import('./features/data/OpenSearchPanel')),
  'explorer':               React.lazy(() => import('./features/data/ExplorerPanel')),
  'templates':              React.lazy(() => import('./features/data/TemplatesPanel')),
  'settings':               React.lazy(() => import('./features/settings/SettingsPanel')),
  'settings-cybersecsuite': React.lazy(() => import('./features/settings/SettingsCybersecSuitePanel')),
}

export default function App() {
  const { theme, sidebarCollapsed, activeTab } = useUIStore()

  useEffect(() => {
    document.body.className = `theme-${theme}${sidebarCollapsed ? ' sidebar-collapsed' : ''}`
  }, [theme, sidebarCollapsed])

  const Panel = panels[activeTab]

  return (
    <RQ.QueryClientProvider client={queryClient}>
      <div id="shell" style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />
        <div
          id="main-content"
          style={{
            marginLeft: sidebarCollapsed ? 0 : 'var(--sidebar-w)',
            flex: 1,
            transition: 'margin-left 0.25s ease',
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
          }}
        >
          <Topbar />
          <main style={{ flex: 1, padding: '16px', overflow: 'auto' }}>
            <ErrorBoundary>
              <Suspense fallback={
                <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                  <Spinner />
                </div>
              }>
                {Panel ? <Panel /> : <div style={{ color: 'var(--text-muted)' }}>Tab not found: {activeTab}</div>}
              </Suspense>
            </ErrorBoundary>
          </main>
          <StatusBar />
        </div>
      </div>
    </RQ.QueryClientProvider>
  )
}
