import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'var(--red)', background: 'var(--surface)', borderRadius: 'var(--radius)' }}>
          <strong>Error:</strong> {this.state.error?.message ?? 'Unknown error'}
        </div>
      )
    }
    return this.props.children
  }
}
