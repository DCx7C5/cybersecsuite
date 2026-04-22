import { Component, type ReactNode } from 'react'
import type { ErrorInfo } from 'react'

interface Props {
  children: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  fallback?: (error: Error, retry: () => void) => ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
  errorCount: number
}

/**
 * ErrorBoundary catches React component errors and displays graceful error UI.
 * 
 * Features:
 * - Error capture and display
 * - Error stack trace in development
 * - Retry mechanism
 * - Custom error callback
 * - Custom fallback UI
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, errorCount: 0 }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo })
    this.props.onError?.(error, errorInfo)
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  retry = () => {
    this.setState((state) => ({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
      errorCount: state.errorCount + 1,
    }))
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback && this.state.error) {
        return this.props.fallback(this.state.error, this.retry)
      }

      // Default error UI
      const isDev = process.env.NODE_ENV === 'development'
      return (
        <div
          style={{
            padding: '24px',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '2px solid var(--red)',
            borderRadius: 'var(--radius)',
            color: 'var(--red)',
          }}
        >
          <div style={{ marginBottom: '16px' }}>
            <strong style={{ fontSize: '16px' }}>⚠️ Something went wrong</strong>
          </div>

          <div style={{ marginBottom: '12px', fontSize: '14px', lineHeight: '1.5' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </div>

          {isDev && this.state.errorInfo && (
            <details
              style={{
                marginBottom: '12px',
                padding: '8px',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
              }}
            >
              <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                Error Details (Dev Only)
              </summary>
              <pre
                style={{
                  marginTop: '8px',
                  fontSize: '11px',
                  overflow: 'auto',
                  maxHeight: '300px',
                }}
              >
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}

          <button
            onClick={this.retry}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--red)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius)',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            Try Again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
