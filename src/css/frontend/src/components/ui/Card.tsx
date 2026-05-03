import type { ReactNode, CSSProperties } from 'react'

export default function Card({
  title,
  children,
  actions,
  style,
}: {
  title?: string
  children: ReactNode
  actions?: ReactNode
  style?: CSSProperties
}) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      ...style,
    }}>
      {(title || actions) && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--surface-2)',
        }}>
          {title && <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>{title}</span>}
          {actions && <div style={{ display: 'flex', gap: '8px' }}>{actions}</div>}
        </div>
      )}
      <div style={{ padding: '16px' }}>
        {children}
      </div>
    </div>
  )
}
