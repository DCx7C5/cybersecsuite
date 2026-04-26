import { useEffect, useState } from 'react'
import Card from './Card'
import Badge from './Badge'

interface ContextAwareness {
  worker_id: string
  session_id: number
  architecture?: {
    current_layer?: string
    current_component?: string
    recent_components?: string[]
  }
  scope?: {
    scope_level?: string
    session_id?: number
    project_id?: number
  }
  hot_patterns?: string[]
  hot_endpoints?: string[]
  recent_errors?: number
}

interface ContextAwareBriefingProps {
  workerId?: string
  sessionId?: number
}

/**
 * ContextAwareBriefing displays worker context awareness information.
 * 
 * Shows:
 * - Current architecture layer and component
 * - Execution scope (session, project, investigation)
 * - Hot patterns and recently used endpoints
 * - Recent error tracking
 */
export function ContextAwareBriefing({
  workerId,
  sessionId,
}: ContextAwareBriefingProps) {
  const [context, setContext] = useState<ContextAwareness | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!workerId || !sessionId) {
      setLoading(false)
      return
    }

    const fetchContext = async () => {
      try {
        const params = new URLSearchParams({
          worker_id: workerId,
          session_id: sessionId.toString(),
        })
        const response = await fetch(`/api/v1/workers/context?${params}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()
        setContext(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch context')
      } finally {
        setLoading(false)
      }
    }

    fetchContext()
    const interval = setInterval(fetchContext, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [workerId, sessionId])

  if (!workerId || !sessionId) {
    return null
  }

  if (loading) {
    return (
      <Card>
        <div style={{ fontSize: '13px', opacity: 0.7 }}>Loading context...</div>
      </Card>
    )
  }

  if (error || !context) {
    return (
      <Card>
        <div style={{ fontSize: '13px', color: 'var(--red)' }}>
          {error || 'No context available'}
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <div style={{ marginBottom: '12px' }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>
          Context Awareness
        </h4>
      </div>

      {/* Architecture Context */}
      {context.architecture && (
        <div style={{ marginBottom: '12px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>
            <strong>Architecture</strong>
          </div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {context.architecture.current_layer && (
              <Badge variant="info">
                {`Layer: ${context.architecture.current_layer}`}
              </Badge>
            )}
            {context.architecture.current_component && (
              <Badge variant="info">
                {context.architecture.current_component}
              </Badge>
            )}
          </div>
          {context.architecture.recent_components && context.architecture.recent_components.length > 0 && (
            <div style={{ fontSize: '11px', opacity: 0.6, marginTop: '6px' }}>
              Recent: {context.architecture.recent_components.join(' → ')}
            </div>
          )}
        </div>
      )}

      {/* Scope Context */}
      {context.scope && (
        <div style={{ marginBottom: '12px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>
            <strong>Scope</strong>
          </div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {context.scope.scope_level && (
              <Badge variant="ok">
                {`Level: ${context.scope.scope_level}`}
              </Badge>
            )}
            {context.scope.session_id && (
              <Badge variant="ok">
                {`Session: ${context.scope.session_id}`}
              </Badge>
            )}
            {context.scope.project_id && (
              <Badge variant="ok">
                {`Project: ${context.scope.project_id}`}
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* Hot Patterns & Endpoints */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {/* Hot Patterns */}
        <div>
          <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '6px', fontWeight: 'bold' }}>
            Hot Patterns
          </div>
          {context.hot_patterns && context.hot_patterns.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {context.hot_patterns.map((pattern, idx) => (
                <div
                  key={idx}
                  style={{
                    fontSize: '11px',
                    padding: '4px 6px',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '4px',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                  }}
                >
                  {pattern}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '11px', opacity: 0.5 }}>No patterns yet</div>
          )}
        </div>

        {/* Hot Endpoints */}
        <div>
          <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '6px', fontWeight: 'bold' }}>
            Hot Endpoints
          </div>
          {context.hot_endpoints && context.hot_endpoints.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {context.hot_endpoints.map((endpoint, idx) => (
                <div
                  key={idx}
                  style={{
                    fontSize: '11px',
                    padding: '4px 6px',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderRadius: '4px',
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                  title={endpoint}
                >
                  {endpoint}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '11px', opacity: 0.5 }}>No endpoints yet</div>
          )}
        </div>
      </div>

      {/* Recent Errors */}
      {context.recent_errors !== undefined && context.recent_errors > 0 && (
        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--border)' }}>
          <Badge variant="warn">
            {`${context.recent_errors} recent errors`}
          </Badge>
        </div>
      )}
    </Card>
  )
}
